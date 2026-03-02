# Copilot Instructions for csvimport

## What this tool does

`csvimport.py` is a CLI tool that merges, transforms, deduplicates, and uploads CSV data to Google Sheets. It is used regularly in production. Changes should be made carefully with test coverage as a priority.

Core capabilities:
- Merges multiple CSV input files
- Transforms columns between `input_format` and `output_format`
- Deduplicates against existing records (from a CSV or a live Google Sheet)
- Uploads deduplicated rows to a Google Sheet (inserts at row 2, sorts column A descending)
- Backs up the target Google Sheet to a local CSV before any upload

## Repository structure

```
csvimport.py          # Main tool — all logic lives here
confs/
  csvimport.conf          # Real config (gitignored)
  csvimport.conf.sample   # Template — keep this up to date
tests/
  test_csvimport.py       # Core functional + integration tests
  test_edge_cases.py      # Boundary/edge case tests
  test_gsheets_mock.py    # Mocked Google Sheets tests
docs/
  csvimport.md            # Full documentation
requirements.txt
```

## Branch and PR workflow

- **Never commit directly to `main`.**
- All changes go through a Pull Request.
- Branch naming convention: `type/short-description`
  - `feature/` — new functionality
  - `fix/` — bug fixes
  - `test/` — adding or improving tests
  - `setup/` — repo config, CI, tooling
  - `docs/` — documentation only
- CI must pass (lint + tests) before a PR can be merged.
- Keep PRs focused. One logical change per PR.
- Use the `gh` CLI for all git operations (branch creation, push, PR creation). Do not use GitKraken or other MCP-based git tools.

## Code style

- Formatter: **black** (line length default, 88 chars)
- Linter: **flake8**
- Run before committing: `black csvimport.py tests/ && flake8 csvimport.py tests/`
- Type hints are used in function signatures — keep them.
- Logging uses a named logger (`logging.getLogger("csvimport")`), not print statements, except for user-facing CLI output.

## Testing expectations

- Every function that is added or modified must have a corresponding test update.
- Tests live in `tests/`. Add new test files if a new logical area is introduced.
- Tests that need a logger use a local `DummyLogger` class inline — do not import a real logger into unit tests.
- Integration/subprocess tests use `tmp_path` (pytest fixture) and spin up the real script via `subprocess.run`. Use these for CLI-layer coverage.
- Google Sheets interactions must always be mocked — never make real API calls in tests.
- Use `unittest.mock.patch` to mock `csvimport.gspread` and `csvimport.Credentials`.

## Key functions

| Function | Purpose |
|---|---|
| `parse_format(format_str)` | Parses a comma-separated or YAML-list string into a Python list |
| `load_config(config_path)` | Loads the YAML config file; returns `{}` if no path given |
| `get_format(config, org, key, cli_format)` | Resolves format from CLI override or org config |
| `remove_duplicates(rows, existing, key_columns, logger)` | Filters rows whose key tuple already exists in `existing` |
| `fetch_sheet_entries(sheet_id, worksheet_name, creds_path, logger)` | Fetches rows from a Google Sheet; also backs it up to `backups/` |
| `transform_csv(input_path, output_path, input_format, output_format, ...)` | Maps input columns to output columns; handles Debit/Credit split |
| `setup_logging(debug, log_file)` | Configures file handler (always) + stdout handler (debug mode only) |
| `main()` | CLI entry point; orchestrates config load, format resolution, dedup, transform, upload |

## Special transform: Debit/Credit split

When `output_format` contains both `Debit` and `Credit`, and `input_format` contains both `Amount` and `Credit Debit Indicator`, `transform_csv` applies a split: the `Amount` value routes to either `Debit` or `Credit` based on the `Credit Debit Indicator` field. The other field is left empty. This is a named org-specific rule — do not generalize it without discussion.

## Config file structure

```yaml
organizations:
  orgname:
    input_format: ["col1", "col2", "col3"]
    output_format: ["col1", "col2", "col3"]
    key_fields: ["col1", "col2"]
    sheet_name: worksheet_name
    extra_columns: []          # optional: appended to each row on upload
google:
  creds: /path/to/service-account.json
  sheet_id: google_sheet_id_string
```

- `confs/csvimport.conf` is the live config and is gitignored.
- `confs/csvimport.conf.sample` is the template — update it when the schema changes.

## CLI flags summary

| Flag | Description |
|---|---|
| `--input-files` | Comma-separated CSV input paths (required) |
| `--org` | Organization key for config lookup |
| `--config` | Path to config file (default: `confs/csvimport.conf`) |
| `--output` | Output CSV path (optional, used when not uploading to Sheets) |
| `--input-format` | Input column list (overrides config) |
| `--output-format` | Output column list (overrides config) |
| `--key-columns` | Columns for dedup key (overrides config) |
| `--existing-csv` | CSV file of existing records to dedup against |
| `--existing-sheet-id` | Google Sheet ID for live dedup source |
| `--sheet-name` | Worksheet name (overrides config) |
| `--google-creds` | Path to service account JSON (overrides config) |
| `--log-file` | Log file path (default: `logs/csvimport.log`) |
| `--debug` | Enable debug logging to stdout |

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 2 | Configuration or field mismatch error |
| 3 | Google Sheets fetch failure |
| 4 | Google Sheets write/sort failure |
