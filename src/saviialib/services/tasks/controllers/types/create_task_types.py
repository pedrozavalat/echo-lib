from dataclasses import dataclass, field

from saviialib.general_types.api.saviia_tasks_api_types import SaviiaTasksConfig


@dataclass
class CreateTaskControllerInput:
    task: dict
    images: list
    config: SaviiaTasksConfig


@dataclass
class CreateTaskControllerOutput:
    message: str
    status: int
    metadata: dict[str, str] = field(default_factory=dict)
