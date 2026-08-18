# SHACL Validation

SHACL validation uses pySHACL in the API and agent workflows. Validation must produce machine-readable reports for automation and human-readable summaries for review.

Validation policy should distinguish:

- Blocking production violations.
- Warnings that require review.
- Informational quality checks.
- Regression checks against previous graph releases.

