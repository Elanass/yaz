"""
Incus provider implementation for container and VM orchestration.
"""
import json
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
from .base import BaseProvider, Instance, InstanceStatus
from ..utils import (
    run, run_json, retry_with_backoff, wait_for_condition,
    parse_memory, extract_ip_from_addresses, validate_instance_name,
    get_backup_path, ProviderError, InstanceNotFoundError
)

logger = logging.getLogger(__name__)

class IncusProvider(BaseProvider):
    """Incus container and VM provider."""
    
    def __init__(self, project: str = "yaz"):
        self.project = project
        self.storage_pool = "incus-pool"
        self.network = "incusbr0"
    
    def is_available(self) -> bool:
        """Check if Incus is available on the system."""
        try:
            run("incus version", timeout=10)
            return True
        except:
            return False
    
    def ensure_host(self) -> bool:
        """Ensure Incus host is properly configured."""
        try:
            logger.info("Checking Incus installation...")
            
            # Check if Incus is installed
            if not self.is_available():
                logger.info("Installing Incus...")
                run("sudo snap install incus --classic", timeout=300)
                run("sudo groupadd -f incus-admin")
                run(f"sudo usermod -aG incus-admin {run('whoami').stdout.strip()}")
                logger.warning("Please log out and back in for group changes to take effect")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure Incus host: {e}")
            return False
    
    def create_instance(self, name: str, config: Dict[str, Any]) -> Instance:
        """Create a new Incus instance (container or VM)."""
        logger.info(f"Creating Incus instance: {name}")
        
        if not validate_instance_name(name):
            raise ProviderError(f"Invalid instance name: {name}")
        
        instance_type = config.get("type", "container")
        image = config.get("image", "ubuntu:22.04")
        
        # Build launch command
        cmd_parts = ["incus", "launch", image, name]
        
        if instance_type == "vm":
            cmd_parts.append("--vm")
        
        # Resource limits
        if "memory" in config:
            cmd_parts.extend(["--config", f"limits.memory={config['memory']}"])
        if "cpus" in config:
            cmd_parts.extend(["--config", f"limits.cpu={config['cpus']}"])
        
        try:
            # Create instance
            run(" ".join(cmd_parts), timeout=120)
            
            # Start instance
            self.start_instance(name)
            
            return self.get_instance(name)
            
        except Exception as e:
            logger.error(f"Failed to create instance {name}: {e}")
            raise ProviderError(f"Instance creation failed: {e}")
    
    def start_instance(self, name: str) -> bool:
        """Start an instance."""
        try:
            run(f"incus start {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to start instance {name}: {e}")
            return False
    
    def stop_instance(self, name: str) -> bool:
        """Stop an instance."""
        try:
            run(f"incus stop {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop instance {name}: {e}")
            return False
    
    def destroy_instance(self, name: str) -> bool:
        """Destroy an instance."""
        try:
            run(f"incus delete {name} --force")
            return True
        except Exception as e:
            logger.error(f"Failed to destroy instance {name}: {e}")
            return False
    
    def get_instance(self, name: str) -> Optional[Instance]:
        """Get instance details."""
        try:
            result = run_json(f"incus list {name} --format json")
            if not result:
                return None
            
            instance_data = result[0]
            
            # Parse status
            status_map = {
                "Running": InstanceStatus.RUNNING,
                "Stopped": InstanceStatus.STOPPED,
                "Starting": InstanceStatus.STARTING,
                "Stopping": InstanceStatus.STOPPING,
                "Frozen": InstanceStatus.FROZEN
            }
            status = status_map.get(instance_data.get("status"), InstanceStatus.UNKNOWN)
            
            return Instance(
                name=name,
                status=status,
                ip_address=None,
                memory_usage=0,
                metadata={}
            )
            
        except Exception as e:
            logger.error(f"Failed to get instance {name}: {e}")
            return None
    
    def list_instances(self) -> List[Instance]:
        """List all instances in the project."""
        try:
            result = run_json("incus list --format json")
            instances = []
            
            for instance_data in result:
                name = instance_data.get("name")
                if name:
                    instance = self.get_instance(name)
                    if instance:
                        instances.append(instance)
            
            return instances
            
        except Exception as e:
            logger.error(f"Failed to list instances: {e}")
            return []
    
    def exec_command(self, name: str, command: str) -> str:
        """Execute command in instance."""
        try:
            result = run(f"incus exec {name} -- {command}", timeout=60)
            return result.stdout
        except Exception as e:
            logger.error(f"Failed to exec in {name}: {e}")
            raise ProviderError(f"Command execution failed: {e}")
    
    def push_file(self, name: str, local_path: Path, remote_path: str) -> bool:
        """Push file to instance."""
        try:
            run(f"incus file push {local_path} {name}/{remote_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to push file to {name}: {e}")
            return False
    
    def pull_file(self, name: str, remote_path: str, local_path: Path) -> bool:
        """Pull file from instance."""
        try:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            run(f"incus file pull {name}/{remote_path} {local_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to pull file from {name}: {e}")
            return False
    
    def snapshot_instance(self, name: str, snapshot_name: str) -> bool:
        """Create instance snapshot."""
        try:
            run(f"incus snapshot {name} {snapshot_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to snapshot {name}: {e}")
            return False
    
    def export_instance(self, name: str, export_path: Path) -> bool:
        """Export instance to file."""
        try:
            export_path.parent.mkdir(parents=True, exist_ok=True)
            run(f"incus export {name} {export_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export {name}: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on Incus provider."""
        health = {
            "provider": "incus",
            "available": False,
            "version": None,
            "instances": 0
        }
        
        try:
            # Check Incus version
            version_result = run("incus version", timeout=10)
            health["version"] = version_result.stdout.strip()
            health["available"] = True
            
            # Count instances
            instances = self.list_instances()
            health["instances"] = len(instances)
        
        except Exception as e:
            health["errors"] = [str(e)]
        
        return health
