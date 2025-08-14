"""
Utility functions for the orchestrator.
"""
import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


def run(
    cmd: str, check: bool = True, timeout: int = 30, **kwargs
) -> subprocess.CompletedProcess:
    """Execute shell command with proper error handling."""
    logger.debug(f"Running: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=check,
            **kwargs,
        )
        if result.stdout:
            logger.debug(f"stdout: {result.stdout.strip()}")
        if result.stderr and result.returncode != 0:
            logger.debug(f"stderr: {result.stderr.strip()}")
        return result
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out after {timeout}s: {cmd}")
        raise
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {cmd}\nstderr: {e.stderr}")
        raise


def run_json(cmd: str, **kwargs) -> Dict[str, Any]:
    """Run command and parse JSON output."""
    result = run(cmd, **kwargs)
    try:
        return json.loads(result.stdout) if result.stdout.strip() else {}
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from: {cmd}\nOutput: {result.stdout}")
        raise


def retry_with_backoff(
    func, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 30.0
):
    """Retry function with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = min(base_delay * (2**attempt), max_delay)
            logger.warning(
                f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s..."
            )
            time.sleep(delay)


def wait_for_condition(condition_func, timeout: int = 120, interval: int = 2) -> bool:
    """Wait for a condition to become true."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            if condition_func():
                return True
        except Exception as e:
            logger.debug(f"Condition check failed: {e}")
        time.sleep(interval)
    return False


def parse_memory(mem_str: str) -> int:
    """Parse memory string to bytes."""
    if not mem_str:
        return 0

    mem_str = mem_str.strip().upper()
    multipliers = {
        "B": 1,
        "K": 1024,
        "KB": 1024,
        "KIB": 1024,
        "M": 1024**2,
        "MB": 1024**2,
        "MIB": 1024**2,
        "G": 1024**3,
        "GB": 1024**3,
        "GIB": 1024**3,
        "T": 1024**4,
        "TB": 1024**4,
        "TIB": 1024**4,
    }

    for suffix, multiplier in multipliers.items():
        if mem_str.endswith(suffix):
            try:
                return int(float(mem_str[: -len(suffix)]) * multiplier)
            except ValueError:
                break

    # Default to treating as bytes
    try:
        return int(mem_str)
    except ValueError:
        raise ValueError(f"Invalid memory format: {mem_str}")


def format_memory(bytes_val: int) -> str:
    """Format bytes to human readable string."""
    for unit in ["B", "KiB", "MiB", "GiB", "TiB"]:
        if bytes_val < 1024:
            return f"{bytes_val:.1f}{unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f}PiB"


def ensure_dir(path: Path, mode: int = 0o755):
    """Ensure directory exists with proper permissions."""
    path.mkdir(parents=True, exist_ok=True, mode=mode)


def load_yaml_file(path: Path) -> Dict[str, Any]:
    """Load YAML file safely."""
    try:
        import yaml

        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        # Fallback to JSON if PyYAML not available
        logger.warning("PyYAML not available, attempting JSON parse")
        with open(path, "r") as f:
            return json.load(f)


def save_yaml_file(data: Dict[str, Any], path: Path):
    """Save data to YAML file."""
    try:
        import yaml

        with open(path, "w") as f:
            yaml.safe_dump(data, f, default_flow_style=False, indent=2)
    except ImportError:
        # Fallback to JSON
        with open(path, "w") as f:
            json.dump(data, f, indent=2)


def extract_ip_from_addresses(addresses: List[Dict[str, Any]]) -> Optional[str]:
    """Extract first IPv4 address from Incus address list."""
    for addr in addresses:
        if addr.get("family") == "inet" and addr.get("scope") == "global":
            return addr.get("address")
    return None


def validate_instance_name(name: str) -> bool:
    """Validate instance name follows naming conventions."""
    import re

    # Incus naming: lowercase, numbers, hyphens, 63 chars max
    return bool(re.match(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$", name) and len(name) <= 63)


def get_backup_path() -> Path:
    """Get backup directory path."""
    backup_dir = Path("/var/backups/yaz")
    ensure_dir(backup_dir)
    return backup_dir


class ProviderError(Exception):
    """Base exception for provider errors."""

    pass


class HealthCheckError(Exception):
    """Exception for health check failures."""

    pass


class InstanceNotFoundError(ProviderError):
    """Exception when instance not found."""

    pass


class ProviderUnavailableError(ProviderError):
    """Exception when provider is unavailable."""

    pass
