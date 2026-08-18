from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import requests
import streamlit as st
import streamlit.components.v1 as components

ROOT_DIR = Path(__file__).resolve().parents[1]
KG_EXAMPLES_DIR = ROOT_DIR / "kg" / "examples"
DEFAULT_API_URL = os.getenv("SEMANTICOPS_API_URL", "http://localhost:8000")


def main() -> None:
    st.set_page_config(page_title="SemanticOps Console", page_icon="SO", layout="wide")
    st.title("SemanticOps Console")

    api_url = st.sidebar.text_input("API base URL", value=DEFAULT_API_URL).rstrip("/")
    st.sidebar.caption("Start the stack with `docker compose up -d --build`.")

    page = st.sidebar.radio(
        "Workspace",
        [
            "Status",
            "Ingestion Workflows",
            "Graph View",
            "Validate RDF",
            "Graph Store",
            "Medical Datasets",
            "SPARQL",
        ],
    )

    if page == "Status":
        render_status(api_url)
    elif page == "Ingestion Workflows":
        render_ingestion_workflows(api_url)
    elif page == "Graph View":
        render_graph_view(api_url)
    elif page == "Validate RDF":
        render_validation(api_url)
    elif page == "Graph Store":
        render_graph_store(api_url)
    elif page == "Medical Datasets":
        render_medical_datasets(api_url)
    else:
        render_sparql(api_url)


def render_status(api_url: str) -> None:
    st.header("Service Status")
    response = api_request("GET", api_url, "/api/v1/health")
    if response is None:
        return

    st.success(f"{response.get('service', 'semanticops-backend')} is {response.get('status', 'unknown')}")

    reports = api_request("GET", api_url, "/api/v1/knowledge-graphs/validation-reports")
    graphs = api_request("GET", api_url, "/api/v1/knowledge-graphs/graphs")

    col1, col2 = st.columns(2)
    col1.metric("Recent validation reports", len(reports or []))
    col2.metric("Named graphs", len(graphs or []))

    if graphs:
        st.subheader("Graphs")
        st.dataframe(graphs, use_container_width=True)


def render_ingestion_workflows(api_url: str) -> None:
    st.header("Ingestion Workflows")
    st.caption("Run a deterministic ingest, validate, promote, and query-ready workflow.")

    datasets = api_request("GET", api_url, "/api/v1/workflows/ingestion/datasets")
    if not datasets:
        st.info("No ingestion datasets registered.")
        return

    dataset_options = {dataset["title"]: dataset for dataset in datasets}
    selected_title = st.selectbox("Dataset", options=list(dataset_options.keys()))
    selected_dataset = dataset_options[selected_title]

    col1, col2, col3 = st.columns(3)
    col1.metric("Dataset key", selected_dataset["key"])
    col2.metric("Graph", selected_dataset["graph_name"])
    col3.metric("Source", selected_dataset["path"])

    if st.button("Run ingestion workflow", type="primary"):
        result = api_request(
            "POST",
            api_url,
            "/api/v1/workflows/ingestion/runs",
            json_payload={"dataset_key": selected_dataset["key"]},
        )
        if result:
            if result["status"] == "completed":
                st.success("Workflow completed")
            else:
                st.error(f"Workflow {result['status']}")
            render_workflow_run(result)

    runs = api_request("GET", api_url, "/api/v1/workflows/ingestion/runs")
    if runs:
        st.subheader("Recent Runs")
        for run in runs:
            with st.expander(f"{run['graph_name']} - {run['status']} - {run['created_at']}"):
                render_workflow_run(run)


def render_workflow_run(run: dict[str, Any]) -> None:
    metrics = st.columns(4)
    metrics[0].metric("Status", run["status"])
    metrics[1].metric("Graph", run["graph_name"])
    metrics[2].metric("Triples", run.get("triple_count") or 0)
    metrics[3].metric("Steps", len(run.get("steps", [])))

    for step in run.get("steps", []):
        if step["status"] == "completed":
            st.success(f"{step['name']}: {step['detail']}")
        else:
            st.error(f"{step['name']}: {step['detail']}")

    if run.get("error"):
        st.error(run["error"])


