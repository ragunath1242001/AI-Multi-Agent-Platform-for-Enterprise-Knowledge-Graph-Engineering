# Agent Architecture

SemanticOps uses modular agents with explicit responsibility boundaries:

- Ontology Agent: proposes and reviews ontology structures.
- RDF Generation Agent: converts source knowledge into RDF.
- Validation Agent: evaluates SHACL conformance.
- Reasoning Agent: materializes or checks inferred knowledge.
- Query Agent: converts natural language into governed graph queries.
- Observability Agent: inspects workflow quality, drift, and failures.

LangGraph coordinates these agents as typed state transitions rather than opaque chains.

