import builtins
import csv
import ftplib
import threading
from unittest.mock import MagicMock

import pytest

from saviialib.general_types.api.saviia_api_types import FtpClientConfig
from saviialib.libs.files_client.clients.csv_client import CsvClient
from saviialib.libs.files_client.types.files_client_types import (
    FilesClientInitArgs,
    WriteArgs,
)
from saviialib.libs.ftp_client.clients.ftplib_client import FtplibClient
from saviialib.libs.ftp_client.types.ftp_client_types import (
    FtpClientInitArgs,
    FtpListFilesArgs,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(("extension", "delimiter"), [("csv", ","), ("tsv", "\t")])
async def test_csv_write_preserves_rows_and_opens_file_off_event_loop(
    tmp_path, monkeypatch, extension, delimiter
):
    main_thread = threading.get_ident()
    open_threads = []
    original_open = builtins.open

    def track_open(*args, **kwargs):
        open_threads.append(threading.get_ident())
        return original_open(*args, **kwargs)

    monkeypatch.setattr(
        "saviialib.libs.files_client.clients.csv_client.open", track_open, raising=False
    )
    rows = [
        {"name": "sensor, one", "value": "12"},
        {"name": "sensor\ttwo", "value": "34"},
    ]
    filename = f"data.{extension}"
    client = CsvClient(FilesClientInitArgs(client_name="csv"))
    await client.write(WriteArgs(filename, rows, "w", str(tmp_path)))

    with (tmp_path / filename).open(newline="") as stream:
        assert list(csv.DictReader(stream, delimiter=delimiter)) == rows
    assert open_threads and all(thread != main_thread for thread in open_threads)


@pytest.mark.asyncio
async def test_ftp_listing_falls_back_when_server_rejects_mlsd_and_size():
    client = FtplibClient(
        FtpClientInitArgs(FtpClientConfig("localhost", 21, "user", "password"))
    )
    client.client = MagicMock()
    client.client.mlsd.side_effect = ftplib.error_perm("500 MLSD unsupported")
    client.client.nlst.return_value = [".", "..", "known.bin", "unknown.bin"]
    client.client.size.side_effect = [42, ftplib.error_perm("550 SIZE unavailable")]

    assert await client.list_files(FtpListFilesArgs("/data")) == [
        ("known.bin", 42),
        ("unknown.bin", 0),
    ]
