"""Notes API — a small FastAPI + MongoDB service.

Endpoints:
    GET    /api/health
    GET    /api/notes?q=<text>&tag=<tag>      list / search / filter
    POST   /api/notes                         create
    GET    /api/notes/{id}                    read one
    PUT    /api/notes/{id}                    update
    DELETE /api/notes/{id}                    delete

Notes are documents {title, body, tags[], created_at, updated_at}. Search is a
case-insensitive substring match over title and body; `tag` filters by an exact
tag. The MongoDB handle is injected via the `get_db` dependency, so the test
suite swaps in an in-memory database.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import List, Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .db import get_db

app = FastAPI(title="Notes API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class NoteIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = ""
    tags: List[str] = Field(default_factory=list)


class NoteOut(NoteIn):
    id: str
    created_at: str
    updated_at: str


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _serialize(doc: dict) -> dict:
    doc = dict(doc)
    doc["id"] = str(doc.pop("_id"))
    return doc


def _oid(note_id: str) -> ObjectId:
    try:
        return ObjectId(note_id)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="note not found")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/notes", response_model=List[NoteOut])
def list_notes(q: Optional[str] = None, tag: Optional[str] = None, db=Depends(get_db)):
    query: dict = {}
    if q:
        rx = {"$regex": re.escape(q), "$options": "i"}
        query["$or"] = [{"title": rx}, {"body": rx}]
    if tag:
        query["tags"] = tag
    cur = db.notes.find(query).sort("updated_at", -1)
    return [_serialize(d) for d in cur]


@app.post("/api/notes", response_model=NoteOut, status_code=201)
def create_note(note: NoteIn, db=Depends(get_db)):
    now = _now()
    doc = note.model_dump()
    doc.update(created_at=now, updated_at=now)
    res = db.notes.insert_one(doc)
    doc["_id"] = res.inserted_id
    return _serialize(doc)


@app.get("/api/notes/{note_id}", response_model=NoteOut)
def get_note(note_id: str, db=Depends(get_db)):
    doc = db.notes.find_one({"_id": _oid(note_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="note not found")
    return _serialize(doc)


@app.put("/api/notes/{note_id}", response_model=NoteOut)
def update_note(note_id: str, note: NoteIn, db=Depends(get_db)):
    patch = note.model_dump()
    patch["updated_at"] = _now()
    doc = db.notes.find_one_and_update(
        {"_id": _oid(note_id)}, {"$set": patch}, return_document=True
    )
    if not doc:
        raise HTTPException(status_code=404, detail="note not found")
    return _serialize(doc)


@app.delete("/api/notes/{note_id}", status_code=204)
def delete_note(note_id: str, db=Depends(get_db)):
    res = db.notes.delete_one({"_id": _oid(note_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="note not found")
    return None
