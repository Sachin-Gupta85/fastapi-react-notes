const BASE = import.meta.env?.VITE_API_URL || "";

async function req(path, opts) {
  const res = await fetch(`${BASE}/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) throw new Error(`${res.status}`);
  return res.status === 204 ? null : res.json();
}

export const listNotes = (q = "", tag = "") => {
  const p = new URLSearchParams();
  if (q) p.set("q", q);
  if (tag) p.set("tag", tag);
  const qs = p.toString();
  return req(`/notes${qs ? `?${qs}` : ""}`);
};
export const createNote = (note) =>
  req("/notes", { method: "POST", body: JSON.stringify(note) });
export const deleteNote = (id) => req(`/notes/${id}`, { method: "DELETE" });
