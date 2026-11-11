from dataclasses import dataclass, field
from logging import Logger


@dataclass
class GetMiniseedFilesUseCaseInput:
    raspberry_shakes: dict[str, str]
    username: str
    password: str
    ssh_key_path: str
    port: int
    logger: Logger


@dataclass
class GetMiniseedFilesUseCaseOutput:
    download_status: dict[str, str] = field(default_factory=dict)
