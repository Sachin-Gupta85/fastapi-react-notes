import React, { useEffect, useState } from "react";
import { listNotes, createNote, deleteNote } from "./api.js";

export default function App() {
  const [notes, setNotes] = useState([]);
  const [q, setQ] = useState("");
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [error, setError] = useState("");

  async function refresh(query = q) {
    try {
      setNotes(await listNotes(query));
      setError("");
    } catch (e) {
      setError("Failed to load notes");
    }
  }

  useEffect(() => {
    refresh("");
  }, []);

  async function onAdd(e) {
    e.preventDefault();
    if (!title.trim()) return;
    const tags = body.match(/#(\w+)/g)?.map((t) => t.slice(1)) || [];
    await createNote({ title: title.trim(), body, tags });
    setTitle("");
    setBody("");
    refresh();
  }

  async function onDelete(id) {
    await deleteNote(id);
    refresh();
  }

  return (
    <main style={{ maxWidth: 640, margin: "2rem auto", fontFamily: "system-ui" }}>
      <h1>📝 Notes</h1>
      <form onSubmit={onAdd} style={{ display: "grid", gap: 8, marginBottom: 16 }}>
        <input
          aria-label="title"
          placeholder="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <textarea
          aria-label="body"
          placeholder="Body (use #tags)"
          value={body}
          onChange={(e) => setBody(e.target.value)}
        />
        <button type="submit">Add note</button>
      </form>
      <input
        aria-label="search"
        placeholder="Search…"
        value={q}
        onChange={(e) => {
          setQ(e.target.value);
          refresh(e.target.value);
        }}
        style={{ width: "100%", marginBottom: 12 }}
      />
      {error && <p role="alert">{error}</p>}
      <ul style={{ listStyle: "none", padding: 0 }}>
        {notes.map((n) => (
          <li key={n.id} style={{ border: "1px solid #ddd", borderRadius: 8, padding: 12, marginBottom: 8 }}>
            <strong>{n.title}</strong>
            <p style={{ whiteSpace: "pre-wrap", margin: "4px 0" }}>{n.body}</p>
            <small>{n.tags.map((t) => `#${t}`).join(" ")}</small>
            <button onClick={() => onDelete(n.id)} style={{ float: "right" }}>
              Delete
            </button>
          </li>
        ))}
      </ul>
    </main>
  );
}
