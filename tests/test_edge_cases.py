import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import pytest
from csvimport import parse_format, remove_duplicates

def test_parse_format_empty():
    assert parse_format("") is None

def test_parse_format_invalid_yaml():
    with pytest.raises(Exception):
        parse_format("[A, B, C")  # missing closing bracket

def test_remove_duplicates_no_keys():
    rows = [{"A": "1"}, {"A": "2"}]
    existing = []
    key_columns = []
    class DummyLogger:
        def debug(self, msg): pass
        def info(self, msg): pass
    deduped = remove_duplicates(rows, existing, key_columns, DummyLogger())
    assert deduped == rows

def test_remove_duplicates_all_duplicates():
    rows = [{"A": "1"}, {"A": "1"}]
    existing = [{"A": "1"}]
    key_columns = ["A"]
    class DummyLogger:
        def debug(self, msg): pass
        def info(self, msg): pass
    deduped = remove_duplicates(rows, existing, key_columns, DummyLogger())
    assert deduped == []
