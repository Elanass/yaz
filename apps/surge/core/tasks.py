"""Task Pipeline System for Surge
DAG-based task execution with domain-specific workflows.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


logger = logging.getLogger(__name__)


@dataclass
class TaskSpec:
    """Specification for a pipeline task."""

    name: str
    description: str
    depends_on: list[str]
    domain: str | None = None
    enabled: bool = True
    params: dict[str, Any] = None


class TaskRunner:
    """Executes tasks in dependency order."""

    def __init__(self, tasks_config: dict[str, Any]) -> None:
        self.tasks = {}
        self.load_tasks(tasks_config)

    def load_tasks(self, config: dict[str, Any]) -> None:
        """Load tasks from configuration."""
        for name, spec in config.get("tasks", {}).items():
            self.tasks[name] = TaskSpec(
                name=name,
                description=spec.get("description", ""),
                depends_on=spec.get("depends_on", []),
                domain=spec.get("domain"),
                enabled=spec.get("enabled", True),
                params=spec.get("params", {}),
            )

    def get_execution_order(
        self, target_tasks: list[str], skip_tasks: list[str] | None = None
    ) -> list[str]:
        """Calculate task execution order respecting dependencies."""
        skip_tasks = skip_tasks or []
        execution_order = []
        completed = set()

        def can_execute(task_name: str) -> bool:
            task = self.tasks[task_name]
            return all(dep in completed for dep in task.depends_on)

        def add_dependencies(task_name: str, visited: set[str] | None = None) -> None:
            visited = visited or set()
            if task_name in visited:
                msg = f"Circular dependency detected involving {task_name}"
                raise ValueError(msg)

            visited.add(task_name)
            task = self.tasks[task_name]

            for dep in task.depends_on:
                if dep not in completed and dep not in skip_tasks:
                    add_dependencies(dep, visited.copy())

            if (
                task_name not in completed
                and task_name not in skip_tasks
                and task.enabled
            ):
                execution_order.append(task_name)
                completed.add(task_name)

        for task_name in target_tasks:
            if task_name in self.tasks:
                add_dependencies(task_name)

        return execution_order

    def list_tasks(self) -> dict[str, TaskSpec]:
        """List all available tasks."""
        return self.tasks


def load_tasks_config(domain: str | None = None) -> dict[str, Any]:
    """Load tasks configuration for domain."""
    config_path = Path("tasks.yaml")

    if not config_path.exists():
        # Create default configuration
        default_config = {
            "version": "1.0",
            "tasks": {
                "load_csv": {
                    "description": "Load and validate CSV data",
                    "depends_on": [],
                    "domain": "surgery",
                    "enabled": True,
                },
                "validate_tnm": {
                    "description": "Validate TNM staging data",
                    "depends_on": ["load_csv"],
                    "domain": "surgery",
                    "enabled": True,
                },
                "km_curve": {
                    "description": "Generate Kaplan-Meier survival curves",
                    "depends_on": ["validate_tnm"],
                    "domain": "surgery",
                    "enabled": True,
                    "params": {"confidence_interval": 0.95},
                },
                "deliver_pdf": {
                    "description": "Generate PDF deliverable",
                    "depends_on": ["km_curve"],
                    "domain": "surgery",
                    "enabled": True,
                },
            },
        }

        with open(config_path, "w") as f:
            yaml.dump(default_config, f, default_flow_style=False)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Filter by domain if specified
    if domain:
        filtered_tasks = {}
        for name, task in config.get("tasks", {}).items():
            if task.get("domain") == domain or task.get("domain") is None:
                filtered_tasks[name] = task
        config["tasks"] = filtered_tasks

    return config


def create_sample_dataset() -> Path:
    """Create sample gastric cohort dataset."""
    sample_data = pd.DataFrame(
        {
            "patient_id": [f"P{i:03d}" for i in range(1, 11)],
            "age": [65, 72, 58, 67, 71, 63, 69, 74, 61, 66],
            "gender": ["M", "F", "M", "F", "M", "F", "M", "F", "M", "F"],
            "tnm_stage": [
                "T2N0M0",
                "T3N1M0",
                "T1N0M0",
                "T4N2M1",
                "T2N1M0",
                "T3N0M0",
                "T2N2M0",
                "T1N0M0",
                "T3N1M0",
                "T2N0M0",
            ],
            "protocol": [
                "FLOT",
                "XELOX",
                "ECF",
                "XELOX",
                "FLOT",
                "ECF",
                "FLOT",
                "XELOX",
                "ECF",
                "FLOT",
            ],
            "survival_months": [36, 18, 48, 8, 24, 42, 15, 60, 30, 45],
            "recurrence": [0, 1, 0, 1, 0, 0, 1, 0, 0, 0],
            "resection_margin": [
                "R0",
                "R1",
                "R0",
                "R2",
                "R0",
                "R0",
                "R1",
                "R0",
                "R0",
                "R0",
            ],
        }
    )

    # Ensure directory exists
    data_dir = Path("data/test_samples")
    data_dir.mkdir(parents=True, exist_ok=True)

    sample_path = data_dir / "sample_gastric_cohort.csv"
    sample_data.to_csv(sample_path, index=False)

    return sample_path
