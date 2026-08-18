from fastapi.testclient import TestClient

from app.main import create_app

DATA_GRAPH = """@prefix so: <https://semanticops.ai/ontology/core#> .
@prefix ex: <https://semanticops.ai/example/> .

ex:asset a so:KnowledgeAsset ;
    so:describes ex:entity .
"""

SHAPES_GRAPH = """@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix so: <https://semanticops.ai/ontology/core#> .

so:KnowledgeAssetShape a sh:NodeShape ;
    sh:targetClass so:KnowledgeAsset ;
    sh:property [
        sh:path so:describes ;
        sh:minCount 1 ;
    ] .
"""


def test_validation_report_is_persisted() -> None:
    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/knowledge-graphs/validate",
            json={
                "graph_name": "customer-risk-controls",
                "data_graph_ttl": DATA_GRAPH,
                "shacl_shapes_ttl": SHAPES_GRAPH,
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["conforms"] is True
        assert payload["graph_name"] == "customer-risk-controls"
        assert payload["id"]

        reports_response = client.get("/api/v1/knowledge-graphs/validation-reports")
        assert reports_response.status_code == 200
        reports = reports_response.json()
        assert reports[0]["id"] == payload["id"]

