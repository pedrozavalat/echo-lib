from dataclasses import dataclass

from saviialib.libs.directory_client import DirectoryClient
from saviialib.libs.email_client import EmailClient
from saviialib.libs.notification_client import NotificationClient


@dataclass
class GetPendingTasksUseCaseInput:
    notification_client: NotificationClient
    email_client: EmailClient
    dir_client: DirectoryClient
    local_backup_path: str = ""
    download: bool = False
    notify: bool = False


@dataclass
class GetPendingTasksUseCaseOutput:
    overdue: list[dict[str, str | bool | dict]]
    ontime: list[dict[str, str | bool | dict]]
