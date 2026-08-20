import { Database } from "lucide-react";

import { ValidationWorkspace } from "@/components/validation-workspace";

export default function ValidationPage() {
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
          <a href="/ontology">Ontology</a>
          <a className="active" href="/validation">Validation</a>
          <a href="/observability">Observability</a>
          <a href="/demo">Demo</a>
        </nav>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">SHACL governance</p>
            <h1>Validation</h1>
          </div>
        </header>

        <section className="panel validation-panel">
          <div className="panel-heading">
            <h2>Graph validation workspace</h2>
            <span>Validate, promote, inventory, and query named graphs</span>
          </div>
          <ValidationWorkspace />
        </section>
      </section>
    </main>
  );
}
