from typing import Any


def parse_downloaded_metadata(responses: list[Any]) -> dict[str, Any]:
    return {
        x["rs_name"]: {
            "destination_path": x["destination_path"],
            "total_files": x["total_files"],
        }
        for x in responses
    }
