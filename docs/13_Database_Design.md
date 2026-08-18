# Database Design

PostgreSQL stores operational data that does not belong directly in the RDF graph store.

Candidate tables:

- `workflow_runs`
- `agent_steps`
- `graph_assets`
- `ontology_versions`
- `validation_reports`
- `audit_events`
- `user_approvals`

All operational records should carry timestamps, actor identity where available, and correlation IDs.

