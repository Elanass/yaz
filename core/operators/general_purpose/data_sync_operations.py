"""
Data Sync Operations Operator
Handles data synchronization, replication, and consistency across systems
"""

from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
from core.services.logger import get_logger

logger = get_logger(__name__)


class SyncStatus(Enum):
    """Data sync status types"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"


class ConflictResolution(Enum):
    """Conflict resolution strategies"""
    MANUAL = "manual"
    LATEST_WINS = "latest_wins"
    SOURCE_WINS = "source_wins"
    MERGE = "merge"


class DataSyncOperationsOperator:
    """Data synchronization operations manager"""
    
    def __init__(self):
        """Initialize data sync operations operator"""
        self.sync_jobs = {}
        self.sync_mappings = {}
        self.conflict_queue = {}
        self.sync_history = {}
        self.data_checksums = {}
        logger.info("Data sync operations operator initialized")
    
    def create_sync_mapping(self, mapping_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create data synchronization mapping between systems"""
        from .core_operations import CoreOperationsOperator
        core_ops = CoreOperationsOperator()
        
        mapping_id = core_ops.generate_operation_id("SYNCMAP")
        
        sync_mapping = {
            "mapping_id": mapping_id,
            "name": mapping_config["name"],
            "source_system": mapping_config["source_system"],
            "target_system": mapping_config["target_system"],
            "data_type": mapping_config["data_type"],
            "field_mappings": mapping_config.get("field_mappings", {}),
            "sync_frequency": mapping_config.get("sync_frequency", "manual"),  # manual, real_time, hourly, daily
            "conflict_resolution": mapping_config.get("conflict_resolution", ConflictResolution.MANUAL.value),
            "filters": mapping_config.get("filters", {}),
            "transformations": mapping_config.get("transformations", []),
            "active": True,
            "bidirectional": mapping_config.get("bidirectional", False),
            "created_at": datetime.now().isoformat(),
            "last_sync": None,
            "sync_count": 0
        }
        
        self.sync_mappings[mapping_id] = sync_mapping
        logger.info(f"Created sync mapping: {mapping_config['name']} ({mapping_id})")
        return sync_mapping
    
    def initiate_sync(self, mapping_id: str, sync_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Initiate data synchronization"""
        from .core_operations import CoreOperationsOperator
        core_ops = CoreOperationsOperator()
        
        if mapping_id not in self.sync_mappings:
            raise ValueError(f"Sync mapping {mapping_id} not found")
        
        mapping = self.sync_mappings[mapping_id]
        
        if not mapping["active"]:
            return {"success": False, "error": "Sync mapping is inactive"}
        
        job_id = core_ops.generate_operation_id("SYNCJOB")
        
        sync_job = {
            "job_id": job_id,
            "mapping_id": mapping_id,
            "status": SyncStatus.PENDING.value,
            "initiated_at": datetime.now().isoformat(),
            "initiated_by": sync_options.get("user_id") if sync_options else "system",
            "sync_options": sync_options or {},
            "progress": {
                "total_records": 0,
                "processed_records": 0,
                "successful_records": 0,
                "failed_records": 0,
                "conflicts": 0
            },
            "start_time": None,
            "end_time": None,
            "error_details": None
        }
        
        self.sync_jobs[job_id] = sync_job
        
        # Start sync execution
        result = self._execute_sync_job(job_id)
        
        # Log the operation
        core_ops.log_operation("sync_initiated", {
            "data": {
                "job_id": job_id,
                "mapping_id": mapping_id,
                "success": result.get("success", False)
            }
        })
        
        logger.info(f"Initiated sync job: {job_id} for mapping {mapping_id}")
        return result
    
    def _execute_sync_job(self, job_id: str) -> Dict[str, Any]:
        """Execute synchronization job"""
        sync_job = self.sync_jobs[job_id]
        mapping = self.sync_mappings[sync_job["mapping_id"]]
        
        sync_job["status"] = SyncStatus.IN_PROGRESS.value
        sync_job["start_time"] = datetime.now().isoformat()
        
        try:
            # Get source data
            source_data = self._get_source_data(mapping)
            sync_job["progress"]["total_records"] = len(source_data)
            
            # Process each record
            for record in source_data:
                try:
                    result = self._sync_record(mapping, record)
                    
                    sync_job["progress"]["processed_records"] += 1
                    
                    if result["success"]:
                        sync_job["progress"]["successful_records"] += 1
                    else:
                        sync_job["progress"]["failed_records"] += 1
                        
                        if result.get("conflict"):
                            sync_job["progress"]["conflicts"] += 1
                            self._handle_conflict(mapping, record, result["conflict_details"])
                
                except Exception as e:
                    sync_job["progress"]["failed_records"] += 1
                    logger.error(f"Failed to sync record in job {job_id}: {e}")
            
            # Update mapping statistics
            mapping["last_sync"] = datetime.now().isoformat()
            mapping["sync_count"] += 1
            
            sync_job["status"] = SyncStatus.COMPLETED.value
            sync_job["end_time"] = datetime.now().isoformat()
            
            logger.info(f"Completed sync job: {job_id}")
            return {"success": True, "job_id": job_id, "progress": sync_job["progress"]}
            
        except Exception as e:
            sync_job["status"] = SyncStatus.FAILED.value
            sync_job["end_time"] = datetime.now().isoformat()
            sync_job["error_details"] = str(e)
            
            logger.error(f"Sync job failed: {job_id} - {e}")
            return {"success": False, "job_id": job_id, "error": str(e)}
    
    def _get_source_data(self, mapping: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get data from source system (mock implementation)"""
        # In a real implementation, this would connect to the actual source system
        # and retrieve data based on the mapping configuration
        
        mock_data = [
            {"id": "1", "name": "Patient A", "updated_at": "2024-01-01T10:00:00Z"},
            {"id": "2", "name": "Patient B", "updated_at": "2024-01-01T11:00:00Z"},
            {"id": "3", "name": "Patient C", "updated_at": "2024-01-01T12:00:00Z"}
        ]
        
        return mock_data
    
    def _sync_record(self, mapping: Dict[str, Any], record: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronize individual record"""
        try:
            # Apply field mappings
            mapped_record = self._apply_field_mappings(mapping["field_mappings"], record)
            
            # Apply transformations
            transformed_record = self._apply_transformations(mapping["transformations"], mapped_record)
            
            # Check for conflicts
            conflict_check = self._check_for_conflicts(mapping, transformed_record)
            
            if conflict_check["has_conflict"]:
                if mapping["conflict_resolution"] == ConflictResolution.MANUAL.value:
                    return {
                        "success": False,
                        "conflict": True,
                        "conflict_details": conflict_check["details"]
                    }
                else:
                    # Auto-resolve conflict
                    resolved_record = self._resolve_conflict(
                        mapping["conflict_resolution"],
                        transformed_record,
                        conflict_check["existing_record"]
                    )
                    transformed_record = resolved_record
            
            # Write to target system
            write_result = self._write_to_target(mapping["target_system"], transformed_record)
            
            # Update checksum for future conflict detection
            self._update_record_checksum(mapping, transformed_record)
            
            return {"success": True, "record_id": transformed_record.get("id")}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _apply_field_mappings(self, field_mappings: Dict[str, str], record: Dict[str, Any]) -> Dict[str, Any]:
        """Apply field mappings to transform record structure"""
        mapped_record = {}
        
        for target_field, source_field in field_mappings.items():
            if source_field in record:
                mapped_record[target_field] = record[source_field]
        
        # Copy unmapped fields
        for field, value in record.items():
            if field not in field_mappings.values() and field not in mapped_record:
                mapped_record[field] = value
        
        return mapped_record
    
    def _apply_transformations(self, transformations: List[Dict[str, Any]], record: Dict[str, Any]) -> Dict[str, Any]:
        """Apply data transformations to record"""
        transformed_record = record.copy()
        
        for transformation in transformations:
            transform_type = transformation.get("type")
            field = transformation.get("field")
            
            if transform_type == "uppercase" and field in transformed_record:
                transformed_record[field] = str(transformed_record[field]).upper()
            elif transform_type == "lowercase" and field in transformed_record:
                transformed_record[field] = str(transformed_record[field]).lower()
            elif transform_type == "date_format" and field in transformed_record:
                # Implement date formatting transformation
                pass
        
        return transformed_record
    
    def _check_for_conflicts(self, mapping: Dict[str, Any], record: Dict[str, Any]) -> Dict[str, Any]:
        """Check for data conflicts"""
        record_id = record.get("id")
        if not record_id:
            return {"has_conflict": False}
        
        # Calculate current record checksum
        current_checksum = self._calculate_record_checksum(record)
        
        # Get stored checksum
        checksum_key = f"{mapping['mapping_id']}:{record_id}"
        stored_checksum = self.data_checksums.get(checksum_key)
        
        if stored_checksum and stored_checksum != current_checksum:
            return {
                "has_conflict": True,
                "details": {
                    "record_id": record_id,
                    "current_checksum": current_checksum,
                    "stored_checksum": stored_checksum,
                    "conflict_type": "checksum_mismatch"
                },
                "existing_record": self._get_existing_record(mapping["target_system"], record_id)
            }
        
        return {"has_conflict": False}
    
    def _resolve_conflict(self, resolution_strategy: str, new_record: Dict[str, Any], 
                         existing_record: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve data conflict based on strategy"""
        if resolution_strategy == ConflictResolution.LATEST_WINS.value:
            new_timestamp = new_record.get("updated_at", "")
            existing_timestamp = existing_record.get("updated_at", "")
            
            if new_timestamp > existing_timestamp:
                return new_record
            else:
                return existing_record
        
        elif resolution_strategy == ConflictResolution.SOURCE_WINS.value:
            return new_record
        
        elif resolution_strategy == ConflictResolution.MERGE.value:
            # Simple merge strategy - new record takes precedence for non-null values
            merged_record = existing_record.copy()
            for key, value in new_record.items():
                if value is not None:
                    merged_record[key] = value
            return merged_record
        
        return new_record
    
    def _handle_conflict(self, mapping: Dict[str, Any], record: Dict[str, Any], 
                        conflict_details: Dict[str, Any]) -> None:
        """Handle unresolved conflicts"""
        from .core_operations import CoreOperationsOperator
        core_ops = CoreOperationsOperator()
        
        conflict_id = core_ops.generate_operation_id("CONFLICT")
        
        conflict = {
            "conflict_id": conflict_id,
            "mapping_id": mapping["mapping_id"],
            "record_id": record.get("id"),
            "conflict_type": conflict_details.get("conflict_type"),
            "source_record": record,
            "existing_record": conflict_details.get("existing_record"),
            "detected_at": datetime.now().isoformat(),
            "status": "unresolved",
            "resolution": None,
            "resolved_at": None,
            "resolved_by": None
        }
        
        self.conflict_queue[conflict_id] = conflict
        logger.warning(f"Conflict detected: {conflict_id} for record {record.get('id')}")
    
    def _write_to_target(self, target_system: str, record: Dict[str, Any]) -> Dict[str, Any]:
        """Write record to target system (mock implementation)"""
        # In a real implementation, this would write to the actual target system
        return {"success": True, "target_system": target_system, "record_id": record.get("id")}
    
    def _get_existing_record(self, target_system: str, record_id: str) -> Dict[str, Any]:
        """Get existing record from target system (mock implementation)"""
        # In a real implementation, this would retrieve from the actual target system
        return {"id": record_id, "name": "Existing Record", "updated_at": "2024-01-01T09:00:00Z"}
    
    def _calculate_record_checksum(self, record: Dict[str, Any]) -> str:
        """Calculate checksum for record"""
        record_string = json.dumps(record, sort_keys=True)
        return hashlib.md5(record_string.encode()).hexdigest()
    
    def _update_record_checksum(self, mapping: Dict[str, Any], record: Dict[str, Any]) -> None:
        """Update stored checksum for record"""
        record_id = record.get("id")
        if record_id:
            checksum_key = f"{mapping['mapping_id']}:{record_id}"
            self.data_checksums[checksum_key] = self._calculate_record_checksum(record)
    
    def resolve_conflict(self, conflict_id: str, resolution: Dict[str, Any], 
                        resolved_by: str) -> Dict[str, Any]:
        """Manually resolve a conflict"""
        if conflict_id not in self.conflict_queue:
            raise ValueError(f"Conflict {conflict_id} not found")
        
        conflict = self.conflict_queue[conflict_id]
        
        conflict["resolution"] = resolution
        conflict["resolved_at"] = datetime.now().isoformat()
        conflict["resolved_by"] = resolved_by
        conflict["status"] = "resolved"
        
        logger.info(f"Conflict resolved: {conflict_id} by {resolved_by}")
        return conflict
    
    def get_sync_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of sync job"""
        if job_id not in self.sync_jobs:
            raise ValueError(f"Sync job {job_id} not found")
        
        return self.sync_jobs[job_id]
    
    def get_pending_conflicts(self) -> List[Dict[str, Any]]:
        """Get list of pending conflicts"""
        return [
            conflict for conflict in self.conflict_queue.values()
            if conflict["status"] == "unresolved"
        ]
    
    def get_sync_statistics(self, mapping_id: Optional[str] = None) -> Dict[str, Any]:
        """Get synchronization statistics"""
        if mapping_id:
            if mapping_id not in self.sync_mappings:
                raise ValueError(f"Sync mapping {mapping_id} not found")
            
            mapping = self.sync_mappings[mapping_id]
            
            # Get jobs for this mapping
            mapping_jobs = [
                job for job in self.sync_jobs.values()
                if job["mapping_id"] == mapping_id
            ]
            
            total_jobs = len(mapping_jobs)
            successful_jobs = len([j for j in mapping_jobs if j["status"] == SyncStatus.COMPLETED.value])
            failed_jobs = len([j for j in mapping_jobs if j["status"] == SyncStatus.FAILED.value])
            
            total_records = sum(j.get("progress", {}).get("total_records", 0) for j in mapping_jobs)
            successful_records = sum(j.get("progress", {}).get("successful_records", 0) for j in mapping_jobs)
            
            return {
                "mapping_id": mapping_id,
                "mapping_name": mapping["name"],
                "total_jobs": total_jobs,
                "successful_jobs": successful_jobs,
                "failed_jobs": failed_jobs,
                "success_rate_percent": round((successful_jobs / total_jobs * 100) if total_jobs > 0 else 100, 2),
                "total_records_synced": total_records,
                "successful_records": successful_records,
                "last_sync": mapping.get("last_sync"),
                "generated_at": datetime.now().isoformat()
            }
        else:
            # Return overall statistics
            total_mappings = len(self.sync_mappings)
            active_mappings = len([m for m in self.sync_mappings.values() if m["active"]])
            total_jobs = len(self.sync_jobs)
            pending_conflicts = len(self.get_pending_conflicts())
            
            return {
                "total_mappings": total_mappings,
                "active_mappings": active_mappings,
                "total_sync_jobs": total_jobs,
                "pending_conflicts": pending_conflicts,
                "generated_at": datetime.now().isoformat()
            }
