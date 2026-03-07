---
applyTo: "tests/**"
---

# Test Agent Instructions

## Project testing conventions
- Test framework: `pytest`
- Existing suites:
  - `tests/test_csvimport.py`
  - `tests/test_edge_cases.py`
  - `tests/test_gsheets_mock.py`
  - `tests/test_main_integration.py`
  - `tests/test_transform_csv.py`
  - `tests/test_utils.py`

## Rules
- Every changed function in `csvimport.py` should have updated or added test coverage.
- Keep Google Sheets interactions mocked; never hit real APIs.
- Use `unittest.mock.patch` for `csvimport.gspread` and `csvimport.Credentials`.
- Integration-style CLI tests should use `tmp_path` and `subprocess.run`.
- Use deterministic test data and assert both success and failure paths.

## What to test for new behavior
- Happy path behavior for transformed/deduped output.
- Error handling and exit codes from `main()`.
- Format resolution precedence (CLI override vs config).
- Column mismatch and missing-field failures.
- Edge cases: empty inputs, duplicate keys, malformed rows.

## Fast verification commands
```bash
pytest -q
black --check csvimport.py tests/
flake8 csvimport.py tests/
```
