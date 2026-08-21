# API Specification

The FastAPI application publishes OpenAPI documentation at `/docs`.

Initial endpoints:

- `GET /api/v1/health`: service health.
- `POST /api/v1/knowledge-graphs/validate`: validate Turtle data against Turtle SHACL shapes.
- `GET /api/v1/knowledge-graphs/validation-reports`: list recent persisted validation reports.
- `GET /api/v1/knowledge-graphs/ontology/modules`: inspect the current ontology source modules.
- `GET /api/v1/knowledge-graphs/ontology/versions`: list immutable ontology snapshots and checksums.
- `PUT /api/v1/knowledge-graphs/graphs`: promote approved Turtle into a named graph.
- `GET /api/v1/knowledge-graphs/graphs`: list named graphs currently stored in Fuseki.
- `POST /api/v1/knowledge-graphs/query`: execute a SPARQL query against Fuseki.
- `GET /api/v1/workflows/ingestion/datasets`: list built-in ingestible datasets.
- `POST /api/v1/workflows/ingestion/runs`: run ingest, validate, promote, and query-ready steps.
- `GET /api/v1/workflows/ingestion/runs`: list recent workflow runs.

Future API modules should cover audit logs and user approvals.