def render_validation(api_url: str) -> None:
    st.header("Validate RDF")
    graph_name = st.text_input("Graph name", value="streamlit-validation-run")
    data_graph_ttl = st.text_area(
        "Data graph Turtle",
        value=read_example("sample.ttl"),
        height=260,
    )
    shacl_shapes_ttl = st.text_area(
        "SHACL shapes Turtle",
        value=read_file(ROOT_DIR / "kg" / "shapes" / "semanticops-core.shacl.ttl"),
        height=180,
    )

    if st.button("Run validation", type="primary"):
        payload = {
            "graph_name": graph_name,
            "data_graph_ttl": data_graph_ttl,
            "shacl_shapes_ttl": shacl_shapes_ttl,
        }
        result = api_request("POST", api_url, "/api/v1/knowledge-graphs/validate", json_payload=payload)
        if result:
            if result["conforms"]:
                st.success("Validation conforms")
            else:
                st.error("Validation failed")
            st.code(result["report_text"], language="text")

    reports = api_request("GET", api_url, "/api/v1/knowledge-graphs/validation-reports")
    if reports:
        st.subheader("Recent Reports")
        st.dataframe(reports, use_container_width=True)


def render_graph_store(api_url: str) -> None:
    st.header("Graph Store")
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Promote Turtle")
        graph_name = st.text_input("Named graph", value="streamlit-promoted-graph")
        data_graph_ttl = st.text_area("Approved Turtle", value=read_example("sample.ttl"), height=280)
        if st.button("Promote graph", type="primary"):
            result = promote_graph(api_url, graph_name, data_graph_ttl)
            if result:
                st.success(f"Promoted {result['triple_count']} triples")
                st.json(result)

    with col2:
        st.subheader("Inventory")
        graphs = api_request("GET", api_url, "/api/v1/knowledge-graphs/graphs")
        if graphs:
            st.dataframe(graphs, use_container_width=True)
        else:
            st.info("No named graphs returned.")


def render_graph_view(api_url: str) -> None:
    st.header("Graph View")
    st.caption("Animated draggable graph view of named graph resources, classes, properties, and literals.")

    graphs = api_request("GET", api_url, "/api/v1/knowledge-graphs/graphs")
    if not graphs:
        st.info("No named graphs returned.")
        return

    graph_options = {graph["graph_name"]: graph["graph_iri"] for graph in graphs}
    selected_graph_name = st.selectbox("Named graph", options=list(graph_options.keys()))
    selected_graph_iri = graph_options[selected_graph_name]

    col1, col2, col3 = st.columns(3)
    triple_limit = col1.slider("Triple limit", min_value=25, max_value=300, value=120, step=25)
    show_literals = col2.toggle("Show literal data", value=True)
    physics = col3.toggle("Animated physics", value=True)

    triples = fetch_graph_triples(api_url, selected_graph_iri, triple_limit, show_literals)
    if not triples:
        st.info("The selected graph returned no triples.")
        return

    stats = graph_stats(triples)
    metric_cols = st.columns(4)
    metric_cols[0].metric("Triples", len(triples))
    metric_cols[1].metric("Resources", stats["resources"])
    metric_cols[2].metric("Classes", stats["classes"])
    metric_cols[3].metric("Literals", stats["literals"])

    components.html(
        build_graph_html(triples, physics=physics),
        height=720,
        scrolling=False,
    )


