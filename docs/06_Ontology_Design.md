# Ontology Design

Ontology design should follow small, composable modules. Core platform concepts belong in `kg/ontologies/semanticops-core.ttl`; domain-specific ontologies should extend the core vocabulary without changing its semantics.

Design principles:

- Prefer stable URIs.
- Separate classes from operational workflow entities.
- Capture labels, comments, provenance, and version metadata.
- Review breaking ontology changes through CI validation.

Current ontology modules:

- `kg/ontologies/semanticops-core.ttl`: core platform vocabulary.
- `kg/ontologies/semanticops-medical.ttl`: medical dataset vocabulary for synthetic and UCI Heart Disease graphs.
