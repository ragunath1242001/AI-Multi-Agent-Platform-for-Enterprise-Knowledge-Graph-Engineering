from fastapi.testclient import TestClient

from app.api.v1.routes.knowledge_graphs import get_graph_store_service
from app.domain.models import GraphStoreResult, GraphSummary, SparqlQueryResult
from app.main import create_app

DATA_GRAPH = """@prefix so: <https://semanticops.ai/ontology/core#> .
@prefix ex: <https://semanticops.ai/example/> .

ex:asset a so:KnowledgeAsset ;
    so:describes ex:entity .
"""


class FakeGraphStoreService:
    async def upsert_graph(self, graph_name: str, data_graph_ttl: str) -> GraphStoreResult:
        assert "so:KnowledgeAsset" in data_graph_ttl
        return GraphStoreResult(
            graph_name=graph_name,
            graph_iri=f"https://semanticops.ai/graphs/{graph_name}",
            triple_count=2,
        )

    async def list_graphs(self) -> list[GraphSummary]:
        return [
            GraphSummary(
                graph_name="customer-risk-controls",
                graph_iri="https://semanticops.ai/graphs/customer-risk-controls",
            )
        ]

    async def execute_query(self, query: str) -> SparqlQueryResult:
        assert query.startswith("SELECT")
        return SparqlQueryResult(
            results={
                "head": {"vars": ["graph"]},
                "results": {"bindings": []},
            }
        )


def test_graph_store_contract_endpoints() -> None:
    app = create_app()
    app.dependency_overrides[get_graph_store_service] = FakeGraphStoreService

    with TestClient(app) as client:
        upsert_response = client.put(
            "/api/v1/knowledge-graphs/graphs",
            json={
                "graph_name": "customer-risk-controls",
                "data_graph_ttl": DATA_GRAPH,
            },
        )
        assert upsert_response.status_code == 200
        assert upsert_response.json()["triple_count"] == 2

        graphs_response = client.get("/api/v1/knowledge-graphs/graphs")
        assert graphs_response.status_code == 200
        assert graphs_response.json()[0]["graph_name"] == "customer-risk-controls"

        query_response = client.post(
            "/api/v1/knowledge-graphs/query",
            json={"query": "SELECT * WHERE { GRAPH ?graph { ?s ?p ?o } } LIMIT 5"},
        )
        assert query_response.status_code == 200
        assert query_response.json()["results"]["head"]["vars"] == ["graph"]
