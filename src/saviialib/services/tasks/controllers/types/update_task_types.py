from dataclasses import dataclass, field
from typing import Any

from saviialib.general_types.api.saviia_tasks_api_types import SaviiaTasksConfig


@dataclass
class UpdateTaskControllerInput:
    task: dict[str, Any]
    completed: bool
    config: SaviiaTasksConfig


@dataclass
class UpdateTaskControllerOutput:
    message: str
    status: int
    metadata: dict[str, str] = field(default_factory=dict)
