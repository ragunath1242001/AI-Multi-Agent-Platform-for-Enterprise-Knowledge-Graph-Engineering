import { Database } from "lucide-react";

import { OntologyWorkspace } from "@/components/ontology-workspace";

export default function OntologyPage() {
  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand">
          <Database aria-hidden="true" />
          <span>SemanticOps</span>
        </div>
        <nav>
          <a href="/">Operations</a>
          <a href="/agents">Agents</a>
          <a className="active" href="/ontology">Ontology</a>
          <a href="/validation">Validation</a>
          <a href="/observability">Observability</a>
          <a href="/demo">Demo</a>
        </nav>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Knowledge graph model</p>
            <h1>Ontology</h1>
          </div>
        </header>

        <OntologyWorkspace />
      </section>
    </main>
  );
}
