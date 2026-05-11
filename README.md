# SHL Assessment Recommender

An AI-powered conversational system that helps recruiters and hiring managers discover the right SHL assessments through natural dialogue.

---

## Screenshots

> _Add screenshots here after deployment_
>
> | Chat UI | Assessment Cards | Mobile View |
> |---------|-----------------|-------------|
> | ![Chat](docs/chat.png) | ![Cards](docs/cards.png) | ![Mobile](docs/mobile.png) |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React + Vite)               │
│  ChatInput → ChatMessage → AssessmentCard → WelcomeScreen    │
└───────────────────────┬─────────────────────────────────────┘
                        │ POST /chat  GET /health
┌───────────────────────▼─────────────────────────────────────┐
│                    FastAPI Backend                            │
│  /health  /chat → Agent → VectorStore → LLM Provider         │
│                                                               │
│  ┌─────────────┐   ┌───────────────┐   ┌─────────────────┐  │
│  │ FAISS/Chroma│   │  LangChain    │   │ OpenAI/Groq/    │  │
│  │ Vector Store│   │  Agent        │   │ Gemini/OpenRouter│  │
│  └─────────────┘   └───────────────┘   └─────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│              Data Layer                                       │
│  shl_catalog.json  →  Embeddings  →  FAISS index             │
│  (scraped / curated from SHL product catalog)                 │
└─────────────────────────────────────────────────────────────┘
```

**Key Design Decisions:**
- **Stateless API**: Full conversation history sent on every request — no server-side sessions
- **Hallucination prevention**: Recommendations are validated against the retrieved catalog; invented assessments are silently dropped
- **Provider agnostic**: Swap LLMs via a single env var (`LLM_PROVIDER`)
- **Dual vector DB**: FAISS (default, zero infra) or ChromaDB (persistent, scalable)

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- An API key for at least one LLM provider (Groq has a free tier)

### 1. Clone and setup

```bash
git clone https://github.com/yourname/shl-recommender.git
cd shl-recommender
bash setup.sh
```

### 2. Configure environment variables

```bash
# Edit the root .env (used by docker-compose)
cp .env.example .env
nano .env

