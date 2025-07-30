"""
Reproducibility Manager
Ensures deterministic and version-controlled analysis workflows
"""

import json
import hashlib
import os
import sys
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import pickle
from dataclasses import dataclass, asdict
import subprocess
from collections import defaultdict

from core.services.logger import get_logger

logger = get_logger(__name__)

@dataclass
class ExecutionMetadata:
    """Execution environment metadata"""
    dataset_hash: str
    config_id: str
    timestamp: datetime
    env_version: str
    analyst_id: str
    python_version: str
    dependencies: Dict[str, str]
    git_commit: Optional[str] = None
    hardware_info: Optional[Dict[str, Any]] = None

@dataclass
class AnalysisRun:
    """Complete analysis run record"""
    run_id: str
    execution_metadata: ExecutionMetadata
    input_data: Dict[str, Any]
    configuration: Dict[str, Any]
    results: Dict[str, Any]
    reproducible: bool = True

class ReproducibilityManager:
    """Manages reproducibility of analysis workflows and datasets"""
    
    def __init__(self, metadata_dir: str = "data/metadata"):
        self.metadata_dir = Path(metadata_dir)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        self.runs_dir = self.metadata_dir / "runs"
        self.runs_dir.mkdir(exist_ok=True)
        self.configs_dir = self.metadata_dir / "configs"
        self.configs_dir.mkdir(exist_ok=True)
        
        self.version_registry = {}
        self.execution_history = []
        
        logger.info("Reproducibility manager initialized")
    
    def create_dataset_fingerprint(self, data: Any, algorithm: str = "sha256") -> str:
        """Create a unique fingerprint for a dataset"""
        try:
            if isinstance(data, dict):
                # Sort keys for consistent hashing
                serialized = json.dumps(data, sort_keys=True, default=str)
            elif hasattr(data, 'to_dict'):
                # Handle pandas DataFrames and similar objects
                serialized = json.dumps(data.to_dict(), sort_keys=True, default=str)
            elif hasattr(data, '__dict__'):
                # Handle custom objects
                serialized = json.dumps(data.__dict__, sort_keys=True, default=str)
            else:
                # Handle other data types
                serialized = str(data)
            
            hash_func = hashlib.new(algorithm)
            hash_func.update(serialized.encode('utf-8'))
            return hash_func.hexdigest()
            
        except Exception as e:
            logger.error(f"Error creating dataset fingerprint: {e}")
            # Fallback to a basic hash
            return hashlib.sha256(str(data).encode()).hexdigest()
    
    def register_dataset_version(
        self, 
        dataset_name: str, 
        data: Any, 
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Register a new version of a dataset with metadata"""
        
        try:
            fingerprint = self.create_dataset_fingerprint(data)
            timestamp = datetime.now()
            
            if dataset_name not in self.version_registry:
                self.version_registry[dataset_name] = []
            
            version_info = {
                "dataset_name": dataset_name,
                "fingerprint": fingerprint,
                "timestamp": timestamp.isoformat(),
                "metadata": metadata or {},
                "version": len(self.version_registry[dataset_name]) + 1,
                "size": self._estimate_data_size(data),
                "type": type(data).__name__
            }
            
            self.version_registry[dataset_name].append(version_info)
            
            # Save to disk
            registry_file = self.metadata_dir / f"{dataset_name}_versions.json"
            with open(registry_file, 'w') as f:
                json.dump(self.version_registry[dataset_name], f, indent=2, default=str)
            
            logger.info(f"Registered dataset version: {dataset_name} v{version_info['version']}")
            
            return version_info
            
        except Exception as e:
            logger.error(f"Error registering dataset version: {e}")
            raise
    
    def get_current_environment_info(self) -> Dict[str, Any]:
        """Get current execution environment information"""
        
        try:
            # Python version
            python_version = sys.version
            
            # Git commit (if available)
            git_commit = None
            try:
                git_commit = subprocess.check_output(
                    ['git', 'rev-parse', 'HEAD'], 
                    stderr=subprocess.DEVNULL
                ).decode().strip()
            except:
                pass
            
            # Get installed packages
            dependencies = {}
            try:
                result = subprocess.run(
                    ['pip', 'freeze'], 
                    capture_output=True, 
                    text=True
                )
                for line in result.stdout.strip().split('\n'):
                    if '==' in line:
                        package, version = line.split('==', 1)
                        dependencies[package] = version
            except:
                pass
            
            # Hardware info
            import platform
            hardware_info = {
                "platform": platform.platform(),
                "processor": platform.processor(),
                "python_implementation": platform.python_implementation(),
                "machine": platform.machine(),
                "node": platform.node()
            }
            
            # Try to get more detailed hardware info
            try:
                import psutil
                hardware_info.update({
                    "cpu_count": psutil.cpu_count(),
                    "memory_total_gb": psutil.virtual_memory().total / (1024**3),
                    "disk_total_gb": psutil.disk_usage('/').total / (1024**3)
                })
            except:
                pass
            
            return {
                "python_version": python_version,
                "git_commit": git_commit,
                "dependencies": dependencies,
                "hardware_info": hardware_info,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting environment info: {e}")
            return {"error": str(e)}
    
    def create_execution_metadata(
        self,
        dataset_hash: str,
        config_id: str,
        analyst_id: str = "system"
    ) -> ExecutionMetadata:
        """Create execution metadata for analysis run"""
        
        env_info = self.get_current_environment_info()
        
        return ExecutionMetadata(
            dataset_hash=dataset_hash,
            config_id=config_id,
            timestamp=datetime.now(),
            env_version=env_info.get("python_version", "unknown"),
            analyst_id=analyst_id,
            python_version=env_info.get("python_version", "unknown"),
            dependencies=env_info.get("dependencies", {}),
            git_commit=env_info.get("git_commit"),
            hardware_info=env_info.get("hardware_info")
        )
    
    def save_configuration(self, config: Dict[str, Any]) -> str:
        """Save analysis configuration and return config ID"""
        
        try:
            config_hash = self.create_dataset_fingerprint(config)
            config_id = f"config_{config_hash[:12]}"
            
            config_file = self.configs_dir / f"{config_id}.json"
            
            config_record = {
                "config_id": config_id,
                "configuration": config,
                "hash": config_hash,
                "created_at": datetime.now().isoformat()
            }
            
            with open(config_file, 'w') as f:
                json.dump(config_record, f, indent=2, default=str)
            
            logger.info(f"Configuration saved: {config_id}")
            
            return config_id
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            raise
    
    def record_analysis_run(
        self,
        input_data: Any,
        configuration: Dict[str, Any],
        results: Dict[str, Any],
        analyst_id: str = "system"
    ) -> str:
        """Record complete analysis run for reproducibility"""
        
        try:
            # Create dataset hash
            dataset_hash = self.create_dataset_fingerprint(input_data)
            
            # Save configuration
            config_id = self.save_configuration(configuration)
            
            # Create execution metadata
            exec_metadata = self.create_execution_metadata(
                dataset_hash, config_id, analyst_id
            )
            
            # Create run ID
            run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{dataset_hash[:8]}"
            
            # Create analysis run record
            analysis_run = AnalysisRun(
                run_id=run_id,
                execution_metadata=exec_metadata,
                input_data={"hash": dataset_hash, "type": type(input_data).__name__},
                configuration=configuration,
                results=results
            )
            
            # Save run record
            run_file = self.runs_dir / f"{run_id}.json"
            with open(run_file, 'w') as f:
                json.dump(asdict(analysis_run), f, indent=2, default=str)
            
            # Store in execution history
            self.execution_history.append(analysis_run)
            
            logger.info(f"Analysis run recorded: {run_id}")
            
            return run_id
            
        except Exception as e:
            logger.error(f"Error recording analysis run: {e}")
            raise
    
    def get_run_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get analysis run history"""
        
        try:
            # Load from disk if not in memory
            if not self.execution_history:
                for run_file in self.runs_dir.glob("*.json"):
                    try:
                        with open(run_file) as f:
                            run_data = json.load(f)
                            self.execution_history.append(run_data)
                    except Exception as e:
                        logger.warning(f"Could not load run file {run_file}: {e}")
            
            # Sort by timestamp (most recent first)
            history = sorted(
                self.execution_history,
                key=lambda x: x.get('execution_metadata', {}).get('timestamp', ''),
                reverse=True
            )
            
            if limit:
                history = history[:limit]
            
            return [asdict(run) if hasattr(run, '__dict__') else run for run in history]
            
        except Exception as e:
            logger.error(f"Error getting run history: {e}")
            return []
    
    def reproduce_analysis(self, run_id: str) -> Dict[str, Any]:
        """Attempt to reproduce a previous analysis run"""
        
        try:
            # Load run record
            run_file = self.runs_dir / f"{run_id}.json"
            if not run_file.exists():
                raise ValueError(f"Run record not found: {run_id}")
            
            with open(run_file) as f:
                run_data = json.load(f)
            
            # Get configuration
            config_id = run_data['execution_metadata']['config_id']
            config_file = self.configs_dir / f"{config_id}.json"
            
            if not config_file.exists():
                raise ValueError(f"Configuration not found: {config_id}")
            
            with open(config_file) as f:
                config_data = json.load(f)
            
            configuration = config_data['configuration']
            
            # Check environment compatibility
            current_env = self.get_current_environment_info()
            original_env = run_data['execution_metadata']
            
            compatibility_issues = self._check_environment_compatibility(
                current_env, original_env
            )
            
            reproduction_result = {
                "run_id": run_id,
                "configuration": configuration,
                "original_execution_metadata": original_env,
                "current_environment": current_env,
                "compatibility_issues": compatibility_issues,
                "reproducible": len(compatibility_issues) == 0,
                "reproduction_timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Reproduction analysis for {run_id}: {'successful' if reproduction_result['reproducible'] else 'issues found'}")
            
            return reproduction_result
            
        except Exception as e:
            logger.error(f"Error reproducing analysis {run_id}: {e}")
            raise
    
    def create_reproducibility_report(self) -> Dict[str, Any]:
        """Create comprehensive reproducibility report"""
        
        try:
            history = self.get_run_history()
            
            # Analyze reproducibility patterns
            total_runs = len(history)
            unique_configs = len(set(
                run.get('execution_metadata', {}).get('config_id', '')
                for run in history
            ))
            
            # Analyze environment diversity
            environments = defaultdict(int)
            for run in history:
                env_info = run.get('execution_metadata', {})
                env_key = f"{env_info.get('python_version', 'unknown')}_{env_info.get('git_commit', 'unknown')[:8]}"
                environments[env_key] += 1
            
            # Recent run statistics
            recent_runs = history[:10] if history else []
            
            report = {
                "report_timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_analysis_runs": total_runs,
                    "unique_configurations": unique_configs,
                    "unique_environments": len(environments),
                    "dataset_versions": sum(len(versions) for versions in self.version_registry.values())
                },
                "recent_runs": [
                    {
                        "run_id": run.get('run_id'),
                        "timestamp": run.get('execution_metadata', {}).get('timestamp'),
                        "analyst_id": run.get('execution_metadata', {}).get('analyst_id'),
                        "reproducible": run.get('reproducible', True)
                    }
                    for run in recent_runs
                ],
                "environment_diversity": dict(environments),
                "registered_datasets": list(self.version_registry.keys()),
                "recommendations": self._generate_reproducibility_recommendations()
            }
            
            # Save report
            report_file = self.metadata_dir / f"reproducibility_report_{datetime.now().strftime('%Y%m%d')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            return report
            
        except Exception as e:
            logger.error(f"Error creating reproducibility report: {e}")
            raise
    
    def _estimate_data_size(self, data: Any) -> str:
        """Estimate data size"""
        try:
            if hasattr(data, '__len__'):
                return f"{len(data)} items"
            elif hasattr(data, 'shape'):
                return f"shape: {data.shape}"
            else:
                return "unknown size"
        except:
            return "unknown size"
    
    def _check_environment_compatibility(
        self, 
        current_env: Dict[str, Any], 
        original_env: Dict[str, Any]
    ) -> List[str]:
        """Check compatibility between environments"""
        
        issues = []
        
        # Check Python version
        current_python = current_env.get('python_version', '')
        original_python = original_env.get('python_version', '')
        
        if current_python != original_python:
            issues.append(f"Python version mismatch: current {current_python} vs original {original_python}")
        
        # Check Git commit
        current_commit = current_env.get('git_commit')
        original_commit = original_env.get('git_commit')
        
        if current_commit and original_commit and current_commit != original_commit:
            issues.append(f"Git commit mismatch: current {current_commit[:8]} vs original {original_commit[:8]}")
        
        # Check key dependencies
        current_deps = current_env.get('dependencies', {})
        original_deps = original_env.get('dependencies', {})
        
        critical_packages = ['pandas', 'numpy', 'scikit-learn', 'fastapi']
        
        for package in critical_packages:
            if package in original_deps:
                if package not in current_deps:
                    issues.append(f"Missing critical package: {package}")
                elif current_deps[package] != original_deps[package]:
                    issues.append(f"Package version mismatch: {package} current {current_deps[package]} vs original {original_deps[package]}")
        
        return issues
    
    def _generate_reproducibility_recommendations(self) -> List[str]:
        """Generate recommendations for improving reproducibility"""
        
        recommendations = []
        
        # Check if Git is being used
        env_info = self.get_current_environment_info()
        if not env_info.get('git_commit'):
            recommendations.append("Initialize Git repository and commit code changes for version tracking")
        
        # Check for dependency management
        if not env_info.get('dependencies'):
            recommendations.append("Use pip freeze or requirements.txt for dependency management")
        
        # Check run frequency
        if len(self.execution_history) < 5:
            recommendations.append("Record more analysis runs to establish reproducibility baseline")
        
        # Check for configuration diversity
        configs = set(
            run.get('execution_metadata', {}).get('config_id', '')
            for run in self.execution_history
        )
        if len(configs) < 3:
            recommendations.append("Test with diverse configurations to ensure robustness")
        
        if not recommendations:
            recommendations.append("Reproducibility practices are well-established")
        
        return recommendations
        
        # Store in registry
        if dataset_name not in self.version_registry:
            self.version_registry[dataset_name] = []
        
        self.version_registry[dataset_name].append(version_info)
        
        # Save metadata to file
        metadata_file = self.metadata_dir / f"{dataset_name}_v{version_info['version']}.json"
        with open(metadata_file, 'w') as f:
            json.dump(version_info, f, indent=2)
        
        logger.info(f"Registered dataset version: {dataset_name} v{version_info['version']}")
        return version_info
    
    def get_dataset_versions(self, dataset_name: str) -> List[Dict[str, Any]]:
        """Get all versions of a dataset"""
        return self.version_registry.get(dataset_name, [])
    
    def verify_dataset_integrity(self, dataset_name: str, data: Any, version: int = None) -> Dict[str, Any]:
        """Verify that a dataset matches its registered version"""
        current_fingerprint = self.create_dataset_fingerprint(data)
        
        versions = self.get_dataset_versions(dataset_name)
        if not versions:
            return {"verified": False, "error": "No versions registered for this dataset"}
        
        if version is None:
            # Check against latest version
            target_version = versions[-1]
        else:
            # Check against specific version
            target_versions = [v for v in versions if v["version"] == version]
            if not target_versions:
                return {"verified": False, "error": f"Version {version} not found"}
            target_version = target_versions[0]
        
        verified = current_fingerprint == target_version["fingerprint"]
        
        return {
            "verified": verified,
            "dataset_name": dataset_name,
            "target_version": target_version["version"],
            "current_fingerprint": current_fingerprint,
            "expected_fingerprint": target_version["fingerprint"],
            "checked_at": datetime.now().isoformat()
        }
    
    def create_analysis_recipe(self, analysis_name: str, parameters: Dict[str, Any], 
                             input_datasets: List[str], code_version: str = None) -> Dict[str, Any]:
        """Create a reproducible analysis recipe"""
        recipe_id = f"{analysis_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        recipe = {
            "recipe_id": recipe_id,
            "analysis_name": analysis_name,
            "parameters": parameters,
            "input_datasets": input_datasets,
            "code_version": code_version,
            "created_at": datetime.now().isoformat(),
            "environment": {
                "python_version": "3.10",  # Could get dynamically
                "dependencies": self._get_dependencies_info()
            }
        }
        
        # Save recipe
        recipe_file = self.metadata_dir / f"recipe_{recipe_id}.json"
        with open(recipe_file, 'w') as f:
            json.dump(recipe, f, indent=2)
        
        logger.info(f"Created analysis recipe: {recipe_id}")
        return recipe
    
    def execute_recipe(self, recipe_id: str, analysis_function, datasets: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an analysis recipe and track results"""
        recipe_file = self.metadata_dir / f"recipe_{recipe_id}.json"
        
        if not recipe_file.exists():
            raise ValueError(f"Recipe {recipe_id} not found")
        
        with open(recipe_file, 'r') as f:
            recipe = json.load(f)
        
        # Verify input datasets
        dataset_verification = {}
        for dataset_name in recipe["input_datasets"]:
            if dataset_name in datasets:
                verification = self.verify_dataset_integrity(dataset_name, datasets[dataset_name])
                dataset_verification[dataset_name] = verification
        
        execution_start = datetime.now()
        
        try:
            # Execute analysis
            result = analysis_function(datasets, recipe["parameters"])
            
            execution_result = {
                "recipe_id": recipe_id,
                "execution_id": f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "started_at": execution_start.isoformat(),
                "completed_at": datetime.now().isoformat(),
                "status": "success",
                "dataset_verification": dataset_verification,
                "result_fingerprint": self.create_dataset_fingerprint(result)
            }
            
        except Exception as e:
            execution_result = {
                "recipe_id": recipe_id,
                "execution_id": f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "started_at": execution_start.isoformat(),
                "completed_at": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e),
                "dataset_verification": dataset_verification
            }
            logger.error(f"Recipe execution failed: {e}")
        
        # Save execution log
        exec_file = self.metadata_dir / f"execution_{execution_result['execution_id']}.json"
        with open(exec_file, 'w') as f:
            json.dump(execution_result, f, indent=2)
        
        return execution_result
    
    def _get_dependencies_info(self) -> Dict[str, str]:
        """Get information about current dependencies"""
        # Simplified for MVP - could be enhanced to read actual package versions
        return {
            "fastapi": "0.104.1",
            "pandas": "2.1.3",
            "numpy": "1.25.2",
            "scikit-learn": "1.3.2"
        }
