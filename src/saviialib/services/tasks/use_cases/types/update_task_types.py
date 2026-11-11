from dataclasses import dataclass

from saviialib.libs.email_client import EmailClient
from saviialib.libs.notification_client import NotificationClient
from saviialib.services.tasks.entities import SaviiaTask


@dataclass
class UpdateTaskUseCaseInput:
    task: SaviiaTask
    notification_client: NotificationClient
    email_client: EmailClient


@dataclass
class UpdateTaskUseCaseOutput:
    tid: str
    title: str
    deadline: str
    creation: str
    priority: int
    description: str | None
    periodicity: str | None
    assignee: str | None
    category: str | None
    completed: bool | None
