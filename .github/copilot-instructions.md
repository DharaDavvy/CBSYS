# Copilot Instructions — CBSys (Career-Based Information System)

## Architecture

RAG expert system with a strict separation: **data** (NUC CCMAS curriculum in ChromaDB) stays isolated from **logic** (Llama 3 reasoning via LangChain). This prevents hallucinations.

- **`backend/`** — Python FastAPI service. Entry point: `app/main.py`. Runs on `uvicorn`.
- **`frontend/`** — React (Vite) app with Tailwind CSS. Entry point: `src/index.jsx`.
- **Firebase** — Auth (email/password) + Firestore (user profiles, chat history, transcripts).
- **ChromaDB** — Local persistent vector store at `backend/chroma_store/`. Populated by `backend/scripts/ingest.py`.
- **Ollama** — Local Llama 3 inference; Groq is the cloud fallback.

## Backend Conventions (`backend/`)

- **Routers** live in `app/routers/` — one file per endpoint group (`chat.py`, `roadmap.py`, `auth.py`).
- **Services** live in `app/services/` — business logic (`rag.py`, `embeddings.py`, `llm.py`). Routers call services, never the reverse.
- **Pydantic models** go in `app/models/schemas.py`. All request/response bodies must have a schema.
- **Prompt templates** go in `app/prompts/`. The advisor prompt enforces: answer ONLY from retrieved context, always cite sources, say "I don't know" when context is insufficient.
- **Firebase Admin SDK** is initialised once in `app/models/firebase.py`. Auth middleware verifies `Authorization: Bearer <token>` headers.
- **Environment variables** are in `backend/.env` (never committed). Load via `python-dotenv` in `app/config.py`.
- LLM temperature is **0** for all curriculum queries to maximise determinism.

## Frontend Conventions (`frontend/`)

- **Component structure:** `src/components/{Feature}/ComponentName.jsx` (e.g., `Chat/ChatWindow.jsx`).
- **Services:** `src/services/firebase.js` (SDK init), `src/services/api.js` (Axios wrapper for FastAPI).
- **Auth flow:** Matric numbers (e.g., `CSC/2024/001`) are converted to synthetic emails (`csc-2024-001@faculty.local`) for Firebase Auth. This mapping must be identical on frontend and backend.
- **State management:** React Context (`src/context/AuthContext.jsx`) for auth; custom hooks (`src/hooks/useChat.js`) for feature state. No Redux.
- **Styling:** Tailwind CSS utility classes. No separate CSS files.
- **Roadmap rendering:** React Flow for directed prerequisite graphs. Fallback to CSS timeline if React Flow is too heavy.

## Firestore Schema

Collections are keyed by Firebase `uid`:
- `users/{uid}` — `name`, `matricNumber`, `level` (100–500), `department`
- `profiles/{uid}` — `interests[]`, `skills[]`, `targetCareer`
- `transcripts/{uid}` — `courses: [{ code, title, units, grade, semester }]`
- `chatHistories/{uid}` — `messages: [{ role, content, sources[], timestamp }]`

## RAG Pipeline (critical path)

1. User query → embed with `all-MiniLM-L6-v2` → search ChromaDB (top-k chunks)
2. Build prompt: system instruction + retrieved context + user question
3. Call Llama 3 (Ollama local, Groq fallback) → post-process to append `[Source: NUC CCMAS Computing, Section X]`
4. Return `{ response, sources[] }` to frontend

## Key Commands

```bash
# Backend
cd backend
python -m venv env && env\Scripts\activate   # Windows
pip install -r requirements.txt
python scripts/ingest.py                      # One-off: embed PDF into ChromaDB
uvicorn app.main:app --reload                 # Dev server on :8000

# Frontend
cd frontend
npm install
npm run dev                                   # Vite dev server on :5173
```

## Important Patterns

- **Every LLM recommendation must include a citation.** Never generate advice without a `sources` array referencing the ChromaDB chunk metadata.
- **Matric-to-email conversion** (`CSC/2024/001` → `csc-2024-001@faculty.local`) is duplicated in both `frontend/src/services/firebase.js` and `backend/app/models/firebase.py`. Keep them in sync.
- **PDF ingestion settings:** chunk_size=500, chunk_overlap=50, embedding model `all-MiniLM-L6-v2`. Changing these requires re-running `ingest.py` and wiping `chroma_store/`.
- **CORS:** FastAPI middleware must whitelist the Vite dev origin (`http://localhost:5173`).
