import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
)  # noqa: E402
from csvimport import transform_csv  # noqa: E402


class DummyLogger:
    def debug(self, msg):
        pass

    def info(self, msg):
        pass


def _write_csv(path, header, rows):
    """Write a CSV file from a header list and list-of-list rows."""
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(",".join(header) + "\n")
        for row in rows:
            f.write(",".join(str(v) for v in row) + "\n")


# ---------------------------------------------------------------------------
# Basic column mapping
# ---------------------------------------------------------------------------


def test_transform_csv_passthrough(tmp_path):
    inp = tmp_path / "in.csv"
    _write_csv(inp, ["col1", "col2"], [["A", "1"], ["B", "2"]])
    result = transform_csv(str(inp), ["col1", "col2"], ["col1", "col2"])
    assert result == [{"col1": "A", "col2": "1"}, {"col1": "B", "col2": "2"}]


def test_transform_csv_column_subset(tmp_path):
    """Output format selects only a subset of input columns."""
    inp = tmp_path / "in.csv"
    _write_csv(inp, ["col1", "col2", "col3"], [["A", "1", "X"]])
    result = transform_csv(str(inp), ["col1", "col2", "col3"], ["col1", "col3"])
    assert result == [{"col1": "A", "col3": "X"}]


def test_transform_csv_missing_column_defaults_empty(tmp_path):
    """Column in output_format but absent from the row gets empty string."""
    inp = tmp_path / "in.csv"
    _write_csv(inp, ["col1"], [["A"]])
    result = transform_csv(str(inp), ["col1"], ["col1", "col2"])
    assert result == [{"col1": "A", "col2": ""}]


def test_transform_csv_empty_file(tmp_path):
    """CSV with only a header row returns an empty list."""
    inp = tmp_path / "in.csv"
    inp.write_text("col1,col2\n")
    result = transform_csv(str(inp), ["col1", "col2"], ["col1", "col2"])
    assert result == []


def test_transform_csv_utf8_bom(tmp_path):
    """Files with a UTF-8 BOM (utf-8-sig) are read correctly."""
    inp = tmp_path / "in.csv"
    with open(inp, "w", encoding="utf-8-sig", newline="") as f:
        f.write("col1,col2\nA,1\n")
    result = transform_csv(str(inp), ["col1", "col2"], ["col1", "col2"])
    assert result == [{"col1": "A", "col2": "1"}]


# ---------------------------------------------------------------------------
# Deduplication inside transform_csv
# ---------------------------------------------------------------------------


def test_transform_csv_dedup_applied(tmp_path):
    """Rows matching existing_entries are removed when key_columns and logger provided."""
    inp = tmp_path / "in.csv"
    _write_csv(inp, ["col1", "col2"], [["A", "1"], ["B", "2"]])
    existing = [{"col1": "A", "col2": "1"}]
    result = transform_csv(
        str(inp),
        ["col1", "col2"],
        ["col1", "col2"],
        existing_entries=existing,
        key_columns=["col1", "col2"],
        logger=DummyLogger(),
    )
    assert result == [{"col1": "B", "col2": "2"}]


def test_transform_csv_dedup_skipped_without_logger(tmp_path):
    """Dedup is not applied when logger is None, even if other args are provided."""
    inp = tmp_path / "in.csv"
    _write_csv(inp, ["col1", "col2"], [["A", "1"], ["B", "2"]])
    existing = [{"col1": "A", "col2": "1"}]
    result = transform_csv(
        str(inp),
        ["col1", "col2"],
        ["col1", "col2"],
        existing_entries=existing,
        key_columns=["col1", "col2"],
        logger=None,
    )
    assert len(result) == 2


# ---------------------------------------------------------------------------
# Debit / Credit split
# ---------------------------------------------------------------------------

DEBIT_CREDIT_INPUT_FORMAT = [
    "Posting Date",
    "Description",
    "Amount",
    "Credit Debit Indicator",
]
DEBIT_CREDIT_OUTPUT_FORMAT = [
    "Posting Date",
    "Description",
    "Debit",
    "Credit",
]


def test_debit_credit_split_debit_row(tmp_path):
    """A row with indicator 'Debit' puts Amount in Debit, Credit is empty."""
    inp = tmp_path / "in.csv"
    _write_csv(
        inp,
        DEBIT_CREDIT_INPUT_FORMAT,
        [["2026-01-01", "Groceries", "42.00", "Debit"]],
    )
    result = transform_csv(
        str(inp), DEBIT_CREDIT_INPUT_FORMAT, DEBIT_CREDIT_OUTPUT_FORMAT
    )
    assert len(result) == 1
    assert result[0]["Debit"] == "42.00"
    assert result[0]["Credit"] == ""
    assert result[0]["Posting Date"] == "2026-01-01"
    assert result[0]["Description"] == "Groceries"


def test_debit_credit_split_credit_row(tmp_path):
    """A row with indicator 'Credit' puts Amount in Credit, Debit is empty."""
    inp = tmp_path / "in.csv"
    _write_csv(
        inp,
        DEBIT_CREDIT_INPUT_FORMAT,
        [["2026-01-02", "Refund", "15.00", "Credit"]],
    )
    result = transform_csv(
        str(inp), DEBIT_CREDIT_INPUT_FORMAT, DEBIT_CREDIT_OUTPUT_FORMAT
    )
    assert result[0]["Debit"] == ""
    assert result[0]["Credit"] == "15.00"


def test_debit_credit_split_mixed_rows(tmp_path):
    """Multiple rows with different indicators are each split correctly."""
    inp = tmp_path / "in.csv"
    _write_csv(
        inp,
        DEBIT_CREDIT_INPUT_FORMAT,
        [
            ["2026-01-01", "Shop", "10.00", "Debit"],
            ["2026-01-02", "Refund", "5.00", "Credit"],
            ["2026-01-03", "Lunch", "8.50", "Debit"],
        ],
    )
    result = transform_csv(
        str(inp), DEBIT_CREDIT_INPUT_FORMAT, DEBIT_CREDIT_OUTPUT_FORMAT
    )
    assert result[0] == {
        "Posting Date": "2026-01-01",
        "Description": "Shop",
        "Debit": "10.00",
        "Credit": "",
    }
    assert result[1] == {
        "Posting Date": "2026-01-02",
        "Description": "Refund",
        "Debit": "",
        "Credit": "5.00",
    }
    assert result[2] == {
        "Posting Date": "2026-01-03",
        "Description": "Lunch",
        "Debit": "8.50",
        "Credit": "",
    }


def test_debit_credit_split_not_triggered_without_indicator_column(tmp_path):
    """Split logic is NOT triggered when input_format lacks 'Credit Debit Indicator'."""
    inp = tmp_path / "in.csv"
    _write_csv(inp, ["Amount", "Description"], [["50.00", "Test"]])
    # output has Debit/Credit but input doesn't have Credit Debit Indicator
    result = transform_csv(str(inp), ["Amount", "Description"], ["Debit", "Credit"])
    # Falls through to generic mapping - Debit and Credit come back empty
    assert result[0]["Debit"] == ""
    assert result[0]["Credit"] == ""
