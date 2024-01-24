import React from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import App from "./App.jsx";

function mockFetch(sequence) {
  const calls = [...sequence];
  globalThis.fetch = vi.fn(() => {
    const next = calls.shift() ?? { ok: true, json: async () => [] };
    return Promise.resolve({
      ok: true,
      status: next.status ?? 200,
      json: async () => next.body ?? [],
    });
  });
}

describe("Notes App", () => {
  beforeEach(() => vi.restoreAllMocks());

  it("loads and displays notes on mount", async () => {
    mockFetch([{ body: [{ id: "1", title: "Hello", body: "world", tags: ["x"] }] }]);
    render(<App />);
    await waitFor(() => expect(screen.getByText("Hello")).toBeInTheDocument());
    expect(screen.getByText("#x")).toBeInTheDocument();
  });

  it("submits a new note", async () => {
    mockFetch([{ body: [] }]);
    render(<App />);
    await waitFor(() => expect(globalThis.fetch).toHaveBeenCalled());
    fireEvent.change(screen.getByLabelText("title"), { target: { value: "New" } });
    fireEvent.click(screen.getByText("Add note"));
    await waitFor(() => {
      const posted = globalThis.fetch.mock.calls.some(
        ([url, opts]) => opts?.method === "POST"
      );
      expect(posted).toBe(true);
    });
  });
});
