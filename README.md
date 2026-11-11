# ECHO Library

> Edge Computing & Hardware Orchestration API library for Home Assistant.

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/pedrozavalat/echo-lib?style=for-the-badge)](https://github.com/pedrozavalat/echo-lib/releases)

## Table of Contents

- [Installation](#installation)
- [ECHO API Client Usage](#echo-api-client-usage)
  - [Initialize the ECHO API Client](#initialize-the-echo-api-client)
  - [Databricks host, token, and destination](#databricks-host-token-and-destination)
  - [Access THIES Data Logger Services](#access-thies-data-logger-services)
    - [THIES files extraction and synchronization](#thies-files-extraction-and-synchronization)
    - [Get THIES status](#get-thies-status)
    - [Post THIES precomputed actions](#post-thies-precomputed-actions)
    - [Detect Failures](#detect-failures)
  - [Access Backup Services](#access-backup-services)
    - [Export Files](#export-files)
  - [Migrating from SharePoint](#migrating-from-sharepoint)
  - [Access Netcamera Services](#access-netcamera-services)
    - [Get Camera Rates](#get-camera-rates)
  - [Access Task System Services](#access-task-system-services)
    - [Create Task](#create-task)
    - [Update Task](#update-task)
    - [Delete Task](#delete-task)
    - [Get Tasks](#get-tasks)
    - [Get Pending Tasks](#get-pending-tasks)
- [Related Projects](#related-projects)
- [Contributing](#contributing)
- [License](#license)

## Installation

ECHO Library supports the ECHO Home Assistant integration. It retrieves THIES Data Logger files over FTP, maintains a local backup, and synchronizes files to Databricks volumes through the Databricks Files API. Databricks is the cloud provider used by `SaviiaAPI` for THIES and backup services.

Python 3.11 or later is required. The Python package and public class names retain their existing `saviialib` / `Saviia` names:

```bash
pip install saviialib
```

## ECHO API Client Usage

### Initialize the ECHO API Client

Configure the local backup root, logger, Databricks workspace host, and access token. The following example reads credentials from environment variables supplied by your application or deployment:

```python
import logging
import os
from pathlib import Path

from saviialib import SaviiaAPI, SaviiaAPIConfig

config = SaviiaAPIConfig(
    logger=logging.getLogger("echo"),
    local_backup_path="saviia-local-backup",
    databricks_host_url=os.environ["DATABRICKS_HOST"],
    databricks_api_key=os.environ["DATABRICKS_TOKEN"],
)

Path(config.local_backup_path).mkdir(parents=True, exist_ok=True)
api_client = SaviiaAPI(config)
```

Relative local paths are resolved from the process's working directory. Use an absolute path when your deployment requires a fixed location; see the destination-path rules below.

The current `SaviiaAPIConfig` fields are:

| Field | Default | Use |
| --- | --- | --- |
| `logger` | Required | Python `logging.Logger`. |
| `local_backup_path` | Required | Local backup root. |
| `databricks_host_url` | `""` | Databricks workspace URL; required for cloud operations. |
| `databricks_api_key` | `""` | Databricks access token; required for cloud operations. |
| `latitude` | `-91` | Station latitude; set a valid value for Netcamera. |
| `longitude` | `-181` | Station longitude; set a valid value for Netcamera. |
| `tasks_channel_id` | `""` | Discord channel for Tasks. |
| `bot_token` | `""` | Discord bot token for Tasks. |
| `email_address` | `""` | Sender address for task emails. |
| `email_password` | `""` | SMTP credential for task emails. |
| `sharepoint_client_id`, `sharepoint_client_secret`, `sharepoint_tenant_id`, `sharepoint_tenant_name`, `sharepoint_site_name` | `None` | Legacy fields; not forwarded to the Databricks services created by `SaviiaAPI`. |

`api_client.get(name)` returns one of `thies`, `backup`, `netcamera`, or `tasks`. `api_client.list_available()` lists those service names. Configuration is copied into the services when `SaviiaAPI` is constructed; create a new client after changing configuration values.

Service operations are asynchronous. The examples use `asyncio.run()` in standalone scripts; inside an existing event loop, await the service method directly. Responses use `message`, numeric HTTP-style `status`, and `metadata`; inspect the status before reading success data. Initialization or connection failures can also raise exceptions.

### Databricks host, token, and destination

| Setting | Where to pass it | Meaning |
| --- | --- | --- |
| Workspace host | `SaviiaAPIConfig.databricks_host_url` | Workspace base URL, for example `https://adb-1234567890123456.7.azuredatabricks.net`. Do not append `/api/2.0/fs` or a volume path. |
| Access token | `SaviiaAPIConfig.databricks_api_key` | Raw token, without a `Bearer ` prefix. The client adds `Authorization: Bearer <token>`. |
| Destination | `cloud_provider_destination_path` on THIES and backup calls | Volume path, for example `/Volumes/catalog/schema/volume/echo`. Pass a path, not a workspace URL. |
| Local backup root | `SaviiaAPIConfig.local_backup_path` | Local directory used for downloaded THIES files and backup exports. |

`DATABRICKS_HOST` and `DATABRICKS_TOKEN` are environment-variable names chosen for the example. The explicit `os.environ` assignments pass them to the library; setting environment variables alone does not populate `SaviiaAPIConfig`.

The host and token fields default to empty strings in `SaviiaAPIConfig`, but both must be nonempty when the Databricks client is initialized. Otherwise, it raises `ValueError` with `Missing Databricks config fields`. The client sends the supplied token as-is; it does not obtain or refresh tokens. Keep the token in your deployment's secret configuration, not in source code.

FTP connection details belong to individual THIES calls, not to `SaviiaAPIConfig`:

```python
ftp_options = {
    "ftp_host": os.environ["THIES_FTP_HOST"],
    "ftp_port": int(os.environ.get("THIES_FTP_PORT", "21")),
    "ftp_user": os.environ["THIES_FTP_USER"],
    "ftp_password": os.environ["THIES_FTP_PASSWORD"],
}
cloud_destination = "/Volumes/catalog/schema/volume/echo"
```

### Access THIES Data Logger Services

The examples below reuse `api_client`, `config`, `ftp_options`, and `cloud_destination` from the setup above.

```python
thies_service = api_client.get("thies")
```

#### THIES files extraction and synchronization

Use `get_thies_data` to inspect FTP, local, and cloud inventories, and `post_thies_data` to perform backup and synchronization. The former `update_thies_data` method has been removed.

THIES stores files under these paths:

| Location | AVG folder with the example configuration |
| --- | --- |
| FTP | `/ARCH_AV1` (`/ARCH_EX1` for EXT) |
| Local backup | `saviia-local-backup/thies/AVG` |
| Databricks | `/Volumes/catalog/schema/volume/echo/saviia-local-backup/thies/AVG` |

THIES appends the **name of the local backup root**, followed by `thies/AVG` or `thies/EXT`, to `cloud_provider_destination_path`. Pass the base destination, without adding these suffixes yourself. An absolute local root such as `/config/saviia-local-backup` produces the same THIES cloud path shown above.

##### Get THIES status

```python
import asyncio


async def main():
    response = await thies_service.get_thies_data(
        **ftp_options,
        cloud_provider_destination_path=cloud_destination,
    )
    if response["status"] != 200:
        raise RuntimeError(response["message"])
    return response["metadata"]["data"]


print(asyncio.run(main()))
```

A successful response contains `need_to_backup` and `need_to_sync` inside `metadata["data"]`. Status inspection uses the FTP folders `/ARCH_AV1` and `/ARCH_EX1`.

##### Post THIES precomputed actions

To request both a local backup and cloud synchronization:

```python
import asyncio


async def main():
    return await thies_service.post_thies_data(
        **ftp_options,
        need_to_backup=True,
        need_to_sync=True,
        cloud_provider_destination_path=cloud_destination,
        ftp_server_folders_path=["/ARCH_AV1", "/ARCH_EX1"],
    )


print(asyncio.run(main()))
```

You can also supply flags computed by your application or obtained from the status response. `need_to_backup` requests downloading pending FTP files into the local backup; `need_to_sync` requests uploading pending local files to Databricks. Request both to back up and synchronize in the same operation.

`post_thies_data` reads the local root from `config.local_backup_path`; it no longer accepts `local_backup_source_path`. Supply the AVG FTP folder first, followed by EXT.

##### Detect Failures

Use `detect_failures` to scan a local THIES backup for missing or corrupt files over the last N days:

```python
import asyncio


async def main():
    return await thies_service.detect_failures(
        local_backup_source_path=config.local_backup_path,
        n_days=7,
    )


print(asyncio.run(main()))
```

### Access Backup Services

```python
backup_service = api_client.get("backup")
```

#### Export Files

Use `export_files` to upload files from an existing local folder under `config.local_backup_path` to Databricks. It compares file names and sizes and uploads missing files or files with differing nonzero sizes. A zero size on either side is treated as unknown and does not by itself trigger an upload.

```python
import asyncio


async def main():
    return await backup_service.export_files(
        local_folder_path="thies/AVG",
        cloud_provider_destination_path=cloud_destination,
    )


print(asyncio.run(main()))
```

The source folder must exist and contain files only; this operation does not recursively export subdirectories or download files from FTP.

The current backup exporter appends the **joined local source path**, with leading/trailing slashes stripped, to the cloud destination:

- With `local_backup_path="saviia-local-backup"`, this example uploads to `/Volumes/catalog/schema/volume/echo/saviia-local-backup/thies/AVG`.
- With `local_backup_path="/config/saviia-local-backup"`, it uploads to `/Volumes/catalog/schema/volume/echo/config/saviia-local-backup/thies/AVG`.

This differs from THIES synchronization, which appends only the backup root's name. Account for this when choosing local and cloud paths. Do not pass the already-expanded destination to `export_files`, as the local path would be appended again.

### Migrating from SharePoint

- Supply `databricks_host_url` and `databricks_api_key` instead of SharePoint credentials when using `SaviiaAPI`.
- Replace `sharepoint_destination_path` with `cloud_provider_destination_path` and use a `/Volumes/...` destination.
- Replace `upload_backup_to_sharepoint` with `export_files` for uploading existing local files.
- Replace `update_thies_data` with the THIES status and post methods described above.
- Keep the local backup root in the configuration instead of passing it to `post_thies_data`.

The lower-level `CloudClient` still includes a SharePoint adapter, but the `SaviiaAPI` workflow documented here uses Databricks. When constructing service configurations directly, `SaviiaBackupConfig.client_name` defaults to `"databricks"`; `SaviiaThiesConfig` requires `cloud_client_name="databricks"`.

### Access Netcamera Services

Set `latitude` and `longitude` in `SaviiaAPIConfig` before creating the client. Netcamera reads them from its service configuration; `get_camera_rates()` takes no arguments.

```python
from dataclasses import replace

camera_config = replace(config, latitude=-33.45, longitude=-70.66)
netcamera_service = SaviiaAPI(camera_config).get("netcamera")
```

#### Get Camera Rates

```python
import asyncio


async def main():
    return await netcamera_service.get_camera_rates()


print(asyncio.run(main()))
```

The response contains `message`, a numeric HTTP-style `status`, and `metadata`. On success, `metadata` contains the weather category (`status`: `A`, `B`, or `C`), `photo_rate`, `video_rate`, `precipitation_probability`, and `precipitation`.

Rates are intervals in minutes, calculated from Open-Meteo precipitation data:

| Weather category | Photo interval | Video interval |
| --- | --- | --- |
| A | 720 minutes | 720 minutes |
| B | 30 minutes | 180 minutes |
| C | 5 minutes | 60 minutes |

### Access Task System Services

Tasks are stored as messages in a Discord channel. Configure the bot and channel when creating `SaviiaAPI`, then obtain the service through `get("tasks")`. Service methods do not accept a `config` argument.

```python
from dataclasses import replace

# Reuse the base configuration from the initialization example.
tasks_config = replace(
    config,
    tasks_channel_id=os.environ["DISCORD_TASKS_CHANNEL_ID"],
    bot_token=os.environ["DISCORD_BOT_TOKEN"],
    email_address=os.environ.get("TASKS_EMAIL_ADDRESS", ""),
    email_password=os.environ.get("TASKS_EMAIL_PASSWORD", ""),
)
tasks_service = SaviiaAPI(tasks_config).get("tasks")
```

The public `SaviiaAPIConfig` field is **`tasks_channel_id`** (plural). The library maps it to `task_channel_id` in the internal `SaviiaTasksConfig`. The Discord bot needs access to the configured channel and permissions for the requested message/reaction operations.

Email credentials are used when notifying assignees by email. The current task controllers use `smtp.gmail.com` on port `587`.

#### Create Task

Use `title`, `creation`, and `deadline` for task data. Dates are parsed as `YYYY-MM-DD` by the current validators.

```python
import asyncio

task_data = {
    "title": "Inspect the THIES station",
    "creation": "2026-11-11",
    "deadline": "2026-11-30",
    "execution": "",
    "priority": 2,
    "assignee": "Station operator",
    "assignee_email": "",
    "assignee_discord_username": "",
    "description": "Check the sensor and its local backup.",
    "periodicity": "Sin periodicidad",
    "category": "Maintenance",
}


async def main():
    return await tasks_service.create_task(task=task_data, images=[])


print(asyncio.run(main()))
```

Required task fields are `title`, `creation`, `deadline`, `priority` (integer from 1 to 4), and `assignee`. Other fields shown above may be empty strings. The date order must satisfy `creation <= execution <= deadline`; an empty `execution` is treated as the creation date for validation.

`images` is optional and accepts up to 10 dictionaries containing `name`, `type`, and Base64-encoded `data`. A successful create response provides the Discord message ID as `response["metadata"]["task_id"]`. Save that ID for updates and deletion. Providing an `assignee_email` also requests an assignment email.

#### Update Task

Provide the complete task data and the saved ID under `tid`, together with the `completed` flag:

```python
import asyncio

updated_task = {
    **task_data,
    "tid": "123456789012345678",  # Replace with metadata["task_id"] from creation.
    "execution": "2026-11-12",
    "description": "Sensor and local backup checked.",
}


async def main():
    return await tasks_service.update_task(task=updated_task, completed=True)


print(asyncio.run(main()))
```

Updates use `tid`; creation responses and task listings use `task_id`. The update method replaces task details, so keep all fields from the example rather than sending only the changed fields. The task is marked with ✅ when completed and 📌 when pending.

#### Delete Task

```python
import asyncio


async def main():
    return await tasks_service.delete_task(task_id="123456789012345678")


print(asyncio.run(main()))
```

#### Get Tasks

```python
import asyncio


async def main():
    return await tasks_service.get_tasks(
        params={
            "completed": False,
            "fields": ["title", "deadline", "priority", "assignee"],
        }
    )


print(asyncio.run(main()))
```

Successful results are in `response["metadata"]["tasks"]`.

- Omit `params` to retrieve tasks without additional filtering or field selection, including their `task_id`.
- `completed` filters by completion status.
- `fields` selects from `title`, `deadline`, `priority`, `description`, `periodicity`, and `assignee`; the list must contain `title` and `deadline`.
- The schema also accepts `sort`, `after`, and `before`, but their current implementation references the legacy `task.due_date` structure. They are not reliable with the current task format and are omitted from this example.

#### Get Pending Tasks

```python
import asyncio


async def main():
    return await tasks_service.get_pending_tasks(download=False, notify=False)


print(asyncio.run(main()))
```

The response groups tasks into `metadata["overdue"]` and `metadata["ontime"]`.

- `download=True` writes a dated Excel report under `<local_backup_path>/saviia-tasks/YYYYMMDD_tasks.xlsx`. It does not download task attachments. The local backup root must exist, and the environment needs a pandas-compatible Excel writer such as `openpyxl`.
- `notify=True` emails each assignee with their pending-task summary, using `assignee_email`. Assignees without an email address are skipped. It does not post a pending-task summary to Discord.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development and release instructions. Run `make test` and `make lint` before submitting changes.

## Related Projects

- [ECHO](https://github.com/raxlab/echo): A Home Assistant custom integration for Edge Computing and Hardware Orchestration that uses this library.

## License

`saviialib` was created by Pedro Pablo Zavala Tejos. It is licensed under the terms of the MIT license.
