import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import pytest
from unittest.mock import patch, MagicMock
from csvimport import fetch_sheet_entries

def test_fetch_sheet_entries_mock():
    # Patch gspread and Credentials
    with patch('csvimport.gspread') as gspread_mock, \
         patch('csvimport.Credentials') as creds_mock:
        creds_instance = MagicMock()
        creds_mock.from_service_account_file.return_value = creds_instance
        client_mock = MagicMock()
        gspread_mock.authorize.return_value = client_mock
        sheet_mock = MagicMock()
        client_mock.open_by_key.return_value = sheet_mock
        worksheet_mock = MagicMock()
        sheet_mock.worksheet.return_value = worksheet_mock
        worksheet_mock.get_all_records.return_value = [
            {"A": "1", "B": "x"},
            {"A": "2", "B": "y"}
        ]
        class DummyLogger:
            handlers = []
            def info(self, msg): pass
            def error(self, msg): pass
            def debug(self, msg): pass
        result = fetch_sheet_entries("sheetid", "sheetname", "creds.json", DummyLogger())
        assert result == [{"A": "1", "B": "x"}, {"A": "2", "B": "y"}]
