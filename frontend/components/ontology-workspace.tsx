"use client";

import { useEffect, useState } from "react";

import { listOntologyModules, type OntologyModule } from "@/lib/api";

export function OntologyWorkspace() {
  const [modules, setModules] = useState<OntologyModule[]>([]);
  const [selected, setSelected] = useState<OntologyModule | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listOntologyModules()
      .then((items) => {
        setModules(items);
        setSelected(items[0] ?? null);
      })
      .catch((caught) => setError(caught instanceof Error ? caught.message : "Could not load ontologies."));
  }, []);

  return (
    <div className="ontology-layout">
      <section className="panel ontology-list">
        <div className="panel-heading">
          <h2>Modules</h2>
          <span>{modules.length} available</span>
        </div>
        <div className="report-list">
          {modules.map((module) => (
            <button key={module.key} type="button" onClick={() => setSelected(module)}>
              <span>{module.title}</span>
              <strong>{module.triple_count} triples</strong>
            </button>
          ))}
          {error ? <p className="error-text">{error}</p> : null}
        </div>
      </section>

      <section className="panel ontology-detail">
        <div className="panel-heading">
          <div>
            <h2>{selected?.title ?? "Ontology details"}</h2>
            <span>{selected?.namespace ?? "Select a module"}</span>
          </div>
          {selected?.version ? <strong>v{selected.version}</strong> : null}
        </div>

        {selected ? (
          <>
            <div className="ontology-metrics">
              <div><strong>{selected.class_count}</strong><span>Classes</span></div>
              <div><strong>{selected.object_property_count}</strong><span>Object properties</span></div>
              <div><strong>{selected.datatype_property_count}</strong><span>Datatype properties</span></div>
              <div><strong>{selected.triple_count}</strong><span>Triples</span></div>
            </div>
            <p className="ontology-path">{selected.path}</p>
            <pre>{selected.turtle}</pre>
          </>
        ) : (
          <p className="empty-text">Ontology details will appear here.</p>
        )}
      </section>
    </div>
  );
}
