# SemanticOps Rollout

Last updated: 2026-07-27

## Current State

SemanticOps is a knowledge-graph engineering platform for validating, storing, querying, visualizing, and ingesting RDF datasets.

The stack runs with Docker Compose:

- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs
- Streamlit console: http://localhost:8501
- Fuseki: http://localhost:3030
- PostgreSQL: localhost:5432

Fuseki local credentials:

- Username: `admin`
- Password: `semanticops`

## Implemented

### Platform Foundation

- Monorepo structure with `frontend`, `backend`, `agents`, `kg`, `streamlit_app`, `docs`, and `tests`.
- Docker Compose stack for frontend, backend, PostgreSQL, and Fuseki.
- Backend database initialization for persisted records.
- Local Streamlit console for operations workflows.

### RDF Validation

- `POST /api/v1/knowledge-graphs/validate`
- `GET /api/v1/knowledge-graphs/validation-reports`
- SHACL validation through `pyshacl`.
- Validation reports persisted in PostgreSQL.

### Graph Store

- Fuseki graph-store adapter.
- `PUT /api/v1/knowledge-graphs/graphs`
- `GET /api/v1/knowledge-graphs/graphs`
- `POST /api/v1/knowledge-graphs/query`
- Named graph promotion and SPARQL query support.

### Medical Data

- Synthetic medical cohort RDF graph.
- UCI Heart Disease Cleveland dataset downloaded and converted to RDF.
- Shared medical ontology:
  - `kg/ontologies/semanticops-medical.ttl`
- Medical SHACL constraints:
  - `kg/shapes/semanticops-medical.shacl.ttl`
- Medical ontology promoted to Fuseki as:
  - `https://semanticops.ai/graphs/semanticops-medical-ontology`

Current key named graphs:

- `customer-risk-controls`
- `synthetic-medical-cohort`
- `uci-heart-disease-cleveland`
- `semanticops-medical-ontology`

### Streamlit Console

The Streamlit app supports:

- Backend status and graph inventory.
- Ingestion workflow execution and persisted run history.
- Animated draggable graph visualization.
- RDF + SHACL validation.
- Graph promotion.
- Medical dataset loading.
- SPARQL querying.

Run it with:

```powershell
.\.venv\Scripts\python -m streamlit run streamlit_app\app.py
```

### Ingestion Workflows

Backend workflow API:

- `GET /api/v1/workflows/ingestion/datasets`
- `POST /api/v1/workflows/ingestion/runs`
- `GET /api/v1/workflows/ingestion/runs`

Workflow steps:

- `ingest`
- `validate`
- `promote`
- `query_ready`

Workflow runs are persisted in PostgreSQL.

Latest verified live run:

- Dataset: `synthetic-medical-cohort`
- Status: `completed`
- Run ID: `98538051-43d8-4c11-8729-3ab5e050a002`
- Validation report ID: `2a9c4466-3f97-46bc-a71b-cc41e818860f`
- Promoted triples: `115`

## Verification Status

Last verified:

- Backend Ruff: passed.
- Backend tests: `4 passed`.
- Streamlit app compile: passed.
- Docker Compose rebuild/start: passed.
- Live ingestion workflow run: passed.

Known warning:

- FastAPI test client emits a Starlette deprecation warning about `httpx`; tests still pass.

## Next Steps

### 1. Add Workflow Run Details Page To Next.js

Currently Streamlit has workflow visibility, but the Next.js frontend does not.

Build:

- Workflow dataset selector.
- Run ingestion button.
- Recent workflow run list.
- Step timeline for ingest, validate, promote, query-ready.
- Links to validation report and named graph.

### 2. Connect LangGraph Agents To Ingestion

The `agents` package currently has placeholder nodes.

Upgrade it so ingestion can optionally run through LangGraph:

- Ontology review node.
- RDF preparation node.
- SHACL validation node.
- Promotion decision node.
- Post-ingestion observation node.

### 3. Add Ontology Versioning

Add persistence and API support for ontology versions:

- Store ontology graph name, version, checksum, created time.
- Promote ontology versions as immutable named graphs.
- Link dataset ingestion runs to the ontology version used during validation.

### 4. Add Graph Lineage

Track where each graph came from:

- Source file or URL.
- Conversion step.
- Validation report.
- Workflow run.
- Promotion timestamp.
- Ontology/shapes version.

### 5. Improve Graph Visualization

Current Streamlit graph visualization is useful but basic.

Improve:

- Filters by class, property, and graph.
- Class/property legend.
- Node details side panel.
- Expand-neighborhood interaction.
- Save selected SPARQL query.

### 6. Add Real Dataset Import Pipeline

The UCI dataset was manually downloaded and converted.

Add repeatable import support:

- Source URL registry.
- Download step.
- Raw data checksum.
- CSV/data parser.
- RDF converter.
- Validation and promotion as one workflow.

### 7. Add CI

Add GitHub Actions or equivalent:

- Backend Ruff.
- Backend tests.
- Agent tests.
- Frontend lint/build.
- RDF parse validation for `kg/**/*.ttl`.
- SHACL validation smoke tests.

## Useful Commands

Start the full stack:

```powershell
docker compose up -d --build
```

Run backend checks:

```powershell
cd backend
..\.venv\Scripts\python -m ruff check .
..\.venv\Scripts\python -m pytest
```

Run Streamlit:

```powershell
.\.venv\Scripts\python -m streamlit run streamlit_app\app.py
```

List ingestion datasets:

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/workflows/ingestion/datasets
```

Run ingestion:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/api/v1/workflows/ingestion/runs `
  -ContentType 'application/json' `
  -Body (@{ dataset_key = 'synthetic-medical-cohort' } | ConvertTo-Json)
```
