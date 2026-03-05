# Project Plan: AI-Powered Career-Based Information System

**Project Root:** `C:\Users\USER\CBSys`  
**Date:** March 2, 2026  
**Architecture:** RAG Expert System  
**Stack:** React.js · Firebase · FastAPI · Llama 3 · ChromaDB

---

## Final Directory Structure

```
CBSys/
├── backend/                    # FastAPI Python service
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app entry point
│   │   ├── config.py           # Environment & app settings
│   │   ├── routers/
│   │   │   ├── chat.py         # /chat endpoint
│   │   │   ├── roadmap.py      # /generate-roadmap endpoint
│   │   │   └── auth.py         # Token verification helpers
│   │   ├── services/
│   │   │   ├── rag.py          # RAG chain (retrieval + generation)
│   │   │   ├── embeddings.py   # ChromaDB query/ingestion logic
│   │   │   └── llm.py          # Llama 3 client (Ollama / Groq)
│   │   ├── prompts/
│   │   │   ├── advisor.py      # System prompt for Faculty Advisor persona
│   │   │   └── roadmap.py      # Prompt template for roadmap generation
│   │   └── models/
│   │       ├── schemas.py      # Pydantic request/response models
│   │       └── firebase.py     # Firebase Admin SDK init + helpers
│   ├── data/
│   │   └── Computing-CCMAS.pdf # Source PDF (placed manually)
│   ├── scripts/
│   │   └── ingest.py           # One-off script to embed PDF → ChromaDB
│   ├── chroma_store/           # Persisted ChromaDB vector data
│   ├── requirements.txt
│   ├── .env                    # Secrets (Firebase key path, Groq API key, etc.)
│   └── README.md
│
├── frontend/                   # React application
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Auth/
│   │   │   │   └── Login.jsx           # Matric number login screen
│   │   │   ├── Onboarding/
│   │   │   │   └── Wizard.jsx          # Interests & level form
│   │   │   ├── Chat/
│   │   │   │   ├── ChatWindow.jsx      # Message list + input
│   │   │   │   └── MessageBubble.jsx   # Single message component
│   │   │   ├── Roadmap/
│   │   │   │   └── VisualRoadmap.jsx   # React Flow / timeline view
│   │   │   └── Layout/
│   │   │       ├── Sidebar.jsx
│   │   │       └── Dashboard.jsx
│   │   ├── services/
│   │   │   ├── firebase.js     # Firebase SDK init + auth helpers
│   │   │   └── api.js          # Axios/fetch wrapper for FastAPI
│   │   ├── context/
│   │   │   └── AuthContext.jsx  # React context for current user
│   │   ├── hooks/
│   │   │   └── useChat.js      # Custom hook for chat state
│   │   ├── App.jsx
│   │   └── index.jsx
│   ├── package.json
│   ├── .env                    # REACT_APP_API_URL, Firebase config
│   └── README.md
│
├── PROJECT_PLAN.md             # ← This file
└── .gitignore
```

---

## Execution Order

Work is divided into **four phases**. Each phase ends with a verifiable checkpoint before moving on.

---

### Phase 1 — Environment & Knowledge Base Setup

| # | Task | Detail |
|---|------|--------|
| 1.1 | **Create project scaffolding** | Set up `backend/` and `frontend/` folders with the directory trees shown above. |
| 1.2 | **Python virtual environment** | Run `python -m venv backend/env` and generate `requirements.txt` with pinned versions of: `fastapi`, `uvicorn[standard]`, `langchain`, `langchain-community`, `chromadb`, `sentence-transformers`, `pypdf`, `python-dotenv`, `firebase-admin`, `httpx`. |
| 1.3 | **Place source PDF** | The user will drop `Computing-CCMAS.pdf` into `backend/data/`. |
| 1.4 | **Write ingestion script** (`scripts/ingest.py`) | Uses `PyPDFLoader` → `RecursiveCharacterTextSplitter` (chunk_size=500, overlap=50) → `HuggingFaceEmbeddings("all-MiniLM-L6-v2")` → persist to `chroma_store/`. |
| 1.5 | **Run ingestion & verify** | Execute `ingest.py`, then run a quick similarity search to confirm results are sensible. |

**Checkpoint:** A populated `chroma_store/` directory that returns relevant chunks for a test query like *"What are the prerequisites for CSC 301?"*.

---

### Phase 2 — Backend API (Inference Engine)

| # | Task | Detail |
|---|------|--------|
| 2.1 | **FastAPI skeleton** (`app/main.py`) | CORS middleware allowing the React dev server, lifespan event to load ChromaDB & LLM on startup. |
| 2.2 | **LLM client** (`services/llm.py`) | Wrapper around Ollama (`llama3` model) with a Groq fallback. Single `generate()` function. |
| 2.3 | **RAG service** (`services/rag.py`) | Accept a user query → embed it → retrieve top-k chunks from ChromaDB → build a prompt with context → call LLM → return answer with citations. |
| 2.4 | **Chat endpoint** (`routers/chat.py`) | `POST /chat` — accepts `{ user_id, message }`, calls RAG service, stores exchange in Firestore under the user's chat history, returns response + sources. |
| 2.5 | **Roadmap endpoint** (`routers/roadmap.py`) | `POST /generate-roadmap` — accepts student profile (level, interests, completed courses), queries ChromaDB for the relevant programme structure, asks LLM to produce a structured JSON roadmap (Year 1–4), returns it. |
| 2.6 | **Prompt engineering** (`prompts/`) | Strict system prompt: *"You are a Faculty Advisor at the Faculty of Computing. Answer ONLY using the provided context. If the context doesn't contain the answer, say so. End every recommendation with its source."* |
| 2.7 | **Citation logic** | Post-process LLM output to append `[Source: NUC CCMAS Computing, Section X]` based on the metadata of the retrieved chunks. |

