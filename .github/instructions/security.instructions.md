---
applyTo: "csvimport.py"
---

# Security Agent Instructions

## Non-negotiable rules
1. Never hard-code Google credentials paths, service account JSON, sheet IDs, or user data in code.
2. Never log secrets or sensitive values from rows/records; log counts and error types instead.
3. All Google Sheets interactions in tests must be mocked (`gspread` and `Credentials`).
4. Keep backup behavior local-only and deterministic; do not upload backups or expose contents in logs.
5. Avoid broad exception handling that hides failure causes during upload/dedup operations.

## What to flag in review
- Any new credential literal (paths, tokens, IDs) in committed files.
- Any `print`/logger statement that can leak full row contents.
- Any direct network calls in tests that should be mocked.
- Any config parsing change that can silently default to unsafe behavior.
- Any new write/sort behavior to Google Sheets without clear error handling and exit code mapping.

## Preferred patterns
- Use environment/config inputs for credentials and sheet metadata.
- Preserve existing exit-code behavior (`2`, `3`, `4`) for failure categories.
- Validate expected columns before transform/write operations.
