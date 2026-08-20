import { afterEach, describe, expect, it, vi } from "vitest";

import { runProjectDemo } from "./demo";

afterEach(() => vi.unstubAllGlobals());

describe("project demo", () => {
  it("runs every platform stage in order", async () => {
    const responses = [
      [{ key: "core" }, { key: "medical" }],
      { id: "run", graph_name: "synthetic-medical-cohort", status: "completed", steps: [{}, {}, {}, {}], triple_count: 115, validation_report_id: "report" },
      [{ id: "report", conforms: true }],
      [{ graph_name: "synthetic-medical-cohort" }],
      { results: { results: { bindings: [{}] } } },
      [{ id: "run" }],
    ];
    vi.stubGlobal("fetch", vi.fn().mockImplementation(async () => ({
      ok: true,
      json: async () => responses.shift(),
    })));
    const updates: string[] = [];

    const summary = await runProjectDemo((id, status) => updates.push(`${id}:${status}`));

    expect(summary).toEqual({
      ontologyModules: 2,
      workflowRuns: 1,
      validationReports: 1,
      namedGraphs: 1,
      queryRows: 1,
    });
    expect(updates.filter((update) => update.endsWith(":completed"))).toHaveLength(6);
  });
});
