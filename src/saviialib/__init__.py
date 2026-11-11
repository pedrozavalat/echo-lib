# read version from installed package
from importlib.metadata import version
from typing import ClassVar

__version__ = version("saviialib")

from typing import Any, Literal, overload

from saviialib.services import (
    SaviiaBackupAPI,
    SaviiaBackupConfig,
    SaviiaNetcameraAPI,
    SaviiaNetcameraConfig,
    SaviiaTasksAPI,
    SaviiaTasksConfig,
    SaviiaThiesAPI,
    SaviiaThiesConfig,
)

from .general_types.api.saviia_api_types import SaviiaAPIConfig

__all__ = ["SaviiaAPI", "SaviiaAPIConfig"]


class SaviiaAPI:
    API_REGISTRY: ClassVar[dict[str, type]] = {
        "thies": SaviiaThiesAPI,
        "backup": SaviiaBackupAPI,
        "netcamera": SaviiaNetcameraAPI,
        "tasks": SaviiaTasksAPI,
    }

    @overload
    def get(self, name: Literal["thies"]) -> SaviiaThiesAPI: ...
    @overload
    def get(self, name: Literal["backup"]) -> SaviiaBackupAPI: ...
    @overload
    def get(self, name: Literal["netcamera"]) -> SaviiaNetcameraAPI: ...
    @overload
    def get(self, name: Literal["tasks"]) -> SaviiaTasksAPI: ...
    def __init__(self, config: SaviiaAPIConfig):
        """
        Receive a dictionary of configurations, with the same key
        as those registered in API_REGISTRY.

        :params configs: Dictionary of configurations for each API.

        Example:
            configs = {
                "thies": SaviiaThiesConfig(...),
                "backup": SaviiaBackupConfig(...),
                "netcamera": SaviiaNetcameraConfig(...),
                "tasks": SaviiaTasksConfig(...),
            }
        """
        self._instances: dict[str, Any] = {}

        for name, api_class in SaviiaAPI.API_REGISTRY.items():
            if name == "thies":
                service_config = SaviiaThiesConfig(
                    local_backup_path=config.local_backup_path,
                    cloud_client_name="databricks",
                    databricks_host_url=config.databricks_host_url,
                    databricks_api_key=config.databricks_api_key,
                    logger=config.logger,
                    latitude=config.latitude,
                    longitude=config.longitude,
                )
            elif name == "backup":
                service_config = SaviiaBackupConfig(
                    databricks_api_key=config.databricks_api_key,
                    databricks_host_url=config.databricks_host_url,
                    logger=config.logger,
                    local_backup_path=config.local_backup_path,
                )
            elif name == "netcamera":
                service_config = SaviiaNetcameraConfig(
                    latitude=config.latitude,
                    longitude=config.longitude,
                )

            elif name == "tasks":
                service_config = SaviiaTasksConfig(
                    bot_token=config.bot_token,
                    task_channel_id=config.tasks_channel_id,
                    email_address=config.email_address,
                    email_password=config.email_password,
                    local_backup_path=config.local_backup_path,
                )

            self._instances[name] = api_class(service_config)

    def get(self, name: Literal["thies", "backup", "netcamera", "tasks"]) -> Any:
        """Returns the API instance associated with the given name."""
        try:
            return self._instances[name]
        except KeyError:
            raise ValueError(f"API '{name}' is not registered or not configured.")

    def list_available(self) -> list[str]:
        """List of available registered APIs."""
        return list(self._instances.keys())
