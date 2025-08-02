"""
Decision Engines Feature Module
Centralized decision support functionality
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
import asyncio

from pydantic import BaseModel, Field

from core.config.settings import get_feature_config
from core.models.base import BaseEntity, ConfidenceLevel
from core.models.medical import DecisionStatus
from core.services.base import BaseService, CacheService
from core.services.logger import get_logger
from core.utils.helpers import HashUtils
from feature.decisions.adci_engine import ADCIEngine
from feature.protocols.flot_analyzer import FLOTAnalyzer
from feature.analysis.impact_metrics import ImpactMetricsCalculator

logger = get_logger(__name__)


# Schemas
class DecisionRequest(BaseModel):
    """Decision analysis request"""
    
    engine_type: str = Field(..., description="Decision engine type")
    patient_data: Dict[str, Any] = Field(..., description="Patient clinical data")
    tumor_data: Dict[str, Any] = Field(..., description="Tumor characteristics")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    
    class Config:
        schema_extra = {
            "example": {
                "engine_type": "adci",
                "patient_data": {
                    "age": 65,
                    "performance_status": 1,
                    "comorbidities": ["hypertension"]
                },
                "tumor_data": {
                    "stage": "T3N1M0",
                    "location": "antrum",
                    "histology": "adenocarcinoma"
                }
            }
        }


class DecisionResponse(BaseModel):
    """Decision analysis response"""
    
    decision_id: str
    engine_type: str
    status: DecisionStatus
    recommendation: Dict[str, Any]
    confidence_score: float
    confidence_level: ConfidenceLevel
    reasoning: List[str]
    evidence: List[Dict[str, Any]]
    warnings: List[str]
    created_at: datetime
    processing_time_ms: Optional[int] = None
    
    class Config:
        schema_extra = {
            "example": {
                "decision_id": "decision_123",
                "engine_type": "adci",
                "status": "completed",
                "recommendation": {
                    "treatment": "neoadjuvant_chemotherapy",
                    "urgency": "standard"
                },
                "confidence_score": 0.85,
                "confidence_level": "high",
                "reasoning": [
                    "T3N1M0 staging suggests locally advanced disease",
                    "Patient age and performance status support treatment"
                ],
                "evidence": [
                    {"source": "clinical_guidelines", "strength": "strong"}
                ],
                "warnings": [],
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


# Models
class Decision(BaseEntity):
    """Decision analysis record"""
    
    engine_type: str
    patient_data: Dict[str, Any]
    tumor_data: Dict[str, Any]
    context: Dict[str, Any]
    status: DecisionStatus = DecisionStatus.PENDING
    recommendation: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    confidence_level: Optional[ConfidenceLevel] = None
    reasoning: List[str] = []
    evidence: List[Dict[str, Any]] = []
    warnings: List[str] = []
    processing_time_ms: Optional[int] = None
    user_id: Optional[str] = None


# Base Decision Engine
class BaseDecisionEngine(ABC):
    """Base class for all decision engines"""
    
    def __init__(self, engine_type: str):
        self.engine_type = engine_type
        self.config = get_feature_config("decisions")
    
    @abstractmethod
    async def analyze(
        self,
        patient_data: Dict[str, Any],
        tumor_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform decision analysis"""
        pass
    
    def validate_input(self, patient_data: Dict[str, Any], tumor_data: Dict[str, Any]) -> List[str]:
        """Validate input data"""
        errors = []
        
        # Basic validation
        if not patient_data.get("age"):
            errors.append("Patient age is required")
        
        if not tumor_data.get("stage"):
            errors.append("Tumor stage is required")
        
        return errors
    
    def calculate_confidence(self, factors: Dict[str, float]) -> float:
        """Calculate overall confidence score"""
        if not factors:
            return 0.5
        
        weights = {
            "data_completeness": 0.3,
            "evidence_strength": 0.4,
            "guideline_support": 0.3
        }
        
        weighted_sum = sum(
            factors.get(factor, 0.5) * weight
            for factor, weight in weights.items()
        )
        
        return min(max(weighted_sum, 0.0), 1.0)


