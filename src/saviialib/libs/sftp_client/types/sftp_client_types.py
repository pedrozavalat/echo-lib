from dataclasses import dataclass, field


@dataclass
class SFTPClientInitArgs:
    client_name: str
    password: str | None
    username: str
    ssh_key_path: str
    host: str = "localhost"
    port: int = 22


@dataclass
class ListfilesArgs:
    path: str


@dataclass
class DownloadfilesArgs:
    source_path: str
    destination_path: str
    files_to_download: list[str] = field(default_factory=list)
