from fastapi.testclient import TestClient

from app.core.settings import get_settings
from app.main import create_app


def test_lists_fixed_ontology_modules(monkeypatch, tmp_path) -> None:
    ontology_dir = tmp_path / "ontologies"
    ontology_dir.mkdir()
    turtle = '''@prefix ex: <https://example.com/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
ex: a owl:Ontology ; rdfs:label "Example" .
ex:Thing a owl:Class .
'''
    for name in ("semanticops-core.ttl", "semanticops-medical.ttl"):
        (ontology_dir / name).write_text(turtle, encoding="utf-8")

    monkeypatch.setenv("KNOWLEDGE_ASSETS_DIR", str(tmp_path))
    get_settings.cache_clear()

    with TestClient(create_app()) as client:
        response = client.get("/api/v1/knowledge-graphs/ontology/modules")

    assert response.status_code == 200
    assert [(item["title"], item["class_count"]) for item in response.json()] == [
        ("Example", 1),
        ("Example", 1),
    ]
