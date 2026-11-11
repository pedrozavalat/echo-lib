from dataclasses import dataclass, field

from saviialib.general_types.api.saviia_tasks_api_types import SaviiaTasksConfig


@dataclass
class GetTasksControllerInput:
    config: SaviiaTasksConfig
    params: dict[str, str | bool | dict | list] = field(default_factory=dict)


@dataclass
class GetTasksControllerOutput:
    message: str
    status: int
    metadata: dict[str, str] = field(default_factory=dict)
