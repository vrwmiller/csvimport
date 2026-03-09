# Lint Agent

## Purpose
Audit Python and YAML files in this repo for lint and formatting violations, report findings, and fix them.

## Tools
- `black` — Python code formatter
- `flake8` — Python linter
- Terminal for running commands and reading output
- File editing tools for applying fixes

## Workflow

### 1. Run the linters
```bash
black --check csvimport.py tests/
flake8 csvimport.py tests/
```

Report each violation grouped by file with line numbers and a brief description.

### 2. Fix Python issues
- Run `black csvimport.py tests/` to auto-format.
- For flake8 violations that black cannot fix (e.g., unused imports, bare `except`, line logic), edit the file directly and re-run `flake8` to confirm zero violations.

### 3. Fix YAML issues
For each `.github/workflows/*.yml` file in the repo:
- Check indentation (must be 2 spaces, no tabs).
- Confirm all jobs and steps have a `name:`.
- Confirm third-party actions are pinned to a version tag (not `@main` or `@latest`).
- Confirm no literal secrets or credentials appear in `env:` blocks.
- Report any issues found with file path and line number.

### 4. Confirm clean
After fixes, re-run:
```bash
black --check csvimport.py tests/
flake8 csvimport.py tests/
```
Report "All clean" when both commands exit 0.

## Scope
- Python: `csvimport.py`, `tests/`
- YAML: `.github/workflows/`
- Do not modify `confs/`, `backups/`, `docs/`, or `logs/`.

## Rules
- Never suppress a flake8 rule with `# noqa` unless the violation is a deliberate, documented exception.
- Never widen line length beyond 88.
- Never reorder or restructure logic while fixing lint — only minimal changes needed to resolve the violation.
