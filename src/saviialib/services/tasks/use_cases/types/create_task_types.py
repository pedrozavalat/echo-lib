from dataclasses import dataclass

from saviialib.libs.email_client import EmailClient
from saviialib.libs.notification_client import NotificationClient
from saviialib.services.tasks.entities.task import SaviiaTask


@dataclass
class CreateTaskUseCaseInput:
    task: SaviiaTask
    notification_client: NotificationClient
    email_client: EmailClient


@dataclass
class CreateTaskUseCaseOutput:
    task_id: str
