"""
Event Correlation Engine for Gastric ADCI Platform.

This service analyzes clinical events to identify patterns, detect anomalies,
and correlate related events for improved clinical decision support and
security monitoring.

Features:
- Temporal pattern analysis of clinical events
- Protocol compliance monitoring
- Anomaly detection for unexpected clinical patterns
- Security incident correlation
- Clinical workflow optimization recommendations
"""

import datetime
from typing import Dict, Any, List, Optional, Tuple, Set, Union
import asyncio
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN

from core.services.logger import get_logger
from services.event_logger.service import EventLog, EventCategory, EventSeverity, event_logger

# Configure logger
logger = get_logger(__name__)

class CorrelationRule(BaseModel):
    """Definition of an event correlation rule."""
    id: str
    name: str
    description: str
    event_categories: List[str]
    timeframe_seconds: int
    condition: str  # Python expression to evaluate
    severity: str = EventSeverity.INFO
    clinical_domain: Optional[str] = None
    requires_action: bool = False
    alert_threshold: Optional[int] = None
    
    class Config:
        arbitrary_types_allowed = True

class CorrelatedEvent(BaseModel):
    """A group of correlated events with clinical context."""
    correlation_id: str
    rule_id: str
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    severity: str
    events: List[str]  # List of event IDs
    clinical_context: Dict[str, Any] = {}
    summary: str
    recommendation: Optional[str] = None
    requires_action: bool = False
    status: str = "NEW"  # NEW, ACKNOWLEDGED, RESOLVED, FALSE_POSITIVE
    assigned_to: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime.datetime: lambda v: v.isoformat()
        }


