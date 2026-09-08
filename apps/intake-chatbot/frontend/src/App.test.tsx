import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";

describe("App", () => {
  beforeEach(() => {
    sessionStorage.clear();
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/api/config/public")) return new Response(JSON.stringify({ profile_version: "2026-08-31", access_token_required: false }), { status: 200 });
      if (url.endsWith("/api/sessions")) return new Response(JSON.stringify([]), { status: 200 });
      return new Response(JSON.stringify({}), { status: 200 });
    }));
  });

  it("states the interpretation boundary on the first screen", async () => {
    render(<App />);
    expect(await screen.findByText("Build a structured Agent Card")).toBeInTheDocument();
    expect(screen.getByText(/Reporting completeness is separate from agent quality/)).toBeInTheDocument();
  });

  it("offers all three intake modes", async () => {
    render(<App />);
    expect(await screen.findByText("Describe an existing agent")).toBeInTheDocument();
    expect(screen.getByText("Document a planned agent")).toBeInTheDocument();
    expect(screen.getByText("Import structured information")).toBeInTheDocument();
  });
});