# Import the dedicated ADCI Engine implementation
from feature.decisions.adci_engine import ADCIEngine


# Create a wrapper for backward compatibility
class ADCIEngineWrapper(BaseDecisionEngine):
    """Wrapper for the Adaptive Decision Confidence Index Engine"""
    
    def __init__(self):
        super().__init__("adci")
        self.engine = ADCIEngine()
        logger.info("ADCI Engine Wrapper initialized")
        
    async def analyze(
        self,
        patient_data: Dict[str, Any],
        tumor_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Delegate to the dedicated ADCI engine"""
        # Combine patient and tumor data to match the expected format
        combined_data = {
            **patient_data,
            "tumor_data": tumor_data,
            "patient_id": patient_data.get("id", "unknown")
        }
        
        # Call the dedicated ADCI engine
        result = await self.engine.predict(
            patient_data=combined_data,
            collaboration_context=context
        )
        
        # Format the response to match the expected interface
        return {
            "recommendation": result.get("adci", {}).get("recommendation", ""),
            "confidence_score": result.get("confidence_metrics", {}).get("overall_confidence", 0.5),
            "confidence_level": ConfidenceLevel.from_score(
                result.get("confidence_metrics", {}).get("overall_confidence", 0.5)
            ),
            "reasoning": result.get("adci", {}).get("critical_factors", []),
            "evidence": result.get("flot_analysis", {}).get("evidence_quality", []),
            "warnings": [],
            "confidence_factors": result.get("confidence_metrics", {})
        }
    
# Gastrectomy Engine
class GastrectomyEngine(BaseDecisionEngine):
    """Gastrectomy surgical decision engine"""
    
    def __init__(self):
        super().__init__("gastrectomy")
    
    async def analyze(
        self,
        patient_data: Dict[str, Any],
        tumor_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform gastrectomy analysis"""
        
        await asyncio.sleep(0.1)
        
        # Extract parameters
        age = patient_data.get("age", 65)
        bmi = patient_data.get("bmi", 24)
        asa_score = patient_data.get("asa_score", 2)
        
        tumor_location = tumor_data.get("location", "antrum")
        tumor_size = tumor_data.get("size_cm", 3.0)
        
        # Determine surgical approach
        approach = self._determine_surgical_approach(tumor_location, tumor_size, age, bmi)
        reasoning = self._generate_surgical_reasoning(approach, tumor_location, tumor_size, age)
        
        confidence_score = self._calculate_surgical_confidence(age, bmi, asa_score, tumor_size)
        
        return {
            "recommendation": approach,
            "confidence_score": confidence_score,
            "confidence_level": ConfidenceLevel.from_score(confidence_score),
            "reasoning": reasoning,
            "evidence": [
                {
                    "source": "Surgical Guidelines",
                    "strength": "strong",
                    "description": "International guidelines for gastric surgery"
                }
            ]
        }
    
    def _determine_surgical_approach(self, location: str, size: float, age: int, bmi: float) -> Dict[str, Any]:
        """Determine surgical approach"""
        
        # Location-based decisions
        if location in ["antrum", "pylorus"]:
            if size < 4.0 and age < 75:
                return {
                    "procedure": "distal_gastrectomy",
                    "approach": "laparoscopic",
                    "lymphadenectomy": "D2"
                }
            else:
                return {
                    "procedure": "distal_gastrectomy", 
                    "approach": "open",
                    "lymphadenectomy": "D2"
                }
        
        elif location in ["fundus", "cardia"]:
            return {
                "procedure": "proximal_gastrectomy",
                "approach": "laparoscopic" if age < 70 and bmi < 30 else "open",
                "lymphadenectomy": "D2"
            }
        
        else:  # body or multiple locations
            return {
                "procedure": "total_gastrectomy",
                "approach": "open",
                "lymphadenectomy": "D2"
            }
    
    def _generate_surgical_reasoning(self, approach: Dict[str, Any], location: str, size: float, age: int) -> List[str]:
        """Generate surgical reasoning"""
        
        reasoning = []
        
        reasoning.append(f"Tumor location ({location}) determines surgical approach")
        reasoning.append(f"Tumor size {size}cm considered in procedure selection")
        
        if approach["approach"] == "laparoscopic":
            reasoning.append("Laparoscopic approach preferred for reduced morbidity")
        else:
            reasoning.append("Open approach recommended for optimal exposure")
        
        reasoning.append(f"D2 lymphadenectomy recommended for oncological adequacy")
        
        return reasoning
    
    def _calculate_surgical_confidence(self, age: int, bmi: float, asa_score: int, tumor_size: float) -> float:
        """Calculate confidence in surgical recommendation"""
        
        confidence = 0.8  # Base confidence
        
        # Age factor
        if age < 65:
            confidence += 0.1
        elif age > 75:
            confidence -= 0.2
        
        # BMI factor
        if bmi > 30:
            confidence -= 0.1
        
        # ASA score factor
        if asa_score > 3:
            confidence -= 0.2
        
        # Tumor size factor
        if tumor_size > 5.0:
            confidence -= 0.1
        
        return min(max(confidence, 0.0), 1.0)
    
    def validate_input(self, patient_data: Dict[str, Any], tumor_data: Dict[str, Any]) -> List[str]:
        """Validate input data for gastrectomy analysis"""
        errors = []
        
        # Basic validation for gastrectomy
        if not patient_data.get("age"):
            errors.append("Patient age is required")
        
        if not tumor_data.get("location"):
            errors.append("Tumor location is required for surgical planning")
        
        return errors


# Create a wrapper for the FLOT analyzer
class FLOTEngineWrapper(BaseDecisionEngine):
    """Wrapper for the FLOT Protocol Analyzer"""
    
    def __init__(self):
        super().__init__("flot")
        self.analyzer = FLOTAnalyzer()
        logger.info("FLOT Engine Wrapper initialized")
        
    async def analyze(
        self,
        patient_data: Dict[str, Any],
        tumor_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Delegate to the dedicated FLOT analyzer"""
        # Combine patient and tumor data to match the expected format
        combined_data = {
            **patient_data,
            "tumor_data": tumor_data,
            "patient_id": patient_data.get("id", "unknown")
        }
        
        # Call the dedicated FLOT analyzer
        result = await self.analyzer.analyze_gastric_surgery_case(
            patient_data=combined_data,
            research_context=context
        )
        
        # Format the response to match the expected interface
        return {
            "recommendation": result.get("treatment_plan", {}).get("recommendation", ""),
            "confidence_score": result.get("treatment_plan", {}).get("confidence", 0.5),
            "confidence_level": ConfidenceLevel.from_score(
                result.get("treatment_plan", {}).get("confidence", 0.5)
            ),
            "reasoning": result.get("treatment_plan", {}).get("factors", []),
            "evidence": result.get("evidence_quality", []),
            "warnings": result.get("risk_assessment", {}).get("warnings", []),
            "surgical_impact": result.get("surgical_impact", {})
        }
    


# Decision Service
class DecisionService(BaseService):
    """Main decision service coordinating all engines"""
    
    def __init__(self):
        super().__init__()
        self.cache = CacheService()
        self.config = get_feature_config("decisions")
        
        # Initialize specialized engines using wrappers for consistent interface
        self.engines = {
            "adci": ADCIEngineWrapper(),
            "gastrectomy": GastrectomyEngine(),
            "flot": FLOTEngineWrapper()
        }
        
        # Create impact calculator for metrics
        self.impact_calculator = ImpactMetricsCalculator()
        
        self.decisions: Dict[str, Decision] = {}  # In-memory store for MVP
        
        logger.info("Decision Service initialized with specialized engines")
    
    async def create_decision(
        self,
        request: DecisionRequest,
        user_id: Optional[str] = None
    ) -> DecisionResponse:
        """Create new decision analysis"""
        
        start_time = asyncio.get_event_loop().time()
        
        # Create decision record
        decision = Decision(
            engine_type=request.engine_type,
            patient_data=request.patient_data,
            tumor_data=request.tumor_data,
            context=request.context or {},
            user_id=user_id
        )
        
        decision_id = str(decision.id)
        self.decisions[decision_id] = decision
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(request)
            cached_result = await self.cache.get(cache_key)
            
            if cached_result:
                self.logger.info(f"Cache hit for decision {decision_id}")
                result = cached_result
            else:
                # Get engine
                engine = self.engines.get(request.engine_type)
                if not engine:
                    raise ValueError(f"Unknown engine type: {request.engine_type}")
                
                # Validate input
                errors = engine.validate_input(request.patient_data, request.tumor_data)
                if errors:
                    decision.status = DecisionStatus.FAILED
                    decision.warnings = errors
                    raise ValueError(f"Validation errors: {'; '.join(errors)}")
                
                # Process decision
                decision.status = DecisionStatus.PROCESSING
                
                result = await engine.analyze(
                    request.patient_data,
                    request.tumor_data,
                    request.context
                )
                
                # Cache result
                await self.cache.set(cache_key, result, ttl=self.config.get("cache_ttl", 3600))
            
            # Update decision record
            decision.status = DecisionStatus.COMPLETED
            decision.recommendation = result["recommendation"]
            decision.confidence_score = result["confidence_score"]
            decision.confidence_level = result["confidence_level"]
            decision.reasoning = result["reasoning"]
            decision.evidence = result.get("evidence", [])
            decision.processing_time_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
            
            self.logger.info(f"Decision {decision_id} completed in {decision.processing_time_ms}ms")
            
            return self._create_response(decision)
            
        except Exception as e:
            decision.status = DecisionStatus.FAILED
            decision.warnings = [str(e)]
            self.logger.error(f"Decision {decision_id} failed: {e}")
            raise
    
    async def get_decision(self, decision_id: str) -> Optional[DecisionResponse]:
        """Get decision by ID"""
        
        decision = self.decisions.get(decision_id)
        if not decision:
            return None
        
        return self._create_response(decision)
    
    async def list_decisions(
        self,
        user_id: Optional[str] = None,
        engine_type: Optional[str] = None,
        status: Optional[DecisionStatus] = None
    ) -> List[DecisionResponse]:
        """List decisions with filters"""
        
        decisions = list(self.decisions.values())
        
        # Apply filters
        if user_id:
            decisions = [d for d in decisions if d.user_id == user_id]
        
        if engine_type:
            decisions = [d for d in decisions if d.engine_type == engine_type]
        
        if status:
            decisions = [d for d in decisions if d.status == status]
        
        # Sort by creation time (newest first)
        decisions.sort(key=lambda d: d.created_at, reverse=True)
        
        return [self._create_response(d) for d in decisions]
    
    async def register_decision_job(
        self,
        job_id: str,
        request: DecisionRequest,
        user_id: str
    ) -> DecisionResponse:
        """
        Register a decision job and return a pending decision
        
        Args:
            job_id: Job ID of the submitted analysis
            request: Decision request data
            user_id: ID of the user making the request
            
        Returns:
            Decision response with job details
        """
        # Generate decision ID
        decision_id = HashUtils.generate_uuid()
        
        # Create decision record with pending status
        decision = {
            "decision_id": decision_id,
            "engine_type": request.engine_type,
            "status": DecisionStatus.PENDING,
            "user_id": user_id,
            "patient_hash": HashUtils.hash_dict(request.patient_data),
            "request_data": request.dict(),
            "job_id": job_id,
            "created_at": datetime.now().isoformat(),
            "confidence_level": None,
            "recommendation": None,
            "factors": [],
            "alternatives": []
        }
        
        # Store in database
        await self.db.save_decision(decision)
        
        # Return decision response
        return DecisionResponse(**decision)
    
    async def update_decision_from_job(
        self,
        decision_id: str,
        job_id: str
    ) -> None:
        """
        Update a decision record when a job completes
        
        Args:
            decision_id: ID of the decision to update
            job_id: Job ID to retrieve results for
        """
        # Import job manager functions
        from feature.analysis.job_manager import get_job_status, wait_for_job_result
        
        # Wait for job to complete (max 30 minutes)
        result = await wait_for_job_result(job_id, timeout=1800)
        
        if not result:
            # Update decision as failed if timeout
            await self.db.update_decision(
                decision_id,
                {
                    "status": DecisionStatus.FAILED,
                    "updated_at": datetime.now().isoformat(),
                    "error": "Job timed out after 30 minutes"
                }
            )
            return
            
        # Update decision with results
        await self.create_decision_from_result(
            result=result,
            decision_id=decision_id
        )
    
    async def create_decision_from_result(
        self,
        result: Dict[str, Any],
        decision_id: Optional[str] = None,
        request: Optional[DecisionRequest] = None,
        user_id: Optional[str] = None
    ) -> DecisionResponse:
        """
        Create or update a decision from a job result
        
        Args:
            result: Job result data
            decision_id: Optional ID of existing decision to update
            request: Optional request data if creating new decision
            user_id: Optional user ID if creating new decision
            
        Returns:
            Updated decision response
        """
        if not decision_id and not (request and user_id):
            raise ValueError("Either decision_id or both request and user_id must be provided")
            
        # Create new decision if needed
        if not decision_id:
            decision_id = HashUtils.generate_uuid()
            decision = {
                "decision_id": decision_id,
                "engine_type": request.engine_type,
                "status": DecisionStatus.COMPLETED,
                "user_id": user_id,
                "patient_hash": HashUtils.hash_dict(request.patient_data),
                "request_data": request.dict(),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        else:
            # Get existing decision
            decision = await self.db.get_decision(decision_id)
            decision["status"] = DecisionStatus.COMPLETED
            decision["updated_at"] = datetime.now().isoformat()
        
        # Process result data
        if "confidence_metrics" in result:
            decision["confidence_level"] = self._map_confidence_level(
                result["confidence_metrics"].get("overall_confidence", 0)
            )
        
        if "recommendation" in result:
            decision["recommendation"] = result["recommendation"]
            
        if "factors" in result:
            decision["factors"] = result["factors"]
            
        if "alternatives" in result:
            decision["alternatives"] = result["alternatives"]
            
        # Add additional result data
        decision["result_data"] = result
        
        # Save decision
        await self.db.save_decision(decision)
        
        # Return response
        return DecisionResponse(**decision)
    
    def _generate_cache_key(self, request: DecisionRequest) -> str:
        """Generate cache key for request"""
        
        key_data = {
            "engine_type": request.engine_type,
            "patient_data": request.patient_data,
            "tumor_data": request.tumor_data
        }
        
        return HashUtils.generate_cache_key(key_data)
    
    def _create_response(self, decision: Decision) -> DecisionResponse:
        """Create response from decision"""
        
        return DecisionResponse(
            decision_id=str(decision.id),
            engine_type=decision.engine_type,
            status=decision.status,
            recommendation=decision.recommendation or {},
            confidence_score=decision.confidence_score or 0.0,
            confidence_level=decision.confidence_level or ConfidenceLevel.VERY_LOW,
            reasoning=decision.reasoning,
            evidence=decision.evidence,
            warnings=decision.warnings,
            created_at=decision.created_at,
            processing_time_ms=decision.processing_time_ms
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on all decision engines"""
        health_status = {
            "status": "healthy",
            "engines": {}
        }
        
        try:
            # Check each engine
            for engine_name, engine in self.engines.items():
                try:
                    # Basic validation test
                    if hasattr(engine, "validate_input"):
                        errors = engine.validate_input({"age": 65}, {"stage": "T2N0M0"})
                        health_status["engines"][engine_name] = {
                            "status": "healthy" if not errors else "degraded",
                            "errors": errors
                        }
                    else:
                        health_status["engines"][engine_name] = {"status": "unknown"}
                except Exception as e:
                    health_status["engines"][engine_name] = {
                        "status": "error",
                        "message": str(e)
                    }
                    health_status["status"] = "degraded"
            
            # Check cache
            try:
                await self.cache.ping()
                health_status["cache"] = {"status": "connected"}
            except Exception as e:
                health_status["cache"] = {"status": "error", "message": str(e)}
                health_status["status"] = "degraded"
                
            return health_status
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
