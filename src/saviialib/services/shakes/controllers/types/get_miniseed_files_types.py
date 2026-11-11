from dataclasses import dataclass

from saviialib.general_types.api.saviia_shakes_api_types import SaviiaShakesConfig


@dataclass
class GetMiniseedFilesControllerInput:
    raspberry_shakes: dict[str, str]
    config: SaviiaShakesConfig


@dataclass
class GetMiniseedFilesControllerOutput:
    status: int
    metadata: dict
    message: str
