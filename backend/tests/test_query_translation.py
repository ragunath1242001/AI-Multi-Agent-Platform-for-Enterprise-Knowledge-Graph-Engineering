import json

import pytest

from app.services.query_translation_service import parse_translation_response


def response_payload(query: str) -> dict:
    return {
        "output": [
            {"type": "reasoning"},
            {
                "type": "message",
                "content": [
                    {
                        "type": "output_text",
                        "text": json.dumps({"query": query, "explanation": "Uses known terms."}),
                    }
                ],
            },
        ]
    }


def test_accepts_read_only_sparql_and_rejects_updates() -> None:
    result = parse_translation_response(
        response_payload(
            "PREFIX so: <https://semanticops.ai/ontology/core#>\n"
            "SELECT * WHERE { ?s ?p ?o }"
        )
    )
    assert result.query.startswith("PREFIX")

    with pytest.raises(ValueError, match="not read-only"):
        parse_translation_response(response_payload("DELETE WHERE { ?s ?p ?o }"))