# Also edit backend/.env (used when running backend directly)
cp backend/.env.example backend/.env
nano backend/.env
```

### 3. Generate embeddings

```bash
cd backend
source venv/bin/activate
python ../scripts/generate_embeddings.py
```

### 4. Start services

**Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Frontend (separate terminal):**
```bash
cd frontend
npm run dev
# Opens at http://localhost:5173
```

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LLM_PROVIDER` | Yes | `groq` | `openai`, `groq`, `gemini`, or `openrouter` |
| `GROQ_API_KEY` | If using Groq | — | [Get free key](https://console.groq.com) |
| `OPENAI_API_KEY` | If using OpenAI | — | [Get key](https://platform.openai.com) |
| `GOOGLE_API_KEY` | If using Gemini | — | [Get key](https://aistudio.google.com) |
| `OPENROUTER_API_KEY` | If using OpenRouter | — | [Get key](https://openrouter.ai) |
| `EMBEDDING_PROVIDER` | No | `openai` | `openai` or `local` |
| `EMBEDDING_MODEL` | No | `text-embedding-3-small` | OpenAI embedding model |
| `VECTOR_DB` | No | `faiss` | `faiss` or `chroma` |
| `CATALOG_JSON_PATH` | No | `./data/shl_catalog.json` | Path to catalog JSON |
| `FAISS_INDEX_PATH` | No | `./data/faiss_index` | FAISS index directory |
| `MAX_TURNS` | No | `8` | Max conversation turns |
| `LOG_LEVEL` | No | `INFO` | `DEBUG`, `INFO`, `WARNING` |

### Frontend (`frontend/.env.local`)

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8000` | Backend API base URL |

---

## API Reference

### `GET /health`

```bash
curl http://localhost:8000/health
```

```json
{"status": "ok"}
```

### `POST /chat`

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "I need to hire a senior Java developer"}
    ]
  }'
```

**Response:**
```json
{
  "reply": "I can help with that! For a senior Java developer, here are the top SHL assessments...",
  "recommendations": [
    {
      "name": "Java 8 (New)",
      "url": "https://www.shl.com/solutions/products/product-catalog/view/java-8-new/",
      "test_type": "K",
      "description": "Assesses core Java 8 programming skills...",
      "duration": "45 minutes",
      "skills_measured": ["Java OOP", "Java collections", "Lambda expressions"],
      "confidence_score": 0.94
    }
  ],
  "end_of_conversation": false
}
```

**Multi-turn conversation:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "I need an assessment"},
      {"role": "assistant", "content": "What role are you hiring for?"},
      {"role": "user", "content": "A Python data engineer"}
    ]
  }'
```

---

## Scripts

### Scrape the SHL catalog

```bash
# Live scrape (may be slow or blocked)
python scripts/scrape_catalog.py

# Use curated fallback catalog (recommended)
python scripts/scrape_catalog.py --fallback
```

Output: `data/shl_catalog.json`

### Generate embeddings / build vector index

```bash
cd backend
python ../scripts/generate_embeddings.py
```

Output: `data/faiss_index/` (FAISS) or `data/chroma/` (ChromaDB)

---

## Docker Deployment

### Local (Docker Compose)

```bash
# Copy and configure .env
cp .env.example .env
# Edit .env with your API keys

# Build and start
docker-compose up --build

# API: http://localhost:8000
# UI:  http://localhost:3000
```

### Production (separate containers)

```bash
# Build backend
docker build -t shl-backend ./backend

# Build frontend
docker build -t shl-frontend ./frontend \
  --build-arg VITE_API_URL=https://your-api.railway.app

# Run backend
docker run -p 8000:8000 \
  -e LLM_PROVIDER=groq \
  -e GROQ_API_KEY=your_key \
  -e OPENAI_API_KEY=your_key \
  -v $(pwd)/data:/app/data \
  shl-backend

# Run frontend
docker run -p 3000:80 shl-frontend
```

---

## Railway Deployment

### Backend on Railway

1. Create a new Railway project
2. Connect your GitHub repository
3. Set **Root Directory** to `backend`
4. Add environment variables in Railway dashboard
5. Railway auto-detects `railway.json` and deploys

**Required Railway env vars:**
```
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_...
OPENAI_API_KEY=sk-...
EMBEDDING_PROVIDER=openai
VECTOR_DB=faiss
```

### Frontend on Railway (or Vercel/Netlify)

**Vercel (recommended for frontend):**
```bash
cd frontend
npx vercel --prod
# Set VITE_API_URL to your Railway backend URL
```

**Railway:**
1. Create second service in the same project
2. Set Root Directory to `frontend`
3. Set `VITE_API_URL` to your backend Railway URL

---

## Running Tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

---

## Project Structure

```
shl-recommender/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── chat.py          # POST /chat endpoint
│   │   │   └── health.py        # GET /health endpoint
│   │   ├── core/
│   │   │   ├── config.py        # Pydantic settings
│   │   │   └── logging.py       # Structlog configuration
│   │   ├── models/
│   │   │   └── schemas.py       # Request/response models
│   │   ├── services/
│   │   │   ├── agent.py         # LangChain AI agent
│   │   │   ├── llm_provider.py  # LLM abstraction (OpenAI/Groq/Gemini)
│   │   │   └── vector_store.py  # FAISS/ChromaDB retrieval
│   │   └── main.py              # FastAPI app factory
│   ├── tests/
│   │   └── test_api.py          # Pytest test suite
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── App.jsx           # Root layout
│   │   │   ├── ChatMessage.jsx   # Message bubble
│   │   │   ├── ChatInput.jsx     # Input bar
│   │   │   ├── AssessmentCard.jsx # Recommendation card
│   │   │   ├── Sidebar.jsx       # Nav sidebar
│   │   │   ├── WelcomeScreen.jsx # Empty state
│   │   │   └── TypingIndicator.jsx
│   │   ├── hooks/
│   │   │   ├── useChat.js        # Conversation state
│   │   │   └── useTheme.js       # Dark/light mode
│   │   ├── utils/
│   │   │   └── api.js            # API client
│   │   └── styles/
│   │       └── globals.css       # Tailwind + custom CSS
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── package.json
│
├── data/
│   ├── shl_catalog.json          # Scraped/curated catalog
│   ├── faiss_index/              # FAISS vector index
│   └── chroma/                   # ChromaDB (if used)
│
├── scripts/
│   ├── scrape_catalog.py         # SHL catalog scraper
│   └── generate_embeddings.py    # Embedding pipeline
│
├── docker-compose.yml
├── railway.json
├── setup.sh
└── README.md
```

---

## Customization

### Adding more assessments

Edit `scripts/scrape_catalog.py` → `get_fallback_catalog()` to add more entries, then re-run `generate_embeddings.py`.

### Changing the LLM

Set `LLM_PROVIDER` env var to `openai`, `groq`, `gemini`, or `openrouter` and provide the corresponding API key.

### Using local embeddings (no OpenAI key needed)

```bash
pip install sentence-transformers
```

Set `EMBEDDING_PROVIDER=local` — uses `all-MiniLM-L6-v2` locally.

---

## License

MIT
