from dataclasses import dataclass, field

from saviialib.general_types.api.saviia_tasks_api_types import SaviiaTasksConfig


@dataclass
class GetPendingTasksControllerInput:
    config: SaviiaTasksConfig
    download: bool = False
    notify: bool = False


@dataclass
class GetPendingTasksControllerOutput:
    message: str
    status: int
    metadata: dict[str, str] = field(default_factory=dict)
