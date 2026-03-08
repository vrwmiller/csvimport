import csv
import os
import subprocess
import sys
import unittest.mock as mock

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csvimport  # noqa: E402

SCRIPT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "csvimport.py"
)
COLS = ["Date", "Amount", "Description"]


def _write_csv(path, fieldnames, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _read_csv(path):
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------------------
# Item 8: main() --existing-csv
# ---------------------------------------------------------------------------


def test_main_existing_csv_dedup(tmp_path):
    """Rows present in the existing CSV are removed from output."""
    input_csv = tmp_path / "input.csv"
    existing_csv = tmp_path / "existing.csv"
    output_csv = tmp_path / "output.csv"
    log_file = tmp_path / "test.log"

    _write_csv(
        input_csv,
        COLS,
        [
            {"Date": "2026-01-01", "Amount": "10.00", "Description": "Coffee"},
            {"Date": "2026-01-02", "Amount": "20.00", "Description": "Lunch"},
            {"Date": "2026-01-03", "Amount": "30.00", "Description": "Dinner"},
        ],
    )
    _write_csv(
        existing_csv,
        COLS,
        [{"Date": "2026-01-01", "Amount": "10.00", "Description": "Coffee"}],
    )

    result = subprocess.run(
        [
            sys.executable,
            SCRIPT,
            "--input-files",
            str(input_csv),
            "--input-format",
            "Date,Amount,Description",
            "--output-format",
            "Date,Amount,Description",
            "--key-columns",
            "Date,Amount",
            "--existing-csv",
            str(existing_csv),
            "--output",
            str(output_csv),
            "--log-file",
            str(log_file),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    rows = _read_csv(output_csv)
    assert len(rows) == 2
    dates = {r["Date"] for r in rows}
    assert "2026-01-02" in dates
    assert "2026-01-03" in dates
    assert "2026-01-01" not in dates


def test_main_existing_csv_no_match(tmp_path):
    """When no existing rows match, all input rows appear in output."""
    input_csv = tmp_path / "input.csv"
    existing_csv = tmp_path / "existing.csv"
    output_csv = tmp_path / "output.csv"
    log_file = tmp_path / "test.log"

    _write_csv(
        input_csv,
        COLS,
        [
            {"Date": "2026-02-01", "Amount": "15.00", "Description": "A"},
            {"Date": "2026-02-02", "Amount": "25.00", "Description": "B"},
        ],
    )
    _write_csv(
        existing_csv,
        COLS,
        [{"Date": "2025-12-31", "Amount": "99.00", "Description": "Old"}],
    )

    result = subprocess.run(
        [
            sys.executable,
            SCRIPT,
            "--input-files",
            str(input_csv),
            "--input-format",
            "Date,Amount,Description",
            "--output-format",
            "Date,Amount,Description",
            "--key-columns",
            "Date,Amount",
            "--existing-csv",
            str(existing_csv),
            "--output",
            str(output_csv),
            "--log-file",
            str(log_file),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    rows = _read_csv(output_csv)
    assert len(rows) == 2


# ---------------------------------------------------------------------------
# Item 9: main() --key-columns CLI override
# ---------------------------------------------------------------------------


def test_main_key_columns_cli_dedup_on_single_column(tmp_path):
    """--key-columns controls which columns drive dedup."""
    input_csv = tmp_path / "input.csv"
    existing_csv = tmp_path / "existing.csv"
    log_file = tmp_path / "test.log"

    # Two input rows sharing the same Date but different Amounts
    _write_csv(
        input_csv,
        COLS,
        [
            {"Date": "2026-03-01", "Amount": "10.00", "Description": "X"},
            {"Date": "2026-03-01", "Amount": "99.00", "Description": "Y"},
        ],
    )
    # Existing row has same Date but different Amount
    _write_csv(
        existing_csv,
        COLS,
        [{"Date": "2026-03-01", "Amount": "55.00", "Description": "Existing"}],
    )

    # Key on Date: both input rows match existing (same Date) -> 0 output rows
    output_csv1 = tmp_path / "output1.csv"
    result1 = subprocess.run(
        [
            sys.executable,
            SCRIPT,
            "--input-files",
            str(input_csv),
            "--input-format",
            "Date,Amount,Description",
            "--output-format",
            "Date,Amount,Description",
            "--key-columns",
            "Date",
            "--existing-csv",
            str(existing_csv),
            "--output",
            str(output_csv1),
            "--log-file",
            str(log_file),
        ],
        capture_output=True,
        text=True,
    )
    assert result1.returncode == 0, result1.stderr
    assert len(_read_csv(output_csv1)) == 0

    # Key on Amount: input Amounts differ from existing -> 2 output rows
    output_csv2 = tmp_path / "output2.csv"
    result2 = subprocess.run(
        [
            sys.executable,
            SCRIPT,
            "--input-files",
            str(input_csv),
            "--input-format",
            "Date,Amount,Description",
            "--output-format",
            "Date,Amount,Description",
            "--key-columns",
            "Amount",
            "--existing-csv",
            str(existing_csv),
            "--output",
            str(output_csv2),
            "--log-file",
            str(log_file),
        ],
        capture_output=True,
        text=True,
    )
    assert result2.returncode == 0, result2.stderr
    assert len(_read_csv(output_csv2)) == 2


# ---------------------------------------------------------------------------
# --input-files repeated flag
# ---------------------------------------------------------------------------


def test_main_input_files_multi_flag(tmp_path):
    """--input-files can be specified multiple times; rows from all files appear."""
    input_a = tmp_path / "a.csv"
    input_b = tmp_path / "b.csv"
    output_csv = tmp_path / "output.csv"
    log_file = tmp_path / "test.log"

    _write_csv(
        input_a,
        COLS,
        [{"Date": "2026-01-01", "Amount": "10.00", "Description": "Alpha"}],
    )
    _write_csv(
        input_b,
        COLS,
        [{"Date": "2026-01-02", "Amount": "20.00", "Description": "Beta"}],
    )

    result = subprocess.run(
        [
            sys.executable,
            SCRIPT,
            "--input-files",
            str(input_a),
            "--input-files",
            str(input_b),
            "--input-format",
            "Date,Amount,Description",
            "--output-format",
            "Date,Amount,Description",
            "--output",
            str(output_csv),
            "--log-file",
            str(log_file),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    rows = _read_csv(output_csv)
    assert len(rows) == 2
    dates = {r["Date"] for r in rows}
    assert "2026-01-01" in dates
    assert "2026-01-02" in dates


# ---------------------------------------------------------------------------
# --dry-run flag
# ---------------------------------------------------------------------------


def test_main_dry_run_gsheets_no_write(tmp_path):
    """--dry-run with sheet args skips all GSheets calls entirely."""
    input_csv = tmp_path / "input.csv"
    log_file = tmp_path / "test.log"
    creds_file = tmp_path / "creds.json"
    creds_file.write_text("{}")

    _write_csv(
        input_csv,
        COLS,
        [{"Date": "2026-04-01", "Amount": "15.00", "Description": "Dry"}],
    )

    mock_gspread, mock_creds_module, mock_cred_cls, mock_worksheet = (
        _make_gsheets_mocks()
    )

    with mock.patch.dict(
        sys.modules,
        {
            "gspread": mock_gspread,
            "google.oauth2.service_account": mock_creds_module,
        },
    ):
        with mock.patch("csvimport.gspread", mock_gspread), mock.patch(
            "csvimport.Credentials", mock_cred_cls
        ):
            _call_main(
                [
                    "--input-files",
                    str(input_csv),
                    "--input-format",
                    "Date,Amount,Description",
                    "--output-format",
                    "Date,Amount,Description",
                    "--existing-sheet-id",
                    "fake-sheet-id",
                    "--sheet-name",
                    "Transactions",
                    "--google-creds",
                    str(creds_file),
                    "--log-file",
                    str(log_file),
                    "--dry-run",
                ]
            )

    mock_gspread.authorize.assert_not_called()
    mock_gspread.authorize.return_value.open_by_key.assert_not_called()
    mock_worksheet.insert_rows.assert_not_called()
    mock_worksheet.sort.assert_not_called()


def test_main_dry_run_skips_output(tmp_path):
    """--dry-run prints rows that would be inserted but does not write output."""
    input_csv = tmp_path / "input.csv"
    output_csv = tmp_path / "output.csv"
    log_file = tmp_path / "test.log"

    _write_csv(
        input_csv,
        COLS,
        [
            {"Date": "2026-03-01", "Amount": "10.00", "Description": "Alpha"},
            {"Date": "2026-03-02", "Amount": "20.00", "Description": "Beta"},
        ],
    )

    result = subprocess.run(
        [
            sys.executable,
            SCRIPT,
            "--input-files",
            str(input_csv),
            "--input-format",
            "Date,Amount,Description",
            "--output-format",
            "Date,Amount,Description",
            "--output",
            str(output_csv),
            "--dry-run",
            "--log-file",
            str(log_file),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    # Output file should not be created because dry-run skips the write path
    assert not output_csv.exists()
    # stdout should mention the row count
    assert "2 row(s) would be written to" in result.stdout


# ---------------------------------------------------------------------------
# Shared helpers for GSheets unit tests (items 10 and 11)
# ---------------------------------------------------------------------------


def _make_gsheets_mocks():
    """Return (mock_gspread, mock_creds_module, mock_cred_cls, mock_worksheet)."""
    mock_worksheet = mock.MagicMock()
    mock_sh = mock.MagicMock()
    mock_sh.worksheet.return_value = mock_worksheet
    mock_gc = mock.MagicMock()
    mock_gc.open_by_key.return_value = mock_sh
    mock_gspread = mock.MagicMock()
    mock_gspread.authorize.return_value = mock_gc
    mock_cred_cls = mock.MagicMock()
    mock_creds_module = mock.MagicMock()
    mock_creds_module.Credentials = mock_cred_cls
    return mock_gspread, mock_creds_module, mock_cred_cls, mock_worksheet


def _call_main(argv):
    """Invoke csvimport.main() with the given argv."""
    with mock.patch.object(sys, "argv", ["csvimport.py"] + argv):
        csvimport.main()


# ---------------------------------------------------------------------------
# Item 10: main() GSheets write/sort path
# ---------------------------------------------------------------------------


def test_main_gsheets_write_inserts_and_sorts(tmp_path):
    """Rows are inserted into the sheet and sort is called."""
    input_csv = tmp_path / "input.csv"
    log_file = tmp_path / "test.log"
    creds_file = tmp_path / "creds.json"
    creds_file.write_text("{}")

    _write_csv(
        input_csv,
        COLS,
        [{"Date": "2026-03-10", "Amount": "5.00", "Description": "Tea"}],
    )

    mock_gspread, mock_creds_module, mock_cred_cls, mock_worksheet = (
        _make_gsheets_mocks()
    )

    with mock.patch.dict(
        sys.modules,
        {
            "gspread": mock_gspread,
            "google.oauth2.service_account": mock_creds_module,
        },
    ):
        with mock.patch("csvimport.gspread", mock_gspread), mock.patch(
            "csvimport.Credentials", mock_cred_cls
        ):
            _call_main(
                [
                    "--input-files",
                    str(input_csv),
                    "--input-format",
                    "Date,Amount,Description",
                    "--output-format",
                    "Date,Amount,Description",
                    "--existing-sheet-id",
                    "fake-sheet-id",
                    "--sheet-name",
                    "Transactions",
                    "--google-creds",
                    str(creds_file),
                    "--log-file",
                    str(log_file),
                ]
            )

    mock_worksheet.insert_rows.assert_called_once()
    inserted = mock_worksheet.insert_rows.call_args[0][0]
    assert inserted == [["2026-03-10", "5.00", "Tea"]]
    mock_worksheet.sort.assert_called_once_with((1, "des"))


def test_main_gsheets_no_new_rows_skips_insert(tmp_path):
    """When all rows are deduplicated away, insert_rows is not called."""
    input_csv = tmp_path / "input.csv"
    log_file = tmp_path / "test.log"
    creds_file = tmp_path / "creds.json"
    creds_file.write_text("{}")

    _write_csv(
        input_csv,
        COLS,
        [{"Date": "2026-03-10", "Amount": "5.00", "Description": "Tea"}],
    )

    mock_gspread, mock_creds_module, mock_cred_cls, mock_worksheet = (
        _make_gsheets_mocks()
    )
    # fetch_sheet_entries returns the same row -> dedup removes it
    mock_worksheet.get_all_records.return_value = [
        {"Date": "2026-03-10", "Amount": "5.00", "Description": "Tea"}
    ]

    with mock.patch.dict(
        sys.modules,
        {
            "gspread": mock_gspread,
            "google.oauth2.service_account": mock_creds_module,
        },
    ):
        with mock.patch("csvimport.gspread", mock_gspread), mock.patch(
            "csvimport.Credentials", mock_cred_cls
        ):
            _call_main(
                [
                    "--input-files",
                    str(input_csv),
                    "--input-format",
                    "Date,Amount,Description",
                    "--output-format",
                    "Date,Amount,Description",
                    "--existing-sheet-id",
                    "fake-sheet-id",
                    "--sheet-name",
                    "Transactions",
                    "--google-creds",
                    str(creds_file),
                    "--key-columns",
                    "Date,Amount",
                    "--log-file",
                    str(log_file),
                ]
            )

    mock_worksheet.insert_rows.assert_not_called()
    mock_worksheet.sort.assert_called_once_with((1, "des"))


# ---------------------------------------------------------------------------
# Item 11: exit codes 3 and 4
# ---------------------------------------------------------------------------


def test_main_exit_code_3_sheet_fetch_failure(tmp_path):
    """Exit code 3 when fetch_sheet_entries raises (bad/missing creds file)."""
    input_csv = tmp_path / "input.csv"
    log_file = tmp_path / "test.log"
    creds_file = tmp_path / "missing_creds.json"  # intentionally absent

    _write_csv(
        input_csv,
        COLS,
        [{"Date": "2026-04-01", "Amount": "1.00", "Description": "Z"}],
    )

    result = subprocess.run(
        [
            sys.executable,
            SCRIPT,
            "--input-files",
            str(input_csv),
            "--input-format",
            "Date,Amount,Description",
            "--output-format",
            "Date,Amount,Description",
            "--key-columns",
            "Date",
            "--existing-sheet-id",
            "fake-sheet-id",
            "--sheet-name",
            "Sheet1",
            "--google-creds",
            str(creds_file),
            "--log-file",
            str(log_file),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 3


def test_main_exit_code_4_sheet_write_failure(tmp_path):
    """Exit code 4 when the GSheets write step raises an exception."""
    input_csv = tmp_path / "input.csv"
    log_file = tmp_path / "test.log"
    creds_file = tmp_path / "creds.json"
    creds_file.write_text("{}")

    _write_csv(
        input_csv,
        COLS,
        [{"Date": "2026-04-02", "Amount": "2.00", "Description": "W"}],
    )

    mock_gspread, mock_creds_module, mock_cred_cls, mock_worksheet = (
        _make_gsheets_mocks()
    )
    mock_worksheet.insert_rows.side_effect = Exception("write failed")

    with mock.patch.dict(
        sys.modules,
        {
            "gspread": mock_gspread,
            "google.oauth2.service_account": mock_creds_module,
        },
    ):
        with mock.patch("csvimport.gspread", mock_gspread), mock.patch(
            "csvimport.Credentials", mock_cred_cls
        ):
            with pytest.raises(SystemExit) as exc_info:
                _call_main(
                    [
                        "--input-files",
                        str(input_csv),
                        "--input-format",
                        "Date,Amount,Description",
                        "--output-format",
                        "Date,Amount,Description",
                        "--existing-sheet-id",
                        "fake-sheet-id",
                        "--sheet-name",
                        "Transactions",
                        "--google-creds",
                        str(creds_file),
                        "--log-file",
                        str(log_file),
                    ]
                )

    assert exc_info.value.code == 4
