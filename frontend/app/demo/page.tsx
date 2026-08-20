import { Database } from "lucide-react";

import { DemoWorkspace } from "@/components/demo-workspace";

export default function DemoPage() {
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
          <a href="/observability">Observability</a>
          <a className="active" href="/demo">Demo</a>
        </nav>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Guided walkthrough</p>
            <h1>Project Demo</h1>
          </div>
        </header>

        <DemoWorkspace />
      </section>
    </main>
  );
}
