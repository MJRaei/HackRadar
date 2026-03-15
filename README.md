<h1 align="center">HackRadar</h1>

<p align="center">
  <strong>AI-Powered Hackathon Judging System</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/node-18%2B-339933?style=flat-square&logo=node.js&logoColor=white" alt="Node 18+">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="MIT License">
  <img src="https://img.shields.io/badge/status-alpha-orange?style=flat-square" alt="Alpha">
  <img src="https://img.shields.io/badge/LLM-Gemini%20%7C%20OpenAI-4285F4?style=flat-square&logo=google&logoColor=white" alt="Multi-LLM">
  <img src="https://img.shields.io/badge/vector%20db-Qdrant-DC382D?style=flat-square&logo=qdrant&logoColor=white" alt="Qdrant">
</p>

<p align="center">
  HackRadar automates hackathon project evaluation using RAG-powered code analysis and AI agents.<br>
  Submit GitHub repos, define your judging criteria, and let intelligent agents score, rank, and categorize<br>
  every submission — grounded in <em>actual code</em>, not just README descriptions.
</p>

---

## Key Features

- **RAG-Powered Scoring** — AI agents retrieve relevant code snippets per criterion via semantic search, producing scores grounded in actual implementation.
- **Custom Criteria Sets** — Define weighted judging criteria with names, descriptions, and relative importance.
- **Intelligent Categorization** — Classify projects into predefined categories or let the AI discover natural clusters automatically.
- **Multi-LLM Support** — Seamlessly switch between Google Gemini, OpenAI, or any OpenAI-compatible endpoint (e.g., self-hosted models).
- **Web Search Integration** — Google Custom Search for novelty and innovation assessment during scoring.
- **Bulk Upload** — Import multiple projects at once via CSV or TXT files.
- **Rankings & Comparison** — View projects ranked by weighted overall scores with per-criterion breakdowns.
- **Full-Stack Web UI** — Modern Next.js interface for project management, judging, and visualization.

---

## How It Works

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌────────────┐
│  Submit URL  │────▶│  Clone Repo  │────▶│  Index Code  │────▶│  AI Scoring  │────▶│  Rankings  │
│  (GitHub)    │     │  & Extract   │     │  (Qdrant)    │     │  (per-criterion)   │  & Export  │
└─────────────┘     └──────────────┘     └──────────────┘     └──────────────┘     └────────────┘
```

1. **Ingest** — GitHub repos are cloned and source code is split into chunks using tree-sitter-aware code splitting.
2. **Index** — Code chunks are embedded using `allenai-specter` and stored in per-project Qdrant collections.
3. **Retrieve** — For each scoring criterion, the RAG pipeline retrieves the most relevant code snippets via semantic search.
4. **Evaluate** — An AI agent scores each criterion (0–10) with rationales grounded in the retrieved code and optional web search results.
5. **Aggregate** — Weighted scores are combined into an overall project score and ranked.

### Scoring Strategies

- **ToolCallStrategy** — For Gemini/OpenAI: the agent dynamically calls code retrieval and web search tools.
- **RAGPrefetchStrategy** — For endpoints without function calling: relevant code is prefetched and included in the prompt.

### Categorization Modes

- **Predefined** — Provide category names; the agent assigns each project to the best fit.
- **Auto-discovery** — The agent analyzes all projects and identifies natural groupings.

---

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+ (for the web interface)
- Docker & Docker Compose (for Qdrant)
- API key for at least one LLM provider

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/HackRadar.git
cd HackRadar

# Start the vector database
docker compose up -d

# Install backend dependencies (using uv, recommended)
uv sync

# Or using pip
pip install -e .

# Run database migrations
alembic upgrade head
```

### Configuration

Create a `.env` file (or copy the template):

```bash
cp .env.example .env
```

Set your LLM provider:

```env
# Google Gemini (default)
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.0-flash
GOOGLE_API_KEY=your-api-key
```

<details>
<summary><strong>All environment variables</strong></summary>

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `LLM_PROVIDER` | `gemini` | LLM provider: `gemini`, `openai`, or `openai_compatible` |
| `LLM_MODEL` | `gemini-2.0-flash` | Model name for the selected provider |
| `GOOGLE_API_KEY` | — | Google Gemini API key |
| `OPENAI_API_KEY` | — | OpenAI API key (for `openai` or `openai_compatible`) |
| `OPENAI_BASE_URL` | — | Custom base URL (for `openai_compatible`) |
| `DATABASE_URL` | `sqlite+aiosqlite:///./hackradar.db` | Database connection string |
| `QDRANT_HOST` | `localhost` | Qdrant vector database host |
| `QDRANT_PORT` | `6333` | Qdrant HTTP port |
| `EMBEDDING_MODEL` | `allenai-specter` | HuggingFace embedding model |
| `REPOS_BASE_DIR` | `./data/repos` | Directory for cloned repositories |
| `GOOGLE_SEARCH_API_KEY` | — | Google Custom Search API key (for novelty assessment) |
| `GOOGLE_SEARCH_ENGINE_ID` | — | Google Programmable Search Engine ID |

</details>

### Run

```bash
# Terminal 1 — Backend
uvicorn hackradar.main:app --reload --port 8000

# Terminal 2 — Frontend
cd hackradar-ui && npm install && npm run dev
```

Open [http://localhost:3000](http://localhost:3000) for the web UI, or [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive API docs.

---

## Project Structure

```
hackradar/                          # FastAPI backend
├── agents/                         # AI agent implementations
│   ├── llm/                        # Multi-provider LLM factory
│   ├── scoring/                    # Scoring agent, strategies, prompts
│   ├── categorization/             # Categorization agent & prompts
│   └── tools/                      # Agent tools (web search)
├── api/v1/                         # Route handlers
│   ├── projects.py                 # Project CRUD & bulk upload
│   ├── judging.py                  # Scoring & categorization
│   └── criteria.py                 # Criteria set management
├── rag/                            # RAG pipeline (ingestion, retrieval)
├── services/                       # Business logic layer
├── repositories/                   # Data access layer
├── models/                         # SQLAlchemy ORM models
├── schemas/                        # Pydantic request/response schemas
└── db/                             # Database session config

hackradar-ui/                       # Next.js frontend
├── src/app/                        # App Router pages
│   ├── dashboard/                  # Overview dashboard
│   ├── projects/                   # Project management
│   ├── criteria/                   # Criteria set management
│   └── judge/                      # Scoring, categorization, rankings
├── src/components/                 # Reusable React components
└── src/providers/                  # Context providers (React Query)

alembic/                            # Database migrations
tests/                              # Test suite
```

---

## Tech Stack

| Layer | Technology |
| ----- | ---------- |
| **Backend** | Python 3.10+, FastAPI, SQLAlchemy 2.0, Pydantic, Alembic |
| **AI / Agents** | Railtracks, LiteLLM, LlamaIndex |
| **Embeddings** | Sentence Transformers (`allenai-specter`) |
| **Vector DB** | Qdrant |
| **LLM Providers** | Google Gemini, OpenAI, OpenAI-compatible endpoints |
| **Frontend** | Next.js 16, React 19, TailwindCSS 4, React Query |
| **Database** | SQLite (dev) / PostgreSQL (prod via SQLAlchemy) |

### Supported Languages for Code Indexing

Python, TypeScript, JavaScript, Go, Rust, Java, C++, Ruby, PHP, Swift, Kotlin, C#, Solidity

---

## Development

```bash
# Run tests
pytest

# Lint & format
ruff check .
ruff format .

# Type checking
mypy hackradar

# Create a migration
alembic revision --autogenerate -m "description"
alembic upgrade head
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
