"use client";

import { CheckCircle2, Database, Loader2, Play, RefreshCw, Search, XCircle } from "lucide-react";
import { type FormEvent, useEffect, useState } from "react";

import {
  executeSparqlQuery,
  listGraphs,
  listValidationReports,
  upsertGraph,
  validateGraph,
  type GraphStoreResult,
  type GraphSummary,
  type SparqlQueryResult,
  type ValidationReport,
} from "@/lib/api";

const sampleData = `@prefix so: <https://semanticops.ai/ontology/core#> .
@prefix ex: <https://semanticops.ai/example/> .

ex:account-policy a so:KnowledgeAsset ;
  so:describes ex:customer-account .

ex:customer-account a so:BusinessEntity .`;

const sampleShapes = `@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix so: <https://semanticops.ai/ontology/core#> .

so:KnowledgeAssetShape a sh:NodeShape ;
  sh:targetClass so:KnowledgeAsset ;
  sh:property [
    sh:path so:describes ;
    sh:minCount 1 ;
  ] .`;

export function ValidationWorkspace() {
  const [graphName, setGraphName] = useState("customer-risk-controls");
  const [dataGraph, setDataGraph] = useState(sampleData);
  const [shapesGraph, setShapesGraph] = useState(sampleShapes);
  const [reports, setReports] = useState<ValidationReport[]>([]);
  const [graphs, setGraphs] = useState<GraphSummary[]>([]);
  const [activeReport, setActiveReport] = useState<ValidationReport | null>(null);
  const [promotion, setPromotion] = useState<GraphStoreResult | null>(null);
  const [query, setQuery] = useState("SELECT ?graph ?subject ?predicate ?object WHERE { GRAPH ?graph { ?subject ?predicate ?object } } LIMIT 10");
  const [queryResult, setQueryResult] = useState<SparqlQueryResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isPromoting, setIsPromoting] = useState(false);
  const [isQuerying, setIsQuerying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listValidationReports()
      .then(setReports)
      .catch(() => setReports([]));
    listGraphs()
      .then(setGraphs)
      .catch(() => setGraphs([]));
  }, []);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsRunning(true);
    setError(null);

    try {
      const report = await validateGraph({
        graph_name: graphName,
        data_graph_ttl: dataGraph,
        shacl_shapes_ttl: shapesGraph,
      });
      setActiveReport(report);
      setPromotion(null);
      setReports((current) => [report, ...current.filter((item) => item.id !== report.id)]);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Validation request failed.");
    } finally {
      setIsRunning(false);
    }
  }

  async function onPromote() {
    if (!activeReport?.conforms) {
      return;
    }

    setIsPromoting(true);
    setError(null);

    try {
      const result = await upsertGraph({
        graph_name: graphName,
        data_graph_ttl: dataGraph,
        shacl_shapes_ttl: shapesGraph,
      });
      setPromotion(result);
      setGraphs(await listGraphs());
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Graph promotion failed.");
    } finally {
      setIsPromoting(false);
    }
  }

  async function onQuery(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsQuerying(true);
    setError(null);

    try {
      setQueryResult(await executeSparqlQuery(query));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Graph query failed.");
    } finally {
      setIsQuerying(false);
    }
  }

  return (
    <div className="validation-stack">
      <div className="validation-layout">
      <form className="validation-form" onSubmit={onSubmit}>
        <div className="field-row">
          <label htmlFor="graph-name">Graph name</label>
          <input
            id="graph-name"
            value={graphName}
            onChange={(event) => setGraphName(event.target.value)}
          />
        </div>

        <div className="editor-grid">
          <label htmlFor="data-graph">Data graph</label>
          <textarea
            id="data-graph"
            value={dataGraph}
            onChange={(event) => setDataGraph(event.target.value)}
            spellCheck={false}
          />

          <label htmlFor="shapes-graph">SHACL shapes</label>
          <textarea
            id="shapes-graph"
            value={shapesGraph}
            onChange={(event) => setShapesGraph(event.target.value)}
            spellCheck={false}
          />
        </div>

        <button type="submit" className="primary-action" disabled={isRunning}>
          {isRunning ? <Loader2 size={18} aria-hidden="true" /> : <Play size={18} aria-hidden="true" />}
          Run validation
        </button>

        {error ? <p className="error-text">{error}</p> : null}
      </form>

      <aside className="validation-results">
        <div className="result-status">
          {activeReport?.conforms ? (
            <CheckCircle2 aria-hidden="true" />
          ) : (
            <XCircle aria-hidden="true" />
          )}
          <div>
            <span>Latest report</span>
            <strong>{activeReport ? (activeReport.conforms ? "Conforms" : "Violations") : "No run"}</strong>
          </div>
        </div>

        <pre>{activeReport?.report_text ?? "Validation output will appear here."}</pre>

        <button
          type="button"
          className="secondary-action"
          disabled={!activeReport?.conforms || isPromoting}
          onClick={onPromote}
        >
          {isPromoting ? <Loader2 size={18} aria-hidden="true" /> : <Database size={18} aria-hidden="true" />}
          Promote graph
        </button>

        {promotion ? (
          <div className="promotion-summary">
            <span>{promotion.graph_name}</span>
            <strong>{promotion.triple_count} triples</strong>
          </div>
        ) : null}

        <div className="report-list">
          {reports.slice(0, 5).map((report) => (
            <button key={report.id} type="button" onClick={() => setActiveReport(report)}>
              <span>{report.graph_name}</span>
              <strong>{report.conforms ? "Pass" : "Fail"}</strong>
            </button>
          ))}
        </div>
      </aside>
      </div>

      <div className="graph-store-grid">
        <section className="graph-inventory" aria-label="Graph inventory">
          <div className="section-heading">
            <h3>Graph Inventory</h3>
            <button type="button" className="icon-action" onClick={() => listGraphs().then(setGraphs)}>
              <RefreshCw size={16} aria-hidden="true" />
              <span>Refresh</span>
            </button>
          </div>
          <div className="report-list">
            {graphs.length ? (
              graphs.map((graph) => (
                <button key={graph.graph_iri} type="button" onClick={() => setGraphName(graph.graph_name)}>
                  <span>{graph.graph_name}</span>
                  <strong>Named</strong>
                </button>
              ))
            ) : (
              <p className="empty-text">No named graphs stored.</p>
            )}
          </div>
        </section>

        <form className="sparql-workbench" onSubmit={onQuery}>
          <div className="section-heading">
            <h3>SPARQL Workbench</h3>
            <button type="submit" className="icon-action" disabled={isQuerying}>
              {isQuerying ? <Loader2 size={16} aria-hidden="true" /> : <Search size={16} aria-hidden="true" />}
              <span>Run</span>
            </button>
          </div>
          <textarea value={query} onChange={(event) => setQuery(event.target.value)} spellCheck={false} />
          <pre>{formatQueryResult(queryResult)}</pre>
        </form>
      </div>
    </div>
  );
}

function formatQueryResult(result: SparqlQueryResult | null) {
  if (!result) {
    return "Query results will appear here.";
  }

  return JSON.stringify(result.results, null, 2);
}
