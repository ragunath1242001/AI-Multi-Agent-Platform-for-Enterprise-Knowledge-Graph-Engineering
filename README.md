# SemanticOps

SemanticOps is a production-oriented monorepo for an AI-powered multi-agent platform for enterprise knowledge graph engineering.

## Modules

- `frontend/`: Next.js TypeScript web application.
- `backend/`: FastAPI API using clean architecture boundaries.
- `agents/`: LangGraph-based orchestration package.
- `kg/`: OWL ontologies, SHACL shapes, and sample RDF.
- `streamlit_app/`: Streamlit operations console for validation, graph visualization, graph promotion, and SPARQL.
- `docker/`: Runtime service configuration.
- `docs/`: Architecture and engineering documentation.
- `tests/`: Cross-service integration tests.

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

Services:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs
- Fuseki: http://localhost:3030
- PostgreSQL: localhost:5432

## Streamlit Console

```bash
python -m pip install -r streamlit_app/requirements.txt
streamlit run streamlit_app/app.py
```

By default, the console uses the backend at `http://localhost:8000`.
