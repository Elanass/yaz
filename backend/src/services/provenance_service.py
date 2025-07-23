"""
Provenance Service - Data traceability and lineage tracking for clinical decisions.
Implements comprehensive provenance tracking following W3C PROV standards.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

import ipfshttpclient
from cryptography.fernet import Fernet
from fastapi import HTTPException
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..db.models import User, Patient, DecisionResult, ClinicalProtocol, EvidenceRecord
from ..schemas.provenance import (
    ProvenanceRecord,
    ProvenanceActivity,
    ProvenanceEntity,
    ProvenanceAgent,
    ProvenanceCreate,
    ProvenanceQuery,
    ProvenanceTrail,
    LineageGraph,
    ImmutableSnapshot,
)

logger = logging.getLogger(__name__)


class ProvenanceService:
    """Service for tracking data provenance and lineage in clinical workflows."""

    def __init__(self):
        self.encryption_key = settings.encryption_key.encode()
        self.cipher = Fernet(self.encryption_key)
        
        # IPFS client for immutable storage
        try:
            self.ipfs = ipfshttpclient.connect(settings.ipfs_api_url)
        except Exception as e:
            logger.warning(f"IPFS not available: {e}")
            self.ipfs = None

    async def create_provenance_record(
        self,
        db: AsyncSession,
        user_id: UUID,
        provenance_data: ProvenanceCreate,
    ) -> ProvenanceRecord:
        """Create a new provenance record."""
        try:
            # Generate unique identifiers
            record_id = uuid4()
            
            # Create provenance entities
            entities = []
            for entity_data in provenance_data.entities:
                entity = ProvenanceEntity(
                    id=uuid4(),
                    record_id=record_id,
                    entity_type=entity_data.entity_type,
                    entity_id=entity_data.entity_id,
                    attributes=entity_data.attributes,
                    value_hash=self._compute_value_hash(entity_data.attributes),
                    location=entity_data.location,
                    created_at=datetime.utcnow(),
                )
                entities.append(entity)

            # Create provenance activities
            activities = []
            for activity_data in provenance_data.activities:
                activity = ProvenanceActivity(
                    id=uuid4(),
                    record_id=record_id,
                    activity_type=activity_data.activity_type,
                    used_entities=activity_data.used_entities,
                    generated_entities=activity_data.generated_entities,
                    started_at=activity_data.started_at or datetime.utcnow(),
                    ended_at=activity_data.ended_at,
                    attributes=activity_data.attributes,
                    location=activity_data.location,
                )
                activities.append(activity)

            # Create provenance agents
            agents = []
            for agent_data in provenance_data.agents:
                agent = ProvenanceAgent(
                    id=uuid4(),
                    record_id=record_id,
                    agent_type=agent_data.agent_type,
                    agent_id=agent_data.agent_id,
                    name=agent_data.name,
                    attributes=agent_data.attributes,
                    acted_on_behalf_of=agent_data.acted_on_behalf_of,
                )
                agents.append(agent)

            # Create main provenance record
            record = ProvenanceRecord(
                id=record_id,
                user_id=user_id,
                namespace=provenance_data.namespace,
                prefix=provenance_data.prefix,
                entities=entities,
                activities=activities,
                agents=agents,
                bundle_id=provenance_data.bundle_id,
                derived_from=provenance_data.derived_from,
                revision_of=provenance_data.revision_of,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            # Store in database
            # Note: This would require actual SQLAlchemy models for provenance
            # For now, we'll return the constructed record
            
            # Create immutable snapshot in IPFS
            if self.ipfs:
                snapshot = await self._create_immutable_snapshot(record)
                record.ipfs_hash = snapshot.ipfs_hash

            logger.info(f"Provenance record created: {record_id}")
            return record

        except Exception as e:
            logger.error(f"Failed to create provenance record: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to create provenance record"
            )

    async def track_decision_provenance(
        self,
        db: AsyncSession,
        decision_id: UUID,
        user_id: UUID,
        input_data: Dict[str, Any],
        model_info: Dict[str, Any],
        output_data: Dict[str, Any],
    ) -> ProvenanceRecord:
        """Track provenance for a clinical decision."""
        try:
            # Get decision result details
            result = await db.execute(
                select(DecisionResult).where(DecisionResult.id == decision_id)
            )
            decision = result.scalar_one_or_none()
            
            if not decision:
                raise HTTPException(status_code=404, detail="Decision not found")

            # Create entities for the decision process
            entities = [
                {
                    "entity_type": "patient_data",
                    "entity_id": str(decision.patient_id),
                    "attributes": input_data,
                    "location": f"patient/{decision.patient_id}",
                },
                {
                    "entity_type": "clinical_protocol",
                    "entity_id": str(decision.protocol_id) if decision.protocol_id else None,
                    "attributes": {"protocol_version": decision.protocol_version},
                    "location": f"protocol/{decision.protocol_id}",
                },
                {
                    "entity_type": "decision_result",
                    "entity_id": str(decision_id),
                    "attributes": output_data,
                    "location": f"decision/{decision_id}",
                },
                {
                    "entity_type": "ai_model",
                    "entity_id": model_info.get("model_id", "adci-model"),
                    "attributes": {
                        "model_version": model_info.get("version"),
                        "model_type": model_info.get("type", "ensemble"),
                        "training_date": model_info.get("training_date"),
                        "hyperparameters": model_info.get("hyperparameters"),
                    },
                    "location": f"model/{model_info.get('model_id')}",
                },
            ]

            # Create activity for the decision process
            activities = [
                {
                    "activity_type": "decision_generation",
                    "used_entities": [entities[0]["entity_id"], entities[1]["entity_id"], entities[3]["entity_id"]],
                    "generated_entities": [entities[2]["entity_id"]],
                    "started_at": decision.created_at,
                    "ended_at": decision.updated_at,
                    "attributes": {
                        "confidence_score": decision.confidence_score,
                        "recommendation": decision.recommendation,
                        "risk_factors": decision.risk_factors,
                        "contraindications": decision.contraindications,
                    },
                    "location": "adci-platform",
                }
            ]

            # Create agents involved in the decision
            agents = [
                {
                    "agent_type": "person",
                    "agent_id": str(user_id),
                    "name": "Clinical User",
                    "attributes": {"role": "clinician"},
                    "acted_on_behalf_of": None,
                },
                {
                    "agent_type": "software_agent",
                    "agent_id": "adci-decision-engine",
                    "name": "ADCI Decision Engine",
                    "attributes": {
                        "version": model_info.get("version"),
                        "organization": "ADCI Platform",
                    },
                    "acted_on_behalf_of": str(user_id),
                },
            ]

            # Create provenance record
            provenance_data = ProvenanceCreate(
                namespace="https://adci.platform/provenance/",
                prefix="adci",
                entities=entities,
                activities=activities,
                agents=agents,
                bundle_id=f"decision-{decision_id}",
            )

            record = await self.create_provenance_record(db, user_id, provenance_data)
            
            # Link provenance to decision
            decision.provenance_id = record.id
            await db.commit()

            return record

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to track decision provenance: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to track decision provenance"
            )

    async def query_provenance(
        self, db: AsyncSession, query: ProvenanceQuery
    ) -> List[ProvenanceRecord]:
        """Query provenance records based on criteria."""
        try:
            # Build query conditions
            conditions = []
            
            if query.entity_id:
                # Query would search for records containing the entity
                pass
            
            if query.activity_type:
                # Query would search for records with specific activity types
                pass
            
            if query.agent_id:
                # Query would search for records involving specific agents
                pass
            
            if query.time_range:
                # Query would search within time range
                pass

            # Execute query (placeholder implementation)
            # In reality, this would query the provenance database tables
            records = []
            
            return records

        except Exception as e:
            logger.error(f"Failed to query provenance: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to query provenance")

    async def get_lineage_graph(
        self, db: AsyncSession, entity_id: UUID, depth: int = 5
    ) -> LineageGraph:
        """Get data lineage graph for an entity."""
        try:
            # Build lineage graph by traversing provenance relationships
            nodes = []
            edges = []
            
            # Start with the target entity
            root_node = {
                "id": str(entity_id),
                "type": "entity",
                "label": f"Entity {entity_id}",
                "attributes": {},
            }
            nodes.append(root_node)
            
            # Traverse backward through provenance chain
            visited = set()
            queue = [(entity_id, 0)]
            
            while queue and depth > 0:
                current_id, current_depth = queue.pop(0)
                
                if current_id in visited or current_depth >= depth:
                    continue
                    
                visited.add(current_id)
                
                # Find provenance records for this entity
                # (placeholder - would query actual provenance tables)
                
                # Add related entities, activities, and agents to graph
                # This would be implemented based on actual provenance data structure
                
                depth -= 1

            graph = LineageGraph(
                nodes=nodes,
                edges=edges,
                metadata={
                    "root_entity": str(entity_id),
                    "depth": depth,
                    "generated_at": datetime.utcnow().isoformat(),
                },
            )

            return graph

        except Exception as e:
            logger.error(f"Failed to get lineage graph: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to get lineage graph")

    async def create_provenance_trail(
        self, db: AsyncSession, start_entity: UUID, end_entity: UUID
    ) -> ProvenanceTrail:
        """Create a provenance trail between two entities."""
        try:
            # Find path through provenance graph
            path = await self._find_provenance_path(db, start_entity, end_entity)
            
            trail = ProvenanceTrail(
                start_entity=start_entity,
                end_entity=end_entity,
                path=path,
                confidence_score=self._calculate_trail_confidence(path),
                metadata={
                    "path_length": len(path),
                    "generated_at": datetime.utcnow().isoformat(),
                },
            )

            return trail

        except Exception as e:
            logger.error(f"Failed to create provenance trail: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to create provenance trail"
            )

    async def _create_immutable_snapshot(
        self, record: ProvenanceRecord
    ) -> ImmutableSnapshot:
        """Create immutable snapshot in IPFS."""
        try:
            if not self.ipfs:
                raise HTTPException(status_code=503, detail="IPFS not available")

            # Serialize provenance record
            snapshot_data = {
                "id": str(record.id),
                "timestamp": record.created_at.isoformat(),
                "namespace": record.namespace,
                "entities": [entity.dict() for entity in record.entities],
                "activities": [activity.dict() for activity in record.activities],
                "agents": [agent.dict() for agent in record.agents],
                "metadata": {
                    "platform": "ADCI",
                    "version": "1.0.0",
                    "hash_algorithm": "SHA-256",
                },
            }

            # Add to IPFS
            result = self.ipfs.add_json(snapshot_data)
            ipfs_hash = result["Hash"]

            # Create snapshot record
            snapshot = ImmutableSnapshot(
                id=uuid4(),
                provenance_id=record.id,
                ipfs_hash=ipfs_hash,
                content_hash=self._compute_content_hash(snapshot_data),
                size_bytes=len(json.dumps(snapshot_data).encode()),
                created_at=datetime.utcnow(),
            )

            return snapshot

        except Exception as e:
            logger.error(f"Failed to create immutable snapshot: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to create immutable snapshot"
            )

    async def verify_immutable_snapshot(
        self, ipfs_hash: str
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Verify immutable snapshot integrity."""
        try:
            if not self.ipfs:
                return False, {"error": "IPFS not available"}

            # Retrieve from IPFS
            data = self.ipfs.get_json(ipfs_hash)
            
            # Verify content hash
            computed_hash = self._compute_content_hash(data)
            stored_hash = data.get("metadata", {}).get("content_hash")
            
            if computed_hash != stored_hash:
                return False, {"error": "Content hash mismatch"}

            # Verify timestamp is reasonable
            timestamp = datetime.fromisoformat(data["timestamp"])
            if timestamp > datetime.utcnow():
                return False, {"error": "Future timestamp"}

            return True, {"verified_at": datetime.utcnow().isoformat()}

        except Exception as e:
            logger.error(f"Failed to verify immutable snapshot: {str(e)}")
            return False, {"error": str(e)}

    async def _find_provenance_path(
        self, db: AsyncSession, start: UUID, end: UUID
    ) -> List[Dict[str, Any]]:
        """Find provenance path between two entities using graph traversal."""
        # Placeholder implementation
        # In reality, this would use graph algorithms to find paths
        # through the provenance graph stored in the database
        return []

    def _calculate_trail_confidence(self, path: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for a provenance trail."""
        if not path:
            return 0.0
        
        # Base confidence decreases with path length
        base_confidence = 1.0 / (1.0 + len(path) * 0.1)
        
        # Adjust based on activity types and agent reliability
        reliability_score = 1.0
        for step in path:
            if step.get("activity_type") == "manual_entry":
                reliability_score *= 0.9  # Manual entry less reliable
            elif step.get("activity_type") == "automated_calculation":
                reliability_score *= 0.95  # Automated more reliable
        
        return min(base_confidence * reliability_score, 1.0)

    def _compute_value_hash(self, value: Any) -> str:
        """Compute hash of a value for integrity checking."""
        import hashlib
        serialized = json.dumps(value, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode()).hexdigest()

    def _compute_content_hash(self, content: Dict[str, Any]) -> str:
        """Compute hash of content for integrity checking."""
        import hashlib
        # Remove metadata that might change
        content_copy = content.copy()
        content_copy.pop("metadata", None)
        serialized = json.dumps(content_copy, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode()).hexdigest()

    async def export_provenance_bundle(
        self, db: AsyncSession, bundle_id: str
    ) -> Dict[str, Any]:
        """Export a complete provenance bundle for sharing or archival."""
        try:
            # Query all records in the bundle
            # (placeholder - would query actual provenance tables)
            
            bundle = {
                "bundle_id": bundle_id,
                "exported_at": datetime.utcnow().isoformat(),
                "format": "PROV-JSON",
                "records": [],
                "metadata": {
                    "platform": "ADCI",
                    "version": "1.0.0",
                    "export_type": "complete",
                },
            }

            return bundle

        except Exception as e:
            logger.error(f"Failed to export provenance bundle: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to export provenance bundle"
            )

    async def import_provenance_bundle(
        self, db: AsyncSession, bundle_data: Dict[str, Any], user_id: UUID
    ) -> List[UUID]:
        """Import a provenance bundle from external source."""
        try:
            # Validate bundle format
            if bundle_data.get("format") != "PROV-JSON":
                raise HTTPException(
                    status_code=400, detail="Unsupported bundle format"
                )

            imported_records = []
            
            # Process each record in the bundle
            for record_data in bundle_data.get("records", []):
                # Convert to internal format and create record
                # (placeholder implementation)
                pass

            return imported_records

        except Exception as e:
            logger.error(f"Failed to import provenance bundle: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to import provenance bundle"
            )

    async def get_data_quality_metrics(
        self, db: AsyncSession, entity_id: UUID
    ) -> Dict[str, Any]:
        """Get data quality metrics based on provenance information."""
        try:
            metrics = {
                "completeness": 0.0,
                "accuracy": 0.0,
                "consistency": 0.0,
                "timeliness": 0.0,
                "lineage_depth": 0,
                "verification_count": 0,
                "last_updated": None,
                "quality_score": 0.0,
            }

            # Calculate metrics based on provenance data
            # (placeholder implementation)
            
            return metrics

        except Exception as e:
            logger.error(f"Failed to get data quality metrics: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to get data quality metrics"
            )
