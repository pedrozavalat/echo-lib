from dataclasses import dataclass, field

from saviialib.general_types.api.saviia_tasks_api_types import SaviiaTasksConfig


@dataclass
class DeleteTaskControllerInput:
    task_id: str
    config: SaviiaTasksConfig


@dataclass
class DeleteTaskControllerOutput:
    message: str
    status: int
    metadata: dict[str, str] = field(default_factory=dict)
