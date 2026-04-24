# Decision Intelligence Assistant

Production‑style FastAPI backend + React frontend that run **four answering strategies** on the same customer‑support ticket in parallel and expose a single query interface that returns all four side‑by‑side:

- **ML** – local Random Forest priority classifier (urgent / normal)
- **LLM zero‑shot** – the same priority question answered by a Groq LLM
- **RAG** – Chroma retrieval over historical tickets → grounded answer via LLM
- **Non‑RAG** – LLM‑only answer with no retrieval (control group)

Every call returns latency, cost, sources, and confidence, so the UI can compare **cost / quality / latency** of each path on the same input.

## Architecture

| Path | Description | Cost | Latency |
|------|-------------|------|---------|
| ML | Random Forest on engineered text features (local inference) | $0 | ~2 ms |
| LLM zero‑shot | Short chat completion triaging the ticket | Token‑based (Groq pricing) | ~1–2 s |
| RAG | Chroma cosine retrieval → prompt‑stuffed grounded answer via LLM | Token‑based (Groq pricing) | ~1–3 s |
| Non‑RAG | LLM‑only answer without retrieval | Token‑based (Groq pricing) | ~1–2 s |

All four run **concurrently** in the backend. The browser sees a single response with all results.

## Repository layout

```
Decision-Intelligence-Assistant/
├── notebook.ipynb                # EDA, labeling logic, feature engineering, model comparison
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app entry point
│   │   ├── routers/              # API endpoints (ml, llm, retrieval)
│   │   ├── schemas/              # Pydantic request/response models
│   │   ├── services/             # business logic (RAG, ML, LLM clients)
│   │   └── core/                 # config, logging setup
│   ├── scripts/
│   │   └── prepare_rag.py        # ingest tweets → Chroma vector store
│   ├── models/                   # priority_classifier_pipeline.joblib + metadata
│   ├── chroma_db/                # persistent Chroma index (gitignored)
│   ├── data/                     # raw CSV (gitignored)
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── uv.lock
├── frontend/
│   ├── src/
│   │   ├── App.jsx               # chat interface with 4‑way comparison
│   │   ├── components/           # Header
│   │   ├── index.css             # custom styling
│   │   └── main.jsx              # React entry point
│   ├── nginx.conf                # reverse proxy to backend:8000
│   ├── Dockerfile                # multi‑stage: node build → nginx
│   ├── package.json
│   └── package-lock.json
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md                     # this file
```

## Quick start — Docker (recommended)

### 1. Prerequisites

- Docker Desktop 4.30+ (or Docker Engine 24+ with Compose v2)
- A Groq API key (or any LLM provider key)

### 2. Configure environment

```bash
cp .env.example .env
# Open .env and set at least:
#   GROQ_API_KEY=your-key-here
# All other variables have sensible defaults.
```

### 3. Run the stack

```bash
# Build images + start everything; Ctrl+C to stop.
docker compose up --build
```

### 4. Open the UI

- Frontend: **http://localhost** (port 80)
- Backend health: **http://localhost:8000/health** (exposed for debugging only)

The browser only talks to the frontend. API requests to `/api/...` are reverse‑proxied by nginx to `backend:8000` on the internal Docker network.

### 5. Ingest tickets into the vector store (required for RAG)

The `chroma_data` volume starts empty. To populate it:

```bash
# Ensure backend/data/twcs.csv exists (or use the prepare_rag.py script that downloads from Kaggle)
docker compose run --rm backend python scripts/prepare_rag.py
```

The script writes into the named volume, so every future `docker compose up` reuses the populated index.

### 6. Stop / rebuild / wipe

```bash
docker compose down            # stop; keep volumes
docker compose down -v         # stop AND wipe chroma_data + logs
docker compose build --no-cache  # rebuild ignoring cache
docker compose up -d --build backend  # rebuild just one service
```

## Docker architecture details

| Service | Base image | Role | Host port |
|---------|------------|------|-----------|
| backend | python:3.11-slim | FastAPI (RAG, ML, LLM) | none (internal only) |
| frontend | nginx:alpine | Static Vite build + reverse proxy to backend:8000 | 80 |
| Vector DB | — | In‑process Chroma (persistent mode) inside backend | — |

**Why no separate vector‑DB service?**  
Chroma in persistent mode is an in‑process library, not a network server. Running it as a separate service would double memory, add a network hop per retrieval, and provide no benefit with a single backend replica. The persisted index lives on a named volume (`chroma_data`), so it survives restarts exactly like a standalone DB would.

**Shared network**  
An explicit bridge network `app-net` is declared. Services reference each other by name (`http://backend:8000`), never via `localhost`.

