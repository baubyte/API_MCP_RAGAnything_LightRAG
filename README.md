# MCP-RAGAnything

A FastAPI application that provides a REST API and MCP server for Retrieval Augmented Generation (RAG) using the [RAG-Anything](https://github.com/HKUDS/RAG-Anything) library. Built with **hexagonal architecture** for maintainability and testability.

## Features

- 🔍 **Multi-modal document processing** — PDF, DOCX, PPTX, images, tables, equations via [Docling](https://github.com/DS4SD/docling)
- 📁 **Batch folder indexing** — Recursive directory traversal with file extension filtering
- 🔌 **LightRAG proxy** — Full pass-through to [LightRAG Server](https://github.com/HKUDS/LightRAG) for queries and knowledge graph operations
- 🤖 **MCP server** — Claude Desktop integration with `query_knowledge_base` tool
- 🐘 **PostgreSQL backend** — pgvector for embeddings + Apache AGE for knowledge graph
- 🏗️ **Hexagonal architecture** — Clean separation of domain, application, and infrastructure layers

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI App                              │
├─────────────────────────────────────────────────────────────────┤
│  Application Layer                                               │
│  ├── api/           → REST routes + MCP tools                   │
│  ├── use_cases/     → IndexFile, IndexFolder, LightRAGProxy     │
│  └── requests/      → Input DTOs (Pydantic)                     │
├─────────────────────────────────────────────────────────────────┤
│  Domain Layer (pure Python, no external imports)                │
│  ├── entities/      → IndexingResult, LightRAGProxyEntities     │
│  └── ports/         → RAGEnginePort, LightRAGProxyClientPort    │
├─────────────────────────────────────────────────────────────────┤
│  Infrastructure Layer                                            │
│  ├── rag/           → LightRAGAdapter (implements RAGEnginePort)│
│  └── proxy/         → LightRAGProxyClient (HTTP client)         │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- **Python 3.13+**
- **Docker & Docker Compose** (recommended)
- An [OpenRouter](https://openrouter.ai/) API Key

## Quick Start with Docker Compose

1. **Clone and configure:**

    ```bash
    git clone https://github.com/Kaiohz/mcp-raganything.git
    cd mcp-raganything

    # Configure the API service
    cp .env.example .env
    # Edit .env and set OPEN_ROUTER_API_KEY

    # Configure LightRAG server
    cp .env.lightrag.server.example .env.lightrag.server
    # Edit .env.lightrag.server and set LLM_BINDING_API_KEY
    ```

2. **Start all services:**

    ```bash
    docker-compose up -d
    ```

    This starts three containers:
    | Container | Port | Description |
    |-----------|------|-------------|
    | `postgres` | 5432 | PostgreSQL 16 with pgvector + Apache AGE |
    | `api` | 8000 | RAG-Anything FastAPI service |
    | `lightrag-server` | 9621 | LightRAG Server with Web UI |

3. **Verify services:**

    ```bash
    curl http://localhost:8000/api/v1/health
    curl http://localhost:9621/health
    ```

4. **Access documentation:**

    - **API Docs (Swagger):** http://localhost:8000/docs
    - **LightRAG Web UI:** http://localhost:9621
    - **LightRAG API Docs:** http://localhost:9621/docs

## Configuration

Configuration is managed via environment files. See the example files for all available options:

- **[`.env.example`](.env.example)** — Main API configuration (OpenRouter, PostgreSQL, RAG settings)
- **[`.env.lightrag.server.example`](.env.lightrag.server.example)** — LightRAG server configuration

### Key Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPEN_ROUTER_API_KEY` | — | Required. Your OpenRouter API key |
| `RAG_STORAGE_TYPE` | `postgres` | Storage backend: `postgres` or `local` |
| `COSINE_THRESHOLD` | `0.2` | Similarity threshold (0.0-1.0) |
| `MCP_TRANSPORT` | `sse` | MCP transport: `stdio`, `sse`, or `streamable` |
| `LIGHTRAG_API_URL` | `http://localhost:9621` | LightRAG server URL for proxy |

## Usage

Full API documentation is available at **http://localhost:8000/docs** (Swagger UI).

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Health check |
| `/api/v1/file/index` | POST | Index a single file (background) |
| `/api/v1/folder/index` | POST | Index a folder (background) |
| `/api/v1/lightrag/*` | ALL | Proxy to LightRAG API (query, documents, etc.) |

### Query Modes

When querying via `/api/v1/lightrag/query`:

| Mode | Description |
|------|-------------|
| `naive` | Vector search only (fast, recommended) |
| `local` | Entity-focused search |
| `global` | Relationship-focused search |
| `hybrid` | Combines local + global |
| `mix` | Knowledge graph + vector chunks |
| `bypass` | Direct LLM query without retrieval |

## MCP Server (Claude Desktop Integration)

The MCP server exposes a `query_knowledge_base` tool for searching the RAG knowledge base.

### Tool: `query_knowledge_base`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | The search query |
| `mode` | string | `"naive"` | Search mode: `naive`, `local`, `global`, `hybrid` |
| `top_k` | integer | `10` | Number of chunks to retrieve |
| `only_need_context` | boolean | `true` | Return only context (no LLM answer) |

### Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "raganything": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/mcp-raganything",
        "python",
        "-m",
        "src.main"
      ],
      "env": {
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

Restart Claude Desktop to activate.

## Development

```bash
uv sync                        # Install dependencies
uv run python src/main.py      # Run locally
uv run pytest --cov=src        # Run tests with coverage
uv run black src/              # Format code
uv run mypy src/               # Type checking
```

```bash
docker-compose build           # Build images
docker-compose up              # Start in foreground
docker-compose logs -f api     # View logs
docker-compose down -v         # Stop and remove volumes
```

## Troubleshooting

- **Empty results:** Lower `COSINE_THRESHOLD` (e.g., `0.1`) or increase `top_k`
- **Port conflicts:** `lsof -ti:8000 | xargs kill -9`
- **Config changes:** Restart server after changing `COSINE_THRESHOLD`, database config, or API keys

## License

MIT License - see LICENSE file for details
