# Deployment

Local deployment uses Docker Compose with frontend, backend, PostgreSQL, and Fuseki services. Production deployment should split services into independently scalable units and provide managed equivalents for PostgreSQL, container hosting, secret storage, telemetry, and graph persistence.

Minimum production controls:

- TLS at all public boundaries.
- Centralized secrets.
- Database backups.
- Audit logging.
- CI/CD gates for linting, tests, and image builds.

