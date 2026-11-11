from dataclasses import dataclass, field

from saviialib.libs.notification_client import NotificationClient


@dataclass
class GetTasksUseCaseInput:
    notification_client: NotificationClient
    params: dict[str, str | bool | dict | list] = field(default_factory=dict)


@dataclass
class GetTasksUseCaseOutput:
    tasks: list[dict[str, str | bool | dict]]
