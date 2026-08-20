import json
import re
from pathlib import Path

import httpx

from app.domain.models import NaturalLanguageQueryResult

READ_ONLY_QUERY = re.compile(
    r"^(?:\s*(?:PREFIX|BASE)\s+[^\n]+\s*)*(SELECT|ASK|CONSTRUCT|DESCRIBE)\b",
    re.IGNORECASE,
)
UPDATE_KEYWORD = re.compile(
    r"\b(INSERT|DELETE|LOAD|CLEAR|CREATE|DROP|COPY|MOVE|ADD)\b",
    re.IGNORECASE,
)


class QueryTranslationService:
    def __init__(self, api_key: str, model: str, assets_dir: Path) -> None:
        self._api_key = api_key
        self._model = model
        self._assets_dir = assets_dir

    async def translate(self, question: str) -> NaturalLanguageQueryResult:
        ontology = "\n\n".join(
            path.read_text(encoding="utf-8-sig")
            for path in sorted((self._assets_dir / "ontologies").glob("*.ttl"))
        )
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.openai.com/v1/responses",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "model": self._model,
                    "instructions": (
                        "Translate the user's question into one read-only SPARQL query using only "
                        "the supplied ontology vocabulary. Never generate SPARQL Update "
                        "operations. "
                        "Return a concise explanation. Ontology:\n" + ontology
                    ),
                    "input": question,
                    "reasoning": {"effort": "low"},
                    "text": {
                        "verbosity": "low",
                        "format": {
                            "type": "json_schema",
                            "name": "sparql_translation",
                            "strict": True,
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string"},
                                    "explanation": {"type": "string"},
                                },
                                "required": ["query", "explanation"],
                                "additionalProperties": False,
                            },
                        },
                    },
                    "max_output_tokens": 1200,
                    "store": False,
                },
            )
            response.raise_for_status()

        return parse_translation_response(response.json())


def parse_translation_response(payload: dict) -> NaturalLanguageQueryResult:
    text = "".join(
        content.get("text", "")
        for item in payload.get("output", [])
        if item.get("type") == "message"
        for content in item.get("content", [])
        if content.get("type") == "output_text"
    )
    if not text:
        raise ValueError("OpenAI returned no query translation.")

    result = NaturalLanguageQueryResult.model_validate(json.loads(text))
    if not READ_ONLY_QUERY.match(result.query) or UPDATE_KEYWORD.search(result.query):
        raise ValueError("Generated SPARQL is not read-only.")
    return result
