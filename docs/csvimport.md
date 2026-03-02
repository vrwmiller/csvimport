# csvimport Documentation

## Overview

`csvimport.py` is a robust, configurable tool for importing, transforming, deduplicating, and uploading CSV data to a target data store (such as Google Sheets). It supports organization-specific formats, multi-file input, backup/DR, and advanced mapping features.

## Features

- Organization-specific input/output formats via config file
- Multi-file CSV merging
- Deduplication against existing records

- Category field mapping (planned)
- Logging and error handling
- Testable with pytest

## Usage

### Command Line Options

```
python csvimport.py --input-files <csv1,csv2,...> --org <org> [--config <config>] [--output <output.csv>] [--dry-run]
```

- `--input-files`: Comma-separated list of CSV files to merge and process
- `--org`: Organization name for config lookup
- `--config`: Path to config file (default: confs/csvimport.conf)
- `--output`: Optional output CSV file
- `--dry-run`: Preview changes without modifying the target data store

## Configuration

The config file (`confs/csvimport.conf`) defines formats, rules, and Google Sheets settings per organization. Example:

```yaml
organizations:
  thebank:
    input_format: ["Transaction Date", "Post Date", "Description", "Category", "Type", "Amount", "Memo"]
    output_format: ["Transaction Date", "Post Date", "Description", "Category", "Type", "Amount", "Memo"]
    key_fields: ["Description", "Amount", "Transaction Date", "Post Date"]
    sheet_name: "sheet1"
    extra_columns: ["", "", "2025"]
  anotherbank:
    input_format: ["Posting Date", "Transaction Date", "Amount", "Credit Debit Indicator", "type", "Type Group", "Reference", "Instructed Currency", "Currency Exchange Rate", "Instructed Amount", "Description", "Category", "Check Serial Number", "Card Ending"]
    output_format: ["Posting Date", "Check Serial Number", "Description", "Debit", "Credit", "Category", "Amount", "Credit Debit Indicator", "type", "Type Group", "Reference", "Instructed Currency", "Currency Exchange Rate", "Instructed Amount", "Card Ending"]
    key_fields: ["Description", "Instructed Amount", "Check Serial Number", "Posting Date"]
    sheet_name: "sheet1"
google:
  creds: 'confs/google.json'
  sheet_id: 'sheet_id'
```

**Field explanations:**

- `input_format` / `output_format`: List of columns for import/export
- `key_fields`: Used for deduplication
- `sheet_name`: Target sheet name for each organization
- `extra_columns`: Optional, for additional columns
- `category_map`: (planned) Maps imported category values to desired values
- `google.creds`: Path to Google API credentials JSON
- `google.sheet_id`: Target Google Sheet ID

## Workflow

```mermaid
flowchart TD
  A[Download CSV files] --> B[Merge input files]
  B --> C{Do formats match?}
  C -- Yes --> D[Skip transformation]
  C -- No --> E[Transform merged CSVs]
  D --> F[Backup current target]
  E --> F[Backup current target]
  F --> G[Deduplicate against existing records]
  G --> H[Import to target]
```

## Testing

- Tests are located in `tests/`
- Run with `pytest`
- Coverage reporting with `pytest-cov` (optional)

## Planned Features

- Dry-run option
- Organization-specific category mapping

## Mermaid Workflow Diagram

See `docs/csvimport.md` for a visual workflow.

## Authors & Contributors

- Vincent Miller
- ...

## License

MIT

## Changelog

- See PRs and commit history for details.
