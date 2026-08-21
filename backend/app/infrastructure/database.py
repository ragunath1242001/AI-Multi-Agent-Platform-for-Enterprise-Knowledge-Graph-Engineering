from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.settings import get_settings


class Base(DeclarativeBase):
    pass


@lru_cache
def get_engine():
    return create_engine(get_settings().database_url, pool_pre_ping=True)


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)


def initialize_database() -> None:
    from app.infrastructure.persistence.graph_lineage_record import GraphLineageRecord
    from app.infrastructure.persistence.ontology_version_record import OntologyVersionRecord
    from app.infrastructure.persistence.validation_report_record import ValidationReportRecord
    from app.infrastructure.persistence.workflow_run_ontology_version_record import (
        WorkflowRunOntologyVersionRecord,
    )
    from app.infrastructure.persistence.workflow_run_record import WorkflowRunRecord

    _ = GraphLineageRecord
    _ = OntologyVersionRecord
    _ = ValidationReportRecord
    _ = WorkflowRunOntologyVersionRecord
    _ = WorkflowRunRecord
    Base.metadata.create_all(bind=get_engine())


def get_session() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()