def render_medical_datasets(api_url: str) -> None:
    st.header("Medical Datasets")
    st.caption("Load the prepared synthetic and UCI Heart Disease RDF graphs into Fuseki.")

    datasets = [
        {
            "name": "synthetic-medical-cohort",
            "path": KG_EXAMPLES_DIR / "synthetic-medical-cohort.ttl",
            "description": "Synthetic cardiometabolic cohort with 5 patient profiles.",
        },
        {
            "name": "uci-heart-disease-cleveland",
            "path": KG_EXAMPLES_DIR / "uci-heart-disease-cleveland.ttl",
            "description": "UCI Heart Disease Cleveland processed dataset converted to RDF.",
        },
    ]

    for dataset in datasets:
        with st.container(border=True):
            st.subheader(dataset["name"])
            st.write(dataset["description"])
            path = dataset["path"]
            if not path.exists():
                st.warning(f"Missing file: {path}")
                continue

            st.caption(f"{path.relative_to(ROOT_DIR)} ({path.stat().st_size:,} bytes)")
            if st.button(f"Promote {dataset['name']}", key=f"promote-{dataset['name']}"):
                result = promote_graph(api_url, dataset["name"], read_file(path))
                if result:
                    st.success(f"Promoted {result['triple_count']} triples")

    st.subheader("Heart Disease Counts")
    query = """
PREFIX somed: <https://semanticops.ai/ontology/medical#>
SELECT ?presence (COUNT(?diagnosis) AS ?count)
WHERE {
  GRAPH <https://semanticops.ai/graphs/uci-heart-disease-cleveland> {
    ?diagnosis a somed:HeartDiseaseDiagnosis ;
      somed:hasHeartDiseasePresence ?presence .
  }
}
GROUP BY ?presence
ORDER BY ?presence
""".strip()
    if st.button("Run heart disease summary"):
        result = execute_query(api_url, query)
        render_bindings(result)


def render_sparql(api_url: str) -> None:
    st.header("SPARQL")
    query = st.text_area(
        "Query",
        value="""
SELECT ?graph ?subject ?predicate ?object
WHERE {
  GRAPH ?graph { ?subject ?predicate ?object }
}
LIMIT 25
""".strip(),
        height=260,
    )
    if st.button("Run query", type="primary"):
        result = execute_query(api_url, query)
        render_bindings(result)
        if result:
            with st.expander("Raw JSON"):
                st.json(result)


def promote_graph(api_url: str, graph_name: str, data_graph_ttl: str) -> dict[str, Any] | None:
    return api_request(
        "PUT",
        api_url,
        "/api/v1/knowledge-graphs/graphs",
        json_payload={"graph_name": graph_name, "data_graph_ttl": data_graph_ttl},
    )


def execute_query(api_url: str, query: str) -> dict[str, Any] | None:
    payload = {"query": query}
    result = api_request("POST", api_url, "/api/v1/knowledge-graphs/query", json_payload=payload)
    if not result:
        return None
    return result["results"]


def fetch_graph_triples(
    api_url: str,
    graph_iri: str,
    limit: int,
    show_literals: bool,
) -> list[dict[str, str]]:
    object_filter = "" if show_literals else "FILTER(isIRI(?object))"
    query = f"""
SELECT ?subject ?predicate ?object
WHERE {{
  GRAPH <{graph_iri}> {{
    ?subject ?predicate ?object .
    {object_filter}
  }}
}}
LIMIT {limit}
""".strip()
    result = execute_query(api_url, query)
    if not result:
        return []

    bindings = result.get("results", {}).get("bindings", [])
    triples = []
    for binding in bindings:
        triples.append(
            {
                "subject": binding["subject"]["value"],
                "predicate": binding["predicate"]["value"],
                "object": binding["object"]["value"],
                "object_type": binding["object"]["type"],
            }
        )
    return triples


def graph_stats(triples: list[dict[str, str]]) -> dict[str, int]:
    resources = set()
    classes = set()
    literals = 0
    for triple in triples:
        resources.add(triple["subject"])
        if triple["object_type"] == "uri":
            resources.add(triple["object"])
        else:
            literals += 1
        if triple["predicate"].endswith("22-rdf-syntax-ns#type"):
            classes.add(triple["object"])
    return {"resources": len(resources), "classes": len(classes), "literals": literals}


