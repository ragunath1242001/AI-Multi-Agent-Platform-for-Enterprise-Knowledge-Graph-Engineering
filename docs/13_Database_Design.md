# Database Design

PostgreSQL stores operational data that does not belong directly in the RDF graph store.

Implemented tables:

- `workflow_runs`
- `ontology_versions`
- `workflow_run_ontology_versions`
- `graph_lineage`
- `validation_reports`

Candidate tables:

- `agent_steps`
- `graph_assets`
- `audit_events`
- `user_approvals`

All operational records should carry timestamps, actor identity where available, and correlation IDs.
