---
applyTo: "docs/**"
---

# Docs Agent Instructions

## Source of truth
- CLI behavior and orchestration: `csvimport.py`
- Config schema: `confs/csvimport.conf.sample`
- Functional behavior and edge cases: tests under `tests/`

## Documentation style
- Keep docs concrete and task-oriented.
- Use fenced code blocks with language tags (`bash`, `yaml`, `csv`).
- Use placeholders for sensitive values (`<sheet_id>`, `<path/to/creds.json>`).
- Keep command examples copy-paste safe.

## Required sync points
When these change, update docs:
- CLI flags or defaults in `main()`
- Config keys/shape in sample config
- Dedup rules / key-field behavior
- Debit/Credit split behavior in `transform_csv`
- Upload workflow (insert at row 2, sort column A descending)

## Quality checks
- Ensure docs match current defaults and exit codes.
- Ensure docs never imply live API calls in tests.
- Ensure examples do not include real local paths or IDs.
