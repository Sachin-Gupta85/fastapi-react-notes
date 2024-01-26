"""API tests for the Notes service. Uses an in-memory mongomock database via a
dependency override, so no running MongoDB is required."""
import mongomock
import pytest
from fastapi.testclient import TestClient

from app.db import get_db
from app.main import app


@pytest.fixture
def client():
    db = mongomock.MongoClient()["testdb"]
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_create_and_get(client):
    r = client.post("/api/notes", json={"title": "First", "body": "hello", "tags": ["x"]})
    assert r.status_code == 201
    nid = r.json()["id"]
    got = client.get(f"/api/notes/{nid}").json()
    assert got["title"] == "First" and got["tags"] == ["x"]
    assert got["created_at"] and got["updated_at"]


def test_list_search_and_tag_filter(client):
    client.post("/api/notes", json={"title": "Grocery", "body": "milk eggs", "tags": ["home"]})
    client.post("/api/notes", json={"title": "Standup", "body": "work notes", "tags": ["work"]})
    assert len(client.get("/api/notes").json()) == 2
    assert [n["title"] for n in client.get("/api/notes?q=milk").json()] == ["Grocery"]
    assert [n["title"] for n in client.get("/api/notes?tag=work").json()] == ["Standup"]
    assert client.get("/api/notes?q=nomatch").json() == []


def test_update(client):
    nid = client.post("/api/notes", json={"title": "Draft"}).json()["id"]
    r = client.put(f"/api/notes/{nid}", json={"title": "Final", "body": "done", "tags": []})
    assert r.status_code == 200 and r.json()["title"] == "Final"


def test_delete_and_404(client):
    nid = client.post("/api/notes", json={"title": "Temp"}).json()["id"]
    assert client.delete(f"/api/notes/{nid}").status_code == 204
    assert client.get(f"/api/notes/{nid}").status_code == 404
    assert client.delete(f"/api/notes/{nid}").status_code == 404


def test_bad_id_is_404(client):
    assert client.get("/api/notes/not-an-id").status_code == 404


def test_validation_rejects_empty_title(client):
    assert client.post("/api/notes", json={"title": ""}).status_code == 422
