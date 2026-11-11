from abc import ABC, abstractmethod

from .types.sftp_client_types import DownloadfilesArgs, ListfilesArgs


class SFTPClientContract(ABC):
    @abstractmethod
    async def list_files(self, args: ListfilesArgs) -> list[str]:
        pass

    @abstractmethod
    async def download_files(self, args: DownloadfilesArgs) -> None:
        pass