**Named volumes**  
- `chroma_data` → `/app/chroma_db` : persistent Chroma index  
- `logs_data` → `/app/logs` : rotating app.log + request logs  

Both survive `docker compose down`. Only `down -v` wipes them.

**Port exposure**  
Only the frontend is published to the host (port 80). The backend declares `expose: ["8000"]` but no `ports:`, making it inaccessible from `localhost:8000` externally by design.

**Secrets & configuration**  
All secrets are loaded from `.env` via `env_file:` in `docker-compose.yml`. Nothing is hardcoded in the Dockerfiles or source. `.env.example` ships with every variable the stack needs; `.env` is gitignored.

## Environment variables

| Variable | Where used | Default |
|----------|------------|---------|
| `GROQ_API_KEY` | Backend — required | (empty) |
| `LLM_MODEL_NAME` | Backend — Groq model | `llama-3.3-70b-versatile` |
| `CHROMA_PERSIST_DIR` | Backend — Chroma index path | `/app/chroma_db` |
| `EMBEDDING_MODEL_NAME` | Backend — sentence‑transformer model | `all-MiniLM-L6-v2` |
| `TOP_K_RETRIEVAL` | Backend — number of RAG sources | 5 |
| `FRONTEND_HOST_PORT` | Compose — host port for the UI | 80 |
| `BACKEND_HOST` | Frontend nginx upstream | `backend` |
| `BACKEND_PORT` | Frontend nginx upstream port | 8000 |

## API reference

Live Swagger doc: `http://localhost:8000/docs` (when backend is exposed).

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness probe. Returns `{"status":"ok"}` |
| GET | `/retrieval/similar?query=...` | Retrieve top‑k similar tickets from Chroma |
| POST | `/llm/rag` | RAG answer with sources, latency, cost |
| POST | `/llm/non-rag` | LLM‑only answer, no context |
| POST | `/llm/priority` | LLM zero‑shot priority prediction |
| POST | `/ml/predict` | ML priority prediction (fast, free) |
| GET | `/ml/info` | Model metadata (test F1, ROC‑AUC) |

Request/response schemas are documented in the `/docs` endpoint.

## Logging

The backend writes structured logs to:
- **stdout** (captured by `docker compose logs`)
- **`/app/logs/app.log`** — rotating file (persisted on `logs_data` volume)

Example:
```
2025-04-24 12:34:56 | INFO | app.routers.llm | RAG answer generated | latency=1834.02ms | cost=0.000312
```

Tail logs:
```bash
docker compose exec backend tail -f /app/logs/app.log
```

## Local development (without Docker)

Useful when iterating on code with hot‑reload.

**Prerequisites**: Python 3.11+, Node 20+

### Backend
```bash
cd backend
uv sync
cp .env.example .env          # then set GROQ_API_KEY
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev                    # proxies /api to localhost:8000
# Open http://localhost:5173
```

## Design decisions

- **One‑query, four answers**: `Promise.all` in the frontend fetches all four endpoints in parallel, so the UI renders them simultaneously.
- **Real token‑derived cost**: The LLM service uses `completion.usage.total_tokens` × Groq\'s pricing to compute per‑request cost (not estimated).
- **Chroma distance → similarity**: `similarity = 1 - distance` for cosine distance, so scores are always in [0,1].
- **Weak‑supervision labeling**: The `priority` target was created with a heuristic rule (keywords + punctuation + sentiment). The Random Forest learns to approximate that rule — documented and acknowledged in the notebook.
- **CPU‑only inference**: The embedding model and ML classifier run on CPU, keeping the backend image small and avoiding GPU dependencies.

## Known limitations

- **RAG quality** depends on the ingested dataset. If training data shifts, the vector store should be re‑built.
- **Priority labels** are not ground truth. The ML model’s high accuracy reflects weak supervision, not human annotation. See the notebook for discussion.
- **First container start** is slow (~90 s) because `sentence-transformers` downloads `all-MiniLM-L6-v2` into the image cache. Subsequent starts are fast.
- **No authentication** — the API is open. In a real deployment, add an API gateway or authentication layer.

## Notebook

`notebook.ipynb` (root) contains the full ML pipeline:

1. Data loading & cleaning  
2. Feature engineering  
3. Weak‑supervision labeling  
4. Model training (Logistic Regression, Random Forest, XGBoost, SVM)  
5. Cross‑validation and test evaluation  
6. Serialization of the best pipeline

The model is saved as `backend/models/priority_classifier_pipeline.joblib`, ready for the FastAPI service.
