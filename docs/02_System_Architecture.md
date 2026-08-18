# System Architecture

SemanticOps is organized as a monorepo with separate deployable services for the web application and API. The backend exposes workflow and graph operations through FastAPI. The `agents` package owns LangGraph orchestration. Fuseki stores RDF named graphs, while PostgreSQL stores operational metadata, job state, users, audit events, and configuration.

Core boundaries:

- API layer: request validation and transport concerns.
- Application services: use-case orchestration.
- Domain layer: platform contracts and business entities.
- Infrastructure adapters: graph stores, databases, model providers, and external systems.

