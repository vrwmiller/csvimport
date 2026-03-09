---
applyTo: "**/*.{py,yml,yaml}"
---

# Lint Instructions

## Python (`*.py`)
- Formatter: **black**, line length 88 (default). All code must be black-clean.
- Linter: **flake8**. Zero violations permitted before committing.
- Type hints are required on all function signatures; do not remove or omit them.
- Use the named logger (`logging.getLogger("csvimport")`), never bare `print`, for non-CLI output.
- No bare `except:`; always catch a specific exception type.
- Imports must be ordered: stdlib → third-party → local, with a blank line between groups.

## YAML (`.yml` / `.yaml`)
- Indent with 2 spaces; never use tabs.
- Quote string values that contain colons, special characters, or template expressions (`${{ }}`).
- Every GitHub Actions workflow must have a `name:` at the top level.
- Every job must have an explicit `runs-on:`. A `name:` on jobs and steps is preferred but not required for simple single-step jobs.
- Pin third-party actions to a specific version tag (e.g., `@v4`, `@v6.2`), not `@main` or `@latest`.
- Action `with:` keys must match the input names documented in the action's `action.yml`/`action.yaml` metadata file. Invalid input keys are silently ignored at runtime and will not produce an error — verify spelling against the action's source or docs.
- Avoid redundant `true`/`false` string values where a boolean is expected.
- Keep `on:` trigger blocks at the top of the file, directly after `name:`.

## What to flag
- Python lines exceeding 88 characters.
- f-strings that concatenate where a format string would be cleaner.
- YAML keys that duplicate or shadow an earlier key in the same mapping.
- Actions steps missing a `name:`.
- Action `with:` blocks that use an input key not present in the action's documented inputs (these keys are silently ignored at runtime and will not cause an error).
- Workflow `env:` blocks that contain literal secrets or credentials.

## Fast verification commands
```bash
black --check csvimport.py tests/
flake8 csvimport.py tests/
```