def build_graph_html(triples: list[dict[str, str]], physics: bool) -> str:
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []
    type_predicate = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"

    for index, triple in enumerate(triples):
        subject = triple["subject"]
        predicate = triple["predicate"]
        object_value = triple["object"]
        object_id = object_value if triple["object_type"] == "uri" else f"literal:{index}:{object_value}"

        nodes.setdefault(
            subject,
            {
                "id": subject,
                "label": compact_iri(subject),
                "title": subject,
                "group": "resource",
            },
        )

        if predicate == type_predicate:
            nodes[object_id] = {
                "id": object_id,
                "label": compact_iri(object_value),
                "title": object_value,
                "group": "class",
            }
            edges.append(
                {
                    "from": subject,
                    "to": object_id,
                    "label": "type",
                    "arrows": "to",
                    "color": {"color": "#7c3aed"},
                }
            )
            continue

        if triple["object_type"] == "uri":
            nodes.setdefault(
                object_id,
                {
                    "id": object_id,
                    "label": compact_iri(object_value),
                    "title": object_value,
                    "group": "resource",
                },
            )
        else:
            nodes[object_id] = {
                "id": object_id,
                "label": truncate_label(object_value),
                "title": object_value,
                "group": "literal",
                "shape": "box",
            }

        edges.append(
            {
                "from": subject,
                "to": object_id,
                "label": compact_iri(predicate),
                "arrows": "to",
            }
        )

    payload = {
        "nodes": list(nodes.values()),
        "edges": edges,
        "physics": physics,
    }
    data_json = json.dumps(payload)

    return f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <script src="https://unpkg.com/vis-network@9.1.9/standalone/umd/vis-network.min.js"></script>
  <style>
    html, body, #graph {{
      height: 100%;
      margin: 0;
      background: #f8faf7;
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    #graph {{
      border: 1px solid #d8ded7;
      border-radius: 8px;
    }}
  </style>
</head>
<body>
  <div id="graph"></div>
  <script>
    const payload = {data_json};
    const nodes = new vis.DataSet(payload.nodes);
    const edges = new vis.DataSet(payload.edges);
    const container = document.getElementById("graph");
    const options = {{
      autoResize: true,
      interaction: {{
        hover: true,
        dragNodes: true,
        dragView: true,
        zoomView: true,
        tooltipDelay: 90
      }},
      physics: {{
        enabled: payload.physics,
        solver: "forceAtlas2Based",
        forceAtlas2Based: {{
          gravitationalConstant: -55,
          centralGravity: 0.015,
          springLength: 120,
          springConstant: 0.08,
          damping: 0.45
        }},
        stabilization: {{ iterations: 120 }}
      }},
      nodes: {{
        borderWidth: 1,
        shadow: true,
        shape: "dot",
        size: 17,
        font: {{ size: 13, color: "#17211b", face: "Inter, Arial" }}
      }},
      groups: {{
        resource: {{ color: {{ background: "#dbeafe", border: "#2563eb" }} }},
        class: {{ color: {{ background: "#ede9fe", border: "#7c3aed" }}, shape: "diamond", size: 22 }},
        literal: {{ color: {{ background: "#ecfdf5", border: "#0f766e" }}, shape: "box" }}
      }},
      edges: {{
        color: {{ color: "#64748b", highlight: "#0f766e" }},
        font: {{ size: 11, align: "middle", strokeWidth: 3, strokeColor: "#f8faf7" }},
        smooth: {{ type: "dynamic" }}
      }}
    }};
    const network = new vis.Network(container, {{ nodes, edges }}, options);
    network.once("stabilizationIterationsDone", () => {{
      if (payload.physics) {{
        network.setOptions({{ physics: {{ enabled: true, stabilization: false }} }});
      }}
    }});
  </script>
</body>
</html>
"""


def compact_iri(value: str) -> str:
    separators = ["#", "/"]
    compact = value
    for separator in separators:
        if separator in compact:
            compact = compact.rsplit(separator, 1)[-1]
    return truncate_label(compact)


def truncate_label(value: str, limit: int = 34) -> str:
    if len(value) <= limit:
        return value
    return f"{value[: limit - 1]}..."


def render_bindings(result: dict[str, Any] | None) -> None:
    if not result:
        return

    bindings = result.get("results", {}).get("bindings", [])
    rows = [
        {key: binding_value.get("value") for key, binding_value in binding.items()}
        for binding in bindings
    ]
    if rows:
        st.dataframe(rows, use_container_width=True)
    else:
        st.info("The query returned no rows.")


def api_request(
    method: str,
    api_url: str,
    path: str,
    json_payload: dict[str, Any] | None = None,
) -> dict[str, Any] | list[dict[str, Any]] | None:
    try:
        response = requests.request(
            method=method,
            url=f"{api_url}{path}",
            json=json_payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        st.error(f"API request failed: {exc}")
        return None


def read_example(filename: str) -> str:
    return read_file(KG_EXAMPLES_DIR / filename)


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


if __name__ == "__main__":
    main()


