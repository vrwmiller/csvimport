# csvimport

A robust, configurable CLI tool for importing, transforming, deduplicating, and uploading CSV data to Google Sheets.

## Features

- Organization-specific input/output formats via config file
- Multi-file CSV merging
- Deduplication against existing records
- Google Sheets integration
- Automated backup before import
- Logging and clear error messages
- Testable with pytest

## Requirements

```sh
pip install -r requirements.txt
```

## Setup

1. Copy `confs/csvimport.conf.sample` to `confs/csvimport.conf` and fill in your organization settings and Google Sheets credentials.
2. Place your Google API service account JSON in `confs/`.

## Usage

```sh
python csvimport.py --input-files <csv1,csv2,...> --org <org> [--config <config>] [--output <output.csv>] [--dry-run]
```

**Options:**
- `--input-files`: Comma-separated list of CSV files to merge and process
- `--org`: Organization name for config lookup
- `--config`: Path to config file (default: `confs/csvimport.conf`)
- `--output`: Optional output CSV file
- `--dry-run`: Preview changes without modifying the target data store

## Running Tests

```sh
pytest tests/
```

## Documentation

See [docs/csvimport.md](docs/csvimport.md) for full documentation including workflow diagram and configuration reference.

## License

MIT