class EventCorrelationEngine:
    """Engine for correlating clinical and security events."""
    
    def __init__(self):
        self.rules: List[CorrelationRule] = []
        self.event_buffer: List[EventLog] = []
        self.buffer_max_size: int = 10000
        self.correlated_events: List[CorrelatedEvent] = []
        self.last_analysis: datetime.datetime = datetime.datetime.now()
        self.analysis_interval_seconds: int = 300  # 5 minutes
        
        # Load default rules
        self._load_default_rules()
    
    def _load_default_rules(self):
        """Load default correlation rules for clinical context."""
        self.rules = [
            CorrelationRule(
                id="protocol-deviation-cluster",
                name="Protocol Deviation Cluster",
                description="Multiple protocol deviations for the same patient within a short period",
                event_categories=[EventCategory.PROTOCOL_DEVIATION],
                timeframe_seconds=3600,  # 1 hour
                condition="len(events) >= 2 and len(set([e.context.patient_id for e in events])) == 1",
                severity=EventSeverity.WARNING,
                requires_action=True,
                alert_threshold=2
            ),
            CorrelationRule(
                id="failed-auth-attempts",
                name="Multiple Failed Authentication Attempts",
                description="Multiple failed authentication attempts for the same user",
                event_categories=[EventCategory.AUTHENTICATION],
                timeframe_seconds=300,  # 5 minutes
                condition="len([e for e in events if e.data.outcome == 'FAILURE']) >= 3",
                severity=EventSeverity.WARNING,
                requires_action=True,
                alert_threshold=3
            ),
            CorrelationRule(
                id="clinical-decision-sequence",
                name="Clinical Decision Sequence",
                description="Sequence of clinical decisions for the same patient",
                event_categories=[EventCategory.CLINICAL_DECISION],
                timeframe_seconds=7200,  # 2 hours
                condition="len(events) >= 2 and len(set([e.context.patient_id for e in events])) == 1",
                severity=EventSeverity.INFO,
                requires_action=False
            ),
            CorrelationRule(
                id="emergency-access-pattern",
                name="Emergency Access Pattern",
                description="Pattern of emergency access to patient records",
                event_categories=[EventCategory.DATA_ACCESS],
                timeframe_seconds=3600,  # 1 hour
                condition="len([e for e in events if e.context.is_emergency]) >= 2",
                severity=EventSeverity.WARNING,
                requires_action=True,
                alert_threshold=2
            ),
            CorrelationRule(
                id="abnormal-data-access",
                name="Abnormal Data Access Pattern",
                description="Unusual pattern of data access by a provider",
                event_categories=[EventCategory.DATA_ACCESS],
                timeframe_seconds=86400,  # 24 hours
                condition="len(set([e.context.patient_id for e in events])) >= 10",
                severity=EventSeverity.WARNING,
                requires_action=True,
                alert_threshold=10
            )
        ]
    
    def add_rule(self, rule: CorrelationRule):
        """Add a new correlation rule."""
        self.rules.append(rule)
        logger.info(f"Added correlation rule: {rule.id} - {rule.name}")
    
    def remove_rule(self, rule_id: str):
        """Remove a correlation rule by ID."""
        self.rules = [r for r in self.rules if r.id != rule_id]
        logger.info(f"Removed correlation rule: {rule_id}")
    
    async def process_event(self, event: EventLog):
        """
        Process a new event for correlation.
        
        This adds the event to the buffer and triggers analysis if needed.
        """
        # Add to buffer
        self.event_buffer.append(event)
        
        # Trim buffer if needed
        if len(self.event_buffer) > self.buffer_max_size:
            self.event_buffer = self.event_buffer[-self.buffer_max_size:]
        
        # Check if analysis is due
        now = datetime.datetime.now()
        if (now - self.last_analysis).total_seconds() >= self.analysis_interval_seconds:
            await self.analyze_events()
            self.last_analysis = now
    
    async def analyze_events(self):
        """
        Analyze buffered events using correlation rules and anomaly detection.
        """
        if not self.event_buffer:
            return
            
        logger.info(f"Analyzing {len(self.event_buffer)} events for correlation")
        
        # Apply correlation rules
        await self._apply_correlation_rules()
        
        # Perform anomaly detection
        await self._detect_anomalies()
        
        # Look for temporal patterns
        await self._analyze_temporal_patterns()
    
    async def _apply_correlation_rules(self):
        """Apply defined correlation rules to event buffer."""
        now = datetime.datetime.now()
        
        for rule in self.rules:
            # Filter events by category and timeframe
            rule_events = [
                e for e in self.event_buffer
                if e.category in rule.event_categories and
                (now - e.timestamp).total_seconds() <= rule.timeframe_seconds
            ]
            
            if not rule_events:
                continue
                
            # Evaluate rule condition
            try:
                # Create a safe local environment for eval
                local_vars = {"events": rule_events, "len": len, "set": set}
                if eval(rule.condition, {"__builtins__": {}}, local_vars):
                    # Rule condition matched
                    await self._create_correlated_event(rule, rule_events)
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.id}: {str(e)}")
    
    async def _create_correlated_event(self, rule: CorrelationRule, events: List[EventLog]):
        """Create a correlated event from matched events."""
        from uuid import uuid4
        
        # Extract clinical context
        clinical_context = self._extract_clinical_context(events)
        
        # Create summary
        if rule.id == "protocol-deviation-cluster":
            patient_id = events[0].context.patient_id
            protocol_id = events[0].context.protocol_id
            summary = f"Multiple protocol deviations ({len(events)}) for patient {patient_id} on protocol {protocol_id}"
            recommendation = "Review patient protocol compliance and consider protocol adjustment"
        elif rule.id == "failed-auth-attempts":
            user_attempts = {}
            for e in events:
                if e.data.outcome == "FAILURE":
                    user = e.data.metadata.get("username", "unknown")
                    user_attempts[user] = user_attempts.get(user, 0) + 1
            
            users = [u for u, c in user_attempts.items() if c >= 3]
            summary = f"Multiple failed authentication attempts for users: {', '.join(users)}"
            recommendation = "Check for potential security breach attempts"
        elif rule.id == "clinical-decision-sequence":
            patient_id = events[0].context.patient_id
            decision_types = set([e.data.metadata.get("decision_type", "unknown") for e in events])
            summary = f"Sequence of clinical decisions ({', '.join(decision_types)}) for patient {patient_id}"
            recommendation = "Review decision sequence for clinical consistency"
        elif rule.id == "emergency-access-pattern":
            providers = set([e.context.provider_id for e in events if e.context.is_emergency])
            summary = f"Pattern of emergency access by providers: {', '.join(providers)}"
            recommendation = "Verify emergency access justification"
        elif rule.id == "abnormal-data-access":
            provider_id = events[0].context.provider_id
            patient_count = len(set([e.context.patient_id for e in events]))
            summary = f"Provider {provider_id} accessed {patient_count} different patient records in a short period"
            recommendation = "Review access pattern for appropriate clinical context"
        else:
            summary = f"Correlated events based on rule: {rule.name}"
            recommendation = "Review correlated events for further analysis"
        
        # Create the correlated event
        correlated_event = CorrelatedEvent(
            correlation_id=str(uuid4()),
            rule_id=rule.id,
            severity=rule.severity,
            events=[e.id for e in events],
            clinical_context=clinical_context,
            summary=summary,
            recommendation=recommendation,
            requires_action=rule.requires_action
        )
        
        # Add to correlated events
        self.correlated_events.append(correlated_event)
        
        # Log the correlation
        await event_logger.log_event(
            category=EventCategory.SYSTEM,
            severity=rule.severity,
            source={
                "component": "event_correlation_engine",
                "service": "correlation"
            },
            context={
                "related_events": [e.id for e in events]
            },
            data={
                "action": "EVENT_CORRELATION",
                "outcome": "DETECTED",
                "metadata": {
                    "rule_id": rule.id,
                    "correlation_id": correlated_event.correlation_id
                }
            },
            message=f"Correlation detected: {summary}"
        )
        
        # If action is required, trigger alert
        if rule.requires_action:
            await self._trigger_alert(correlated_event)
    
    def _extract_clinical_context(self, events: List[EventLog]) -> Dict[str, Any]:
        """Extract relevant clinical context from correlated events."""
        context = {}
        
        # Extract patient IDs
        patient_ids = set([e.context.patient_id for e in events if e.context.patient_id])
        if patient_ids:
            context["patient_ids"] = list(patient_ids)
        
        # Extract provider IDs
        provider_ids = set([e.context.provider_id for e in events if e.context.provider_id])
        if provider_ids:
            context["provider_ids"] = list(provider_ids)
        
        # Extract protocol IDs
        protocol_ids = set([e.context.protocol_id for e in events if e.context.protocol_id])
        if protocol_ids:
            context["protocol_ids"] = list(protocol_ids)
        
        # Extract decision IDs
        decision_ids = set([e.context.decision_id for e in events if e.context.decision_id])
        if decision_ids:
            context["decision_ids"] = list(decision_ids)
        
        # Extract clinical domains
        clinical_domains = set([e.context.clinical_domain for e in events if e.context.clinical_domain])
        if clinical_domains:
            context["clinical_domains"] = list(clinical_domains)
        
        return context
    
    async def _detect_anomalies(self):
        """
        Detect anomalies in event patterns using machine learning.
        
        This uses Isolation Forest to identify outlier events based on
        their features and context.
        """
        if len(self.event_buffer) < 100:
            return  # Need more events for meaningful anomaly detection
            
        try:
            # Extract features for anomaly detection
            features = []
            events = []
            
            for event in self.event_buffer:
                # Skip if too old
                if (datetime.datetime.now() - event.timestamp).total_seconds() > 86400:
                    continue
                    
                # Create feature vector
                feature_dict = {
                    "category": event.category,
                    "severity": event.severity,
                    "component": event.source.component,
                    "hour_of_day": event.timestamp.hour,
                    "is_weekend": 1 if event.timestamp.weekday() >= 5 else 0,
                    "has_patient_id": 1 if event.context.patient_id else 0,
                    "has_provider_id": 1 if event.context.provider_id else 0,
                    "is_emergency": 1 if event.context.is_emergency else 0
                }
                
                # One-hot encode categorical features
                categories = {
                    f"category_{event.category}": 1,
                    f"severity_{event.severity}": 1,
                    f"component_{event.source.component}": 1
                }
                
                # Combine features
                feature_dict.update(categories)
                
                features.append(feature_dict)
                events.append(event)
            
            if not features:
                return
                
            # Convert to pandas DataFrame
            df = pd.DataFrame(features)
            
            # Fill missing values
            df = df.fillna(0)
            
            # Convert categorical columns to one-hot encoding
            for col in df.select_dtypes(include=['object']).columns:
                dummies = pd.get_dummies(df[col], prefix=col)
                df = pd.concat([df.drop(col, axis=1), dummies], axis=1)
            
            # Run Isolation Forest for anomaly detection
            model = IsolationForest(contamination=0.05, random_state=42)
            df['anomaly_score'] = model.fit_predict(df)
            
            # Identify anomalies (isolation forest returns -1 for anomalies)
            anomaly_indices = df.index[df['anomaly_score'] == -1].tolist()
            
            # Process anomalies
            if anomaly_indices:
                await self._process_anomalies([events[i] for i in anomaly_indices])
                
        except Exception as e:
            logger.error(f"Error in anomaly detection: {str(e)}")
    
    async def _process_anomalies(self, anomalous_events: List[EventLog]):
        """Process detected anomalies and create alerts if needed."""
        if not anomalous_events:
            return
            
        logger.info(f"Detected {len(anomalous_events)} anomalous events")
        
        # Group anomalies by context
        grouped_anomalies = {}
        
        for event in anomalous_events:
            # Create a context key
            if event.context.patient_id:
                context_key = f"patient_{event.context.patient_id}"
            elif event.context.provider_id:
                context_key = f"provider_{event.context.provider_id}"
            else:
                context_key = f"category_{event.category}"
                
            if context_key not in grouped_anomalies:
                grouped_anomalies[context_key] = []
                
            grouped_anomalies[context_key].append(event)
        
        # Create correlated events for each group
        for context_key, events in grouped_anomalies.items():
            if len(events) >= 2:  # Only create correlation for multiple events
                # Create a synthetic rule for this anomaly
                rule = CorrelationRule(
                    id=f"anomaly-{context_key}",
                    name="Anomalous Event Pattern",
                    description="Machine learning detected unusual event pattern",
                    event_categories=[e.category for e in events],
                    timeframe_seconds=86400,
                    condition="True",  # Already filtered
                    severity=EventSeverity.WARNING,
                    requires_action=True
                )
                
                await self._create_correlated_event(rule, events)
    
    async def _analyze_temporal_patterns(self):
        """
        Analyze temporal patterns in events to identify sequences.
        
        This looks for common sequences of events that might indicate
        clinical workflows or security patterns.
        """
        # This would implement temporal pattern mining algorithms
        # For now, we'll leave this as a stub for future implementation
        pass
    
    async def _trigger_alert(self, correlated_event: CorrelatedEvent):
        """Trigger an alert for a correlated event that requires action."""
        # This would connect to the alerting service
        # For now, we'll just log it
        logger.warning(
            f"ALERT: {correlated_event.summary} "
            f"[Severity: {correlated_event.severity}, ID: {correlated_event.correlation_id}]"
        )
    
    async def get_correlated_events(
        self,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
        severity: Optional[str] = None,
        requires_action: Optional[bool] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[CorrelatedEvent]:
        """
        Query correlated events with filtering and pagination.
        """
        filtered_events = self.correlated_events
        
        # Apply filters
        if start_time:
            filtered_events = [e for e in filtered_events if e.timestamp >= start_time]
            
        if end_time:
            filtered_events = [e for e in filtered_events if e.timestamp <= end_time]
            
        if severity:
            filtered_events = [e for e in filtered_events if e.severity == severity]
            
        if requires_action is not None:
            filtered_events = [e for e in filtered_events if e.requires_action == requires_action]
            
        if status:
            filtered_events = [e for e in filtered_events if e.status == status]
        
        # Sort by timestamp descending
        filtered_events.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply pagination
        paginated_events = filtered_events[offset:offset + limit]
        
        return paginated_events
    
    async def update_correlated_event_status(
        self,
        correlation_id: str,
        status: str,
        assigned_to: Optional[str] = None
    ) -> Optional[CorrelatedEvent]:
        """Update the status of a correlated event."""
        for event in self.correlated_events:
            if event.correlation_id == correlation_id:
                event.status = status
                if assigned_to:
                    event.assigned_to = assigned_to
                return event
                
        return None


# Create a singleton instance
correlation_engine = EventCorrelationEngine()

# Start background processing task
async def start_background_processing():
    """Start background processing of events."""
    while True:
        try:
            await correlation_engine.analyze_events()
        except Exception as e:
            logger.error(f"Error in event correlation background processing: {str(e)}")
            
        await asyncio.sleep(300)  # Run every 5 minutes
