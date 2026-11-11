from dataclasses import dataclass
from logging import Logger

from saviialib.libs.cloud_client import CloudClient
from saviialib.libs.directory_client import DirectoryClient
from saviialib.libs.files_client import FilesClient
from saviialib.libs.ftp_client import FTPClient


@dataclass
class PostThiesDataUseCaseInput:
    ftp_client: FTPClient
    cloud_client: CloudClient
    files_client: FilesClient
    directory_client: DirectoryClient
    cloud_provider_destination_path: str
    ftp_server_folders_path: list[str]
    local_backup_source_path: str
    need_to_sync: bool
    need_to_backup: bool
    logger: Logger
