import { Database } from "lucide-react";

import { ObservabilityWorkspace } from "@/components/observability-workspace";

export default function ObservabilityPage() {
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
          <a href="/validation">Validation</a>
          <a className="active" href="/observability">Observability</a>
          <a href="/demo">Demo</a>
        </nav>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Operational telemetry</p>
            <h1>Observability</h1>
          </div>
        </header>

        <ObservabilityWorkspace />
      </section>
    </main>
  );
}