**Checkpoint:** `POST /chat` with a curriculum question returns a cited answer; `POST /generate-roadmap` returns a valid JSON roadmap.

---

### Phase 3 — Firebase (Auth & Database)

| # | Task | Detail |
|---|------|--------|
| 3.1 | **Firebase project creation** | Create project in Firebase Console, enable Authentication (Email/Password) and Firestore. |
| 3.2 | **Firebase Admin SDK (backend)** | Download service account JSON, reference it in `backend/.env`, initialise in `app/models/firebase.py`. |
| 3.3 | **Matric → email mapping** | Utility function: `CSC/2024/001` → `csc-2024-001@faculty.local`. Implemented on both frontend and backend so they stay in sync. |
| 3.4 | **Firestore schema** | Create collections programmatically on first write: |

```
Firestore
├── users/{uid}
│   ├── name: string
│   ├── matricNumber: string       # "CSC/2024/001"
│   ├── level: number              # 100–500
│   └── department: string         # "Computer Science"
│
├── profiles/{uid}
│   ├── interests: string[]
│   ├── skills: string[]
│   └── targetCareer: string
│
├── transcripts/{uid}
│   └── courses: [{ code, title, units, grade, semester }]
│
└── chatHistories/{uid}
    └── messages: [{ role, content, sources[], timestamp }]
```

| 3.5 | **Auth middleware** | FastAPI dependency that verifies the Firebase ID token from the `Authorization: Bearer <token>` header on protected routes. |

**Checkpoint:** A test user can be created via the Admin SDK, a Firestore document is written and read, and the middleware rejects invalid tokens.

---

### Phase 4 — Frontend (React)

| # | Task | Detail |
|---|------|--------|
| 4.1 | **Scaffold React app** | `npm create vite@latest frontend -- --template react` (Vite for speed). Install dependencies: `firebase`, `axios`, `react-router-dom`, `reactflow`, `tailwindcss`. |
| 4.2 | **Firebase client init** (`services/firebase.js`) | Configure with project keys from `.env`. Export `auth` and `db` instances. |
| 4.3 | **Auth context & routing** | `AuthContext` provides `currentUser`. Unauthenticated users see Login; authenticated users see Dashboard. |
| 4.4 | **Login screen** | Input for Matric Number + password. On submit, convert matric → email, call `signInWithEmailAndPassword`. First-time users are created via `createUserWithEmailAndPassword` then redirected to onboarding. |
| 4.5 | **Onboarding wizard** | Multi-step form: (1) Confirm name & department, (2) Select interests from a checklist, (3) Enter current level. Writes to `users/` and `profiles/` in Firestore. |
| 4.6 | **Chat interface** | Messenger-style UI. Messages stored in local state via `useChat` hook. Each send triggers `POST /chat` with the Firebase ID token. Bot responses render Markdown + citation badges. |
| 4.7 | **Visual roadmap** | Call `POST /generate-roadmap` on button click. Parse returned JSON into nodes/edges for React Flow (or a simple CSS timeline fallback). Nodes represent semesters; edges represent prerequisites. |
| 4.8 | **Dashboard layout** | Sidebar with navigation (Chat, Roadmap, Profile). Top bar shows student name & level. |

**Checkpoint:** Full flow — login → onboarding → ask a question → receive cited answer → view roadmap.

---

## Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| LLM hosting | Ollama (local) with Groq cloud fallback | Free, keeps data on-premise; Groq provides faster inference if network is available. |
| Embedding model | `all-MiniLM-L6-v2` | Lightweight (80 MB), runs on CPU, good accuracy for academic text. |
| Vector DB | ChromaDB (local, persistent) | Zero infrastructure, file-based, native LangChain integration. |
| Frontend framework | React + Vite | Fast HMR, widely supported, large ecosystem. |
| Styling | Tailwind CSS | Utility-first, rapid prototyping, no custom CSS files needed. |
| Roadmap visualisation | React Flow | Interactive, supports directed graphs (prerequisite chains). |
| Auth strategy | Firebase Auth (email/password) | Matric numbers are mapped to synthetic emails; avoids OAuth complexity while still providing secure token-based auth. |

---

## Assumptions & Prerequisites

1. **Ollama** is installed and the `llama3` model has been pulled (`ollama pull llama3`).  
2. **Node.js ≥ 18** and **Python ≥ 3.10** are available on the machine.  
3. The NUC **Computing-CCMAS.pdf** file will be provided by the user before Phase 1.5.  
4. A Firebase project will be created manually via the Firebase Console; the service account JSON will be placed at `backend/.env` path.

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| LLM hallucinating course data | Strict RAG prompt + citation enforcement + temperature set to 0. |
| PDF parsing errors (tables, formatting) | Inspect chunk quality after ingestion; add manual corrections to a supplementary JSON file if needed. |
| Slow local inference | Groq fallback for cloud inference; cache frequent queries in Firestore. |
| Firebase free-tier limits | Firestore reads are minimised by batching chat history writes; Auth is free for email/password. |

---

## Next Step

Once this plan is reviewed and approved, implementation begins with **Phase 1.1 — Project scaffolding**.
