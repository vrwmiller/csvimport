import csv
import sys
import os

sys.path.insert(
    0, os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
)  # noqa: E402
import pytest  # noqa: E402
from unittest.mock import MagicMock, patch  # noqa: E402
from csvimport import fetch_sheet_entries  # noqa: E402


class DummyLogger:
    handlers = []

    def info(self, msg):
        pass

    def error(self, msg):
        pass

    def debug(self, msg):
        pass


def _make_mocks(
    creds_mock,
    gspread_mock,
    rows=None,
    fail_at=None,
):
    """
    Build the standard gspread mock chain. fail_at can be one of:
    'creds', 'authorize', 'open_by_key', 'worksheet', 'get_all_records'
    """
    error = RuntimeError("mock error")

    if fail_at == "creds":
        creds_mock.from_service_account_file.side_effect = error
        return

    creds_instance = MagicMock()
    creds_mock.from_service_account_file.return_value = creds_instance

    if fail_at == "authorize":
        gspread_mock.authorize.side_effect = error
        return

    client_mock = MagicMock()
    gspread_mock.authorize.return_value = client_mock

    if fail_at == "open_by_key":
        client_mock.open_by_key.side_effect = error
        return

    sheet_mock = MagicMock()
    client_mock.open_by_key.return_value = sheet_mock

    if fail_at == "worksheet":
        sheet_mock.worksheet.side_effect = error
        return

    worksheet_mock = MagicMock()
    sheet_mock.worksheet.return_value = worksheet_mock

    if fail_at == "get_all_records":
        worksheet_mock.get_all_records.side_effect = error
        return

    worksheet_mock.get_all_records.return_value = rows if rows is not None else []


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_fetch_sheet_entries_returns_rows():
    with patch("csvimport.gspread") as gspread_mock, patch(
        "csvimport.Credentials"
    ) as creds_mock, patch("csvimport.os.getcwd", return_value="/tmp"):
        _make_mocks(creds_mock, gspread_mock, rows=[{"A": "1"}, {"A": "2"}])
        result = fetch_sheet_entries(
            "sheetid", "sheetname", "creds.json", DummyLogger()
        )
        assert result == [{"A": "1"}, {"A": "2"}]


# ---------------------------------------------------------------------------
# Exception paths
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fail_at",
    ["creds", "authorize", "open_by_key", "worksheet", "get_all_records"],
)
def test_fetch_sheet_entries_raises_on_failure(fail_at):
    with patch("csvimport.gspread") as gspread_mock, patch(
        "csvimport.Credentials"
    ) as creds_mock:
        _make_mocks(creds_mock, gspread_mock, fail_at=fail_at)
        with pytest.raises(RuntimeError, match="mock error"):
            fetch_sheet_entries("sheetid", "sheetname", "creds.json", DummyLogger())


# ---------------------------------------------------------------------------
# Backup logic
# ---------------------------------------------------------------------------


def test_fetch_sheet_entries_backup_written(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rows = [{"Col1": "a", "Col2": "b"}, {"Col1": "c", "Col2": "d"}]
    with patch("csvimport.gspread") as gspread_mock, patch(
        "csvimport.Credentials"
    ) as creds_mock:
        _make_mocks(creds_mock, gspread_mock, rows=rows)
        fetch_sheet_entries("sheetid", "mysheet", "creds.json", DummyLogger())

    backup_dir = tmp_path / "backups"
    assert backup_dir.exists()
    backup_files = list(backup_dir.glob("mysheet_backup_*.csv"))
    assert len(backup_files) == 1

    with open(backup_files[0], newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        written = list(reader)
    assert written == rows


def test_fetch_sheet_entries_no_backup_when_empty(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with patch("csvimport.gspread") as gspread_mock, patch(
        "csvimport.Credentials"
    ) as creds_mock:
        _make_mocks(creds_mock, gspread_mock, rows=[])
        fetch_sheet_entries("sheetid", "mysheet", "creds.json", DummyLogger())

    backup_dir = tmp_path / "backups"
    backup_files = (
        list(backup_dir.glob("mysheet_backup_*.csv")) if backup_dir.exists() else []
    )
    assert len(backup_files) == 0
