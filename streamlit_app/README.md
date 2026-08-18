# SemanticOps Streamlit Console

This Streamlit app provides a lightweight operations console for the running SemanticOps backend.

## Run

Start the platform services first:

```bash
docker compose up -d --build
```

Install Streamlit dependencies:

```bash
python -m pip install -r streamlit_app/requirements.txt
```

Run the app:

```bash
streamlit run streamlit_app/app.py
```

The app expects the API at `http://localhost:8000` by default. Override it with:

```bash
$env:SEMANTICOPS_API_URL="http://localhost:8000"
streamlit run streamlit_app/app.py
```

## Workspaces

- Status: backend health, validation report count, and graph inventory.
- Ingestion Workflows: run built-in dataset workflows and inspect persisted step history.
- Graph View: animated draggable visualization of classes, resources, properties, and literal data.
- Validate RDF: run Turtle plus SHACL validation through FastAPI.
- Graph Store: promote approved Turtle and inspect named graphs.
- Medical Datasets: load the synthetic and UCI Heart Disease RDF graphs.
- SPARQL: run ad hoc graph queries.
