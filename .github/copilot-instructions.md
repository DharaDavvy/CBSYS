# Copilot Instructions — CBSys (Career-Based Information System)

## Architecture Overview

RAG expert system with strict **data/logic separation**: NUC CCMAS curriculum embeddings (FAISS vector store) stay isolated from LLM reasoning (Llama 3 via LangChain). This prevents hallucinations.

**Tech Stack:**
- **Backend:** FastAPI (Python 3.13) — entry point `backend/app/main.py`
- **Frontend:** React 19 + Vite 8 + Tailwind CSS 4 — entry point `frontend/src/main.jsx`
- **Auth/DB:** Firebase (synthetic email auth) + Firestore (user profiles, chat history)
- **Vector Store:** FAISS (`backend/faiss_store/`) with HuggingFace Inference API embeddings (`all-MiniLM-L6-v2`)
- **LLM Cascade:** Ollama (local) → Groq → Gemini → HuggingFace Inference (cloud fallbacks, see `backend/app/services/llm.py`)

## Critical Workflows

### 1. First-Time Setup
```powershell
# Backend
cd backend
python -m venv env; .\env\Scripts\activate
pip install -r requirements.txt

# Place PDF in backend/data/, then run ingestion
python scripts/ingest.py  # Creates faiss_store/index.faiss + metadata.json

# Create .env with: FIREBASE_CREDENTIALS, GROQ_API_KEY, HF_API_TOKEN, etc.
uvicorn app.main:app --reload  # Starts on :8000

# Frontend
cd frontend
npm install
# Create .env.local with VITE_API_URL, VITE_FIREBASE_* keys
npm run dev  # Starts on :5173
```

### 2. Startup Lifecycle (`app/main.py` lifespan)
FastAPI's `@asynccontextmanager` runs **before** accepting requests:
1. `embeddings.init_vectorstore()` — loads FAISS index into memory
2. `llm.init_llm()` — tests Ollama health → falls back to Groq/Gemini if unreachable
3. `firebase.init_firebase()` — initialises Admin SDK from service account JSON

### 3. RAG Request Flow (`/chat` endpoint)
```
User message → verify_token (Firebase JWT) → rag.ask(question)
  ├─ embeddings.search() — embed query → FAISS similarity search (top-k)
  ├─ _format_context() — build rich metadata labels (course code, prerequisites, page)
  ├─ llm.generate(prompt) — calls LLM with ADVISOR_SYSTEM_PROMPT template
  └─ Post-process: ensure [Source: ...] citations → save to Firestore
```

## Backend Conventions

### Service Layer Pattern
- **Routers** (`app/routers/`) — thin FastAPI endpoints. Only validate schemas, call services, return responses.
- **Services** (`app/services/`) — business logic. `rag.py` orchestrates `embeddings.py` + `llm.py`.
- **Never** import routers from services (prevents circular deps).

### Authentication Middleware
`app/routers/auth.py` exports `verify_token` dependency:
- **Production mode** (Firebase configured): verifies JWT via Firebase Admin SDK
- **Dev mode** (no Firebase): treats Bearer token value as UID directly (passthrough)
- All protected routes use `uid: str = Depends(verify_token)`

### LLM Fallback Chain (`llm.py`)
`init_llm()` tests each provider in order until one succeeds:
1. **Ollama** (`localhost:11434`) — no auth required, fastest
2. **Groq** — requires `GROQ_API_KEY`, uses `llama3-70b-8192`
3. **Gemini** — requires `GOOGLE_API_KEY`, uses `gemini-2.0-flash`
4. **HuggingFace** — requires `HF_API_TOKEN`, uses `Meta-Llama-3-8B-Instruct` via Inference API

### Environment Variables (`backend/.env`)
```env
FIREBASE_CREDENTIALS=cbsys-a69e2-firebase-adminsdk-fbsvc-63a48f8acc.json  # relative to backend/
GROQ_API_KEY=gsk_...
GOOGLE_API_KEY=AIza...
HF_API_TOKEN=hf_...
OLLAMA_BASE_URL=http://localhost:11434  # optional
CORS_EXTRA_ORIGINS=https://cbsys.vercel.app  # space-separated
```

## Frontend Conventions

### Matric Number Auth (Critical Pattern)
Firebase doesn't support matric numbers natively. Both frontend and backend implement **identical** conversion:
```javascript
// frontend/src/services/firebase.js
function matricToEmail(matric) {
  return matric.trim().toLowerCase().replace(/\//g, "-") + "@faculty.local";
}
```
```python
# backend/app/models/firebase.py
def matric_to_email(matric: str) -> str:
    return matric.strip().lower().replace("/", "-") + "@faculty.local"
```
Example: `CSC/2024/001` → `csc-2024-001@faculty.local`

### API Client (`src/services/api.js`)
Axios instance with automatic token injection:
- Request interceptor waits for `auth.currentUser` (handles async init race)
- Calls `user.getIdToken(true)` to force-refresh expired tokens
- Sets `Authorization: Bearer <token>` header on every request

### Route Guards (`src/App.jsx`)
- `ProtectedRoute` checks **both** `currentUser` (context) and `auth.currentUser` (sync SDK state) to prevent registration race condition
- `PublicRoute` redirects authenticated users to `/dashboard` or `/onboarding` based on `sessionStorage.getItem("needsOnboarding")`

## Data Pipeline Details

### FAISS Ingestion (`scripts/ingest.py`)
1. Load PDFs from `backend/data/` using `pypdf.PdfReader`
2. Split text with `text_splitter.split_text(chunk_size=500, overlap=50)`
3. Extract metadata via regex: course codes, level, semester, units, prerequisites, section numbers
4. Embed chunks via HF Inference API (retries on 503 for model cold-start)
5. Build `faiss.IndexFlatIP` (inner product = cosine similarity after L2 normalization)
6. Persist to `faiss_store/index.faiss` + `metadata.json`

**Metadata Schema (per chunk):**
```python
{
  "page": int,
  "source": str,           # e.g. "Computing-CCMAS 2023-FINAL.pdf"
  "course_code": str,      # e.g. "CSC 301"
  "level": int,            # e.g. 300
  "department": str,       # e.g. "CSC"
  "semester": int,         # 1 or 2
  "units": int,
  "prerequisites": list[str],
  "section": str           # e.g. "3.2.1"
}
```

### Prompt Engineering (`app/prompts/advisor.py`)
The advisor system prompt enforces **6 strict rules**:
1. Answer ONLY from provided context (no external knowledge)
2. Say "I don't have enough information" if context is insufficient
3. End every factual statement with `[Source: ...]`
4. Be concise and encouraging
5. Include course code + units when listing courses
6. **Course level accuracy:** Never recommend a 300-level course for Year 2 (code determines year)

### Firestore Schema
```
users/{uid}          — name, matricNumber, level (100-500), department
profiles/{uid}       — interests[], skills[], targetCareer
transcripts/{uid}    — courses: [{ code, title, units, grade, semester }]
chatHistories/{uid}  — messages: [{ role, content, sources[], timestamp }]
```
All writes use `set(data, merge=True)` to avoid overwriting existing fields.

## Key Constraints

1. **LLM temperature is always 0** (`config.py`) for deterministic curriculum answers
2. **CORS origins** include both dev (`localhost:5173`) and production URLs (Vercel, Render)
3. **Changing embedding settings** (model, chunk size) requires re-running `ingest.py` and deleting `faiss_store/`
4. **Matric-to-email** conversion must stay identical in frontend + backend
5. **No external knowledge:** LLM must cite FAISS sources for every recommendation
