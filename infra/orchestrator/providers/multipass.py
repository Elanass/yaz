"""
Multipass provider implementation as fallback for VM orchestration.
"""
import json
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
from .base import BaseProvider, Instance, InstanceStatus
from ..utils import (
    run, run_json, retry_with_backoff, wait_for_condition,
    parse_memory, validate_instance_name, get_backup_path,
    ProviderError, InstanceNotFoundError
)

logger = logging.getLogger(__name__)

class MultipassProvider(BaseProvider):
    """Multipass VM provider as fallback."""
    
    def __init__(self):
        self.bridge_name = "mpbr0"
        
    def is_available(self) -> bool:
        """Check if Multipass is available."""
        try:
            run("multipass version", timeout=10)
            return True
        except:
            return False
    
    def ensure_host(self) -> bool:
        """Ensure Multipass host is properly configured."""
        try:
            logger.info("Checking Multipass installation...")
            
            # Check if Multipass is installed
            if not self.is_available():
                logger.info("Installing Multipass...")
                run("sudo snap install multipass", timeout=300)
            
            # Set up networking if needed
            self._ensure_networking()
            
            logger.info("Multipass host ready")
            return True
            
        except Exception as e:
            logger.error(f"Failed to ensure Multipass host: {e}")
            raise ProviderError(f"Host setup failed: {e}")
    
    def _ensure_networking(self):
        """Ensure Multipass networking is configured."""
        try:
            # Try to set bridge if available
            run("multipass set local.bridged-network=true", check=False)
        except:
            logger.debug("Bridge networking not available, using default")
    
    def _get_instance_info(self, name: str) -> Dict[str, Any]:
        """Get instance information from Multipass."""
        try:
            result = run_json(f"multipass info {name} --format json")
            return result.get("info", {}).get(name, {})
        except:
            raise InstanceNotFoundError(f"Instance not found: {name}")
    
    def _parse_status(self, status_str: str) -> InstanceStatus:
        """Parse Multipass status to InstanceStatus."""
        status_map = {
            "Running": InstanceStatus.RUNNING,
            "Stopped": InstanceStatus.STOPPED,
            "Starting": InstanceStatus.STARTING,
            "Stopping": InstanceStatus.STOPPING,
            "Suspended": InstanceStatus.FROZEN,
        }
        return status_map.get(status_str, InstanceStatus.UNKNOWN)
    
    def create_instance(self, name: str, config: Dict[str, Any]) -> Instance:
        """Create a new Multipass instance."""
        logger.info(f"Creating Multipass instance: {name}")
        
        if not validate_instance_name(name):
            raise ProviderError(f"Invalid instance name: {name}")
        
        # Build multipass launch command
        cmd_parts = ["multipass", "launch"]
        
        # Image
        image = config.get("image", "22.04")
        cmd_parts.append(image)
        
        # Name
        cmd_parts.extend(["--name", name])
        
        # Resources
        if "memory" in config:
            cmd_parts.extend(["--memory", config["memory"]])
        if "cpus" in config:
            cmd_parts.extend(["--cpus", str(config["cpus"])])
        if "disk" in config:
            cmd_parts.extend(["--disk", config["disk"]])
        
        # Cloud-init
        cloud_init = config.get("cloud_init")
        if cloud_init:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                if isinstance(cloud_init, str):
                    f.write(cloud_init)
                else:
                    import yaml
                    yaml.dump(cloud_init, f)
                cloud_init_file = f.name
            cmd_parts.extend(["--cloud-init", cloud_init_file])
        
        # Networking
        network = config.get("network", {})
        if network.get("bridged"):
            cmd_parts.append("--bridged")
        
        try:
            run(" ".join(cmd_parts), timeout=300)
            
            # Wait for instance to be ready
            def check_running():
                info = self._get_instance_info(name)
                return info.get("state") == "Running"
            
            if not wait_for_condition(check_running, timeout=180):
                raise ProviderError(f"Instance {name} failed to start within timeout")
            
            # Set metadata using exec
            metadata = config.get("metadata", {})
            for key, value in metadata.items():
                try:
                    self.exec_command(name, f"echo '{value}' | sudo tee /etc/yaz-{key}")
                except:
                    logger.debug(f"Failed to set metadata {key}")
            
            return self.get_instance(name)
            
        except Exception as e:
            logger.error(f"Failed to create instance {name}: {e}")
            # Cleanup on failure
            try:
                self.destroy_instance(name)
            except:
                pass
            raise ProviderError(f"Instance creation failed: {e}")
        finally:
            # Cleanup cloud-init file
            if cloud_init and 'cloud_init_file' in locals():
                Path(cloud_init_file).unlink(missing_ok=True)
    
    def start_instance(self, name: str) -> bool:
        """Start a Multipass instance."""
        logger.info(f"Starting instance: {name}")
        try:
            run(f"multipass start {name}", timeout=60)
            
            # Wait for running state
            def check_running():
                info = self._get_instance_info(name)
                return info.get("state") == "Running"
            
            return wait_for_condition(check_running, timeout=120)
            
        except Exception as e:
            logger.error(f"Failed to start instance {name}: {e}")
            return False
    
    def stop_instance(self, name: str) -> bool:
        """Stop a Multipass instance."""
        logger.info(f"Stopping instance: {name}")
        try:
            run(f"multipass stop {name}", timeout=60)
            
            # Wait for stopped state
            def check_stopped():
                info = self._get_instance_info(name)
                return info.get("state") == "Stopped"
            
            return wait_for_condition(check_stopped, timeout=120)
            
        except Exception as e:
            logger.error(f"Failed to stop instance {name}: {e}")
            return False
    
    def destroy_instance(self, name: str) -> bool:
        """Destroy a Multipass instance."""
        logger.info(f"Destroying instance: {name}")
        try:
            run(f"multipass delete {name}", timeout=30)
            run(f"multipass purge", timeout=30)
            return True
        except Exception as e:
            logger.error(f"Failed to destroy instance {name}: {e}")
            return False
    
    def list_instances(self) -> List[Instance]:
        """List all Multipass instances."""
        try:
            result = run_json("multipass list --format json")
            instances = []
            
            for instance_data in result.get("list", []):
                name = instance_data.get("name")
                status = self._parse_status(instance_data.get("state", ""))
                
                # Get IP addresses
                ip_address = None
                ipv4_addresses = instance_data.get("ipv4", [])
                if ipv4_addresses:
                    ip_address = ipv4_addresses[0]
                
                instances.append(Instance(
                    name=name,
                    status=status,
                    ip_address=ip_address,
                    metadata={}
                ))
            
            return instances
            
        except Exception as e:
            logger.error(f"Failed to list instances: {e}")
            return []
    
    def get_instance(self, name: str) -> Optional[Instance]:
        """Get Multipass instance details."""
        try:
            info = self._get_instance_info(name)
            
            status = self._parse_status(info.get("state", ""))
            
            # Get IP address
            ip_address = None
            ipv4_addresses = info.get("ipv4", [])
            if ipv4_addresses:
                ip_address = ipv4_addresses[0]
            
            # Parse memory and CPU usage
            memory_usage = 0
            cpu_usage = 0.0
            
            return Instance(
                name=name,
                status=status,
                ip_address=ip_address,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                metadata={}
            )
            
        except InstanceNotFoundError:
            return None
        except Exception as e:
            logger.error(f"Failed to get instance {name}: {e}")
            return None
    
    def exec_command(self, name: str, command: str) -> str:
        """Execute command in Multipass instance."""
        try:
            result = run(f"multipass exec {name} -- {command}", timeout=60)
            return result.stdout
        except Exception as e:
            logger.error(f"Failed to exec in {name}: {e}")
            raise ProviderError(f"Command execution failed: {e}")
    
    def push_file(self, name: str, local_path: Path, remote_path: str) -> bool:
        """Push file to Multipass instance."""
        try:
            run(f"multipass transfer {local_path} {name}:{remote_path}", timeout=60)
            return True
        except Exception as e:
            logger.error(f"Failed to push file to {name}: {e}")
            return False
    
    def pull_file(self, name: str, remote_path: str, local_path: Path) -> bool:
        """Pull file from Multipass instance."""
        try:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            run(f"multipass transfer {name}:{remote_path} {local_path}", timeout=60)
            return True
        except Exception as e:
            logger.error(f"Failed to pull file from {name}: {e}")
            return False
    
    def snapshot_instance(self, name: str, snapshot_name: str) -> bool:
        """Create instance snapshot (Multipass doesn't support snapshots)."""
        logger.warning("Multipass doesn't support snapshots, using backup instead")
        return self.export_instance(name, get_backup_path() / f"{name}-{snapshot_name}.backup")
    
    def export_instance(self, name: str, export_path: Path) -> bool:
        """Export instance to file (basic backup)."""
        try:
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create a basic backup by saving instance info
            info = self._get_instance_info(name)
            with open(export_path, 'w') as f:
                json.dump(info, f, indent=2)
            
            logger.info(f"Instance {name} info exported to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export instance {name}: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on Multipass."""
        health = {
            "provider": "multipass",
            "available": False,
            "version": None,
            "instances": 0,
            "errors": []
        }
        
        try:
            # Check availability
            health["available"] = self.is_available()
            
            if health["available"]:
                # Get version
                result = run("multipass version")
                health["version"] = result.stdout.strip().split('\n')[0]
                
                # Count instances
                instances = self.list_instances()
                health["instances"] = len(instances)
            
        except Exception as e:
            health["errors"].append(str(e))
        
        return health
