---
applyTo: "**"
---

# Pull Request Agent Instructions

## Branch rules
- Never commit directly to `main`.
- Create a focused branch for each change: `feature/<topic>`, `fix/<topic>`, `test/<topic>`, `setup/<topic>`, `docs/<topic>`.
- Open a PR into `main`.

## PR title format
Use concise conventional prefixes:
```
feature: short description
fix: short description
test: short description
setup: short description
docs: short description
```

## PR description structure

### For small changes
Include:
- What changed
- Why it changed
- Validation performed

### For larger changes
Use this template:
```
## Summary
Short explanation of the change.

## Changes
- File-by-file list of key edits.

## Motivation
Why this was needed.

## Testing
- `pytest -q`
- `black --check csvimport.py tests/`
- `flake8 csvimport.py tests/`

## Risk
Possible regressions and mitigation.

## Breaking Changes
List CLI/config changes; if none, state "None".
```

## Referencing issues
- Use `Closes #N` for complete fixes.
- Use `Related to #N` for partial or supporting work.

## Checklist before opening
- [ ] Branch is not `main`
- [ ] Tests pass (`pytest -q`)
- [ ] Formatting/lint pass (`black --check ...` and `flake8 ...`)
- [ ] No real credentials, sheet IDs, or sensitive local paths leaked in docs or examples
- [ ] Any config schema changes are reflected in `confs/csvimport.conf.sample`

## Using gh CLI body files
For multi-line issue/PR content, always use `--body-file`.

Correct approach:
1. Write body content to a temp file (for example `/tmp/pr-body.txt`) using file tools.
2. Pass the file to `gh`:
```bash
gh pr create --title "setup: integrate copilot instruction files" --body-file /tmp/pr-body.txt --base main
gh pr edit <number> --body-file /tmp/pr-body.txt
gh issue create --title "..." --body-file /tmp/issue-body.txt
```
3. Delete the temp file after command success.
