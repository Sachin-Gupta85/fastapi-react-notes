# 📝 fastapi-react-notes — notes app (React + FastAPI + MongoDB)

> A full-stack notes manager: create, search, tag, and delete notes. **React** (Vite) front end, **FastAPI** + **MongoDB** back end, with a cross-language test harness.

![React](https://img.shields.io/badge/React-18-61dafb)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![MongoDB](https://img.shields.io/badge/MongoDB-7-47A248)
![Tests](https://img.shields.io/badge/tests-pytest%20%2B%20vitest-brightgreen)

## ✨ Features
- Full CRUD REST API (`/api/notes`) with Pydantic validation.
- Case-insensitive substring **search** (`?q=`) and **tag filter** (`?tag=`).
- `#hashtags` in a note body become tags automatically in the UI.
- Backend tests run against an **in-memory Mongo** (`mongomock`) — no database required to test.

## 🗂️ Layout
```
server/   FastAPI app (app/main.py, app/db.py) + pytest suite
client/   React + Vite UI + Vitest tests
docker-compose.yml   MongoDB + API
run_harness.sh       runs both test suites
```

## 🚀 Run
```bash
docker compose up --build        # MongoDB + API on :8000
cd client && npm install && npm run dev   # UI on :5173 (proxies /api -> :8000)
```

## ✅ Test
```bash
./run_harness.sh                 # backend (pytest) + frontend (vitest)
# or individually:
cd server && pip install -r requirements-dev.txt && python -m pytest -q
cd client && npm install && npm test
```

## 🔌 API
| Method | Path | Purpose |
|---|---|---|
| GET | `/api/notes?q=&tag=` | list / search / filter |
| POST | `/api/notes` | create |
| GET | `/api/notes/{id}` | read one |
| PUT | `/api/notes/{id}` | update |
| DELETE | `/api/notes/{id}` | delete |

## 📝 License
MIT — see [LICENSE](LICENSE).
