import { afterEach, describe, expect, it, vi } from "vitest";

import { listIngestionDatasets, startIngestionRun, translateNaturalLanguageQuery } from "./api";

afterEach(() => vi.unstubAllGlobals());

describe("agent workflow API", () => {
  it("uses the ingestion endpoints", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => [] });
    vi.stubGlobal("fetch", fetchMock);

    await listIngestionDatasets();
    await startIngestionRun("sample");
    await translateNaturalLanguageQuery("Show all graphs");

    expect(fetchMock.mock.calls.map(([url]) => url)).toEqual([
      "http://localhost:8000/api/v1/workflows/ingestion/datasets",
      "http://localhost:8000/api/v1/workflows/ingestion/runs",
      "http://localhost:8000/api/v1/knowledge-graphs/translate-query",
    ]);
  });
});
