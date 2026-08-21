from pathlib import Path

from fastapi.testclient import TestClient

from app.api.v1.routes.knowledge_graphs import get_graph_store_service
from app.core.settings import get_settings
from app.domain.models import GraphStoreResult
from app.main import create_app


class FakeGraphStoreService:
    def __init__(self) -> None:
        self.promoted: list[str] = []

    async def upsert_graph(self, graph_name: str, data_graph_ttl: str) -> GraphStoreResult:
        self.promoted.append(graph_name)
        return GraphStoreResult(
            graph_name=graph_name,
            graph_iri=f"https://semanticops.ai/graphs/{graph_name}",
            triple_count=data_graph_ttl.count("."),
        )


def test_ingestion_workflow_run_is_persisted(monkeypatch, tmp_path: Path) -> None:
    assets_dir = tmp_path / "kg"
    (assets_dir / "examples").mkdir(parents=True)
    (assets_dir / "shapes").mkdir(parents=True)
    (assets_dir / "ontologies").mkdir(parents=True)

    (assets_dir / "examples" / "synthetic-medical-cohort.ttl").write_text(
        """@prefix so: <https://semanticops.ai/ontology/core#> .
@prefix ex: <https://semanticops.ai/example/> .
ex:asset a so:KnowledgeAsset ; so:describes ex:cohort .
ex:cohort a so:BusinessEntity .
""",
        encoding="utf-8",
    )
    (assets_dir / "examples" / "uci-heart-disease-cleveland.ttl").write_text(
        (assets_dir / "examples" / "synthetic-medical-cohort.ttl").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    ontology_ttl = """@prefix ex: <https://example.com/ontology#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
ex: a owl:Ontology ; rdfs:label "Example Ontology" ; owl:versionInfo "1.0.0" .
ex:Asset a owl:Class .
"""
    for filename in ("semanticops-core.ttl", "semanticops-medical.ttl"):
        (assets_dir / "ontologies" / filename).write_text(ontology_ttl, encoding="utf-8")
    (assets_dir / "shapes" / "semanticops-core.shacl.ttl").write_text(
        """@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix so: <https://semanticops.ai/ontology/core#> .
so:KnowledgeAssetShape a sh:NodeShape ;
  sh:targetClass so:KnowledgeAsset ;
  sh:property [ sh:path so:describes ; sh:minCount 1 ] .
""",
        encoding="utf-8",
    )
    (assets_dir / "shapes" / "semanticops-medical.shacl.ttl").write_text(
        "@prefix sh: <http://www.w3.org/ns/shacl#> .\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("KNOWLEDGE_ASSETS_DIR", str(assets_dir))
    get_settings.cache_clear()

    graph_store = FakeGraphStoreService()
    app = create_app()
    app.dependency_overrides[get_graph_store_service] = lambda: graph_store

    with TestClient(app) as client:
        datasets_response = client.get("/api/v1/workflows/ingestion/datasets")
        assert datasets_response.status_code == 200
        assert datasets_response.json()[0]["key"] == "synthetic-medical-cohort"

        run_response = client.post(
            "/api/v1/workflows/ingestion/runs",
            json={"dataset_key": "synthetic-medical-cohort"},
        )
        assert run_response.status_code == 200
        run = run_response.json()
        assert run["status"] == "completed"
        assert [step["name"] for step in run["steps"]] == [
            "ontology",
            "rdf_generation",
            "validation",
            "promotion",
            "observability",
        ]
        assert graph_store.promoted[-1] == "synthetic-medical-cohort"
        assert len(graph_store.promoted) == 3
        assert len(run["ontology_versions"]) == 2
        assert all(len(version["checksum"]) == 64 for version in run["ontology_versions"])
        assert run["lineage"]["workflow_run_id"] == run["id"]
        assert run["lineage"]["source_uri"] == "examples/synthetic-medical-cohort.ttl"
        assert len(run["lineage"]["source_checksum"]) == 64
        assert run["lineage"]["validation_report_id"] == run["validation_report_id"]
        assert run["lineage"]["graph_iri"] == (
            "https://semanticops.ai/graphs/synthetic-medical-cohort"
        )
        assert len(run["lineage"]["ontology_versions"]) == 2

        lineage_response = client.get(
            "/api/v1/knowledge-graphs/lineage/synthetic-medical-cohort"
        )
        assert lineage_response.status_code == 200
        assert [item["workflow_run_id"] for item in lineage_response.json()] == [run["id"]]

        versions_response = client.get("/api/v1/knowledge-graphs/ontology/versions")
        assert versions_response.status_code == 200
        assert len(versions_response.json()) == 2

        (assets_dir / "examples" / "synthetic-medical-cohort.ttl").write_text(
            """@prefix so: <https://semanticops.ai/ontology/core#> .
@prefix ex: <https://semanticops.ai/example/> .
ex:asset a so:KnowledgeAsset .
""",
            encoding="utf-8",
        )
        failed_response = client.post(
            "/api/v1/workflows/ingestion/runs",
            json={"dataset_key": "synthetic-medical-cohort"},
        )
        assert failed_response.status_code == 200
        failed = failed_response.json()
        assert failed["status"] == "failed"
        assert failed["lineage"] is None
        assert [step["name"] for step in failed["steps"]] == [
            "ontology",
            "rdf_generation",
            "validation",
            "observability",
        ]
        assert len(graph_store.promoted) == 3
        assert [version["id"] for version in failed["ontology_versions"]] == [
            version["id"] for version in run["ontology_versions"]
        ]
        assert len(
            client.get(
                "/api/v1/knowledge-graphs/lineage/synthetic-medical-cohort"
            ).json()
        ) == 1

        runs_response = client.get("/api/v1/workflows/ingestion/runs")
        assert runs_response.status_code == 200
        assert runs_response.json()[0]["id"] == failed["id"]
