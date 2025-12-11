# RAG-Anything FastAPI Service

A FastAPI application that provides a REST API and MCP server for Retrieval Augmented Generation (RAG) using the [RAG-Anything](https://github.com/HKUDS/RAG-Anything) library. Built with **hexagonal architecture** for maintainability and testability.

## Features

- 🔍 **Multi-modal document processing** (PDF, DOCX, PPTX, Images, etc.)
- 📁 **Batch folder indexing** with recursive directory support
- 🎯 **Advanced query controls** with runtime parameters
- 🧩 **Granular context retrieval** (chunks, entities, relationships)
- 🔌 **MCP server** for Claude Desktop integration
- 🐘 **PostgreSQL backend** with vector and graph storage
- ⚙️ **Configurable similarity threshold** via environment variables
- 🏗️ **Hexagonal architecture** with clean separation of concerns

## Architecture

The application follows **hexagonal architecture** (ports and adapters pattern):

```
src/
├── domain/          # Business logic (entities, ports, services)
├── application/     # Use cases, DTOs, API routes
└── infrastructure/  # External adapters (RAG, database, config)
```

This design ensures:

- **Testability**: Each layer can be tested independently
- **Maintainability**: Clear separation of concerns
- **Flexibility**: Easy to swap implementations without affecting business logic

## Prerequisites

- **Python 3.13 or higher** (uses modern Python features)
- **PostgreSQL** with pgvector and Apache AGE extensions
- An [OpenRouter](https://openrouter.ai/) API Key

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/mcp-raganything.git
    cd mcp-raganything
    ```

2. **Install dependencies using uv:**

    ```bash
    uv sync
    ```

3. **Set up PostgreSQL:**

    Use Docker Compose or install PostgreSQL with required extensions manually.

    ```bash
    docker-compose up -d  # If using Docker Compose
    ```

## Docker Deployment (Recommended)

### Quick Start with Docker Compose

1. **Create your environment file:**

    ```bash
    cp .env.example .env.docker
    # Edit .env.docker and add your OPEN_ROUTER_API_KEY
    # Make sure POSTGRES_HOST=postgres (Docker service name)

    cp .env.lightrag.server.example .env.lightrag.server
    # Edit .env.lightrag.server and add your LLM_BINDING_API_KEY
    ```

2. **Start all services:**

    ```bash
    docker-compose up -d
    ```

    This will start:
    - PostgreSQL with pgvector and Apache AGE extensions
    - RAG-Anything API on port 8000
    - LightRAG Server with Web UI on port 9621

3. **Check service health:**

    ```bash
    docker-compose ps
    curl http://localhost:8000/api/v1/health
    curl http://localhost:9621/health
    ```

4. **Access LightRAG Web UI:**

    Open `http://localhost:9621` in your browser to access the LightRAG Web UI for:
    - Document indexing and management
    - Knowledge graph exploration
    - RAG query interface

5. **View logs:**

    ```bash
    docker-compose logs -f api
    docker-compose logs -f lightrag-server
    ```

6. **Stop services:**

    ```bash
    docker-compose down
    ```

### LightRAG Server

The LightRAG Server provides a standalone Web UI and API for RAG operations. It shares the same PostgreSQL database as the main API.

**Features:**
- 📊 Web UI for document management and knowledge graph visualization
- 🔍 Interactive RAG query interface
- 🔌 Ollama-compatible API for integration with Open WebUI
- 📈 Swagger API documentation at `http://localhost:9621/docs`

**Configuration:** See `.env.lightrag.server.example` for all available options.

### Docker Commands

```bash
# Build images
docker-compose build

# Start in foreground (see logs)
docker-compose up

# Restart specific service
docker-compose restart api

# Remove all containers and volumes
docker-compose down -v
```

## Configuration

Create a `.env` file in the root directory with the following variables:

```env
# OpenRouter API Configuration
OPEN_ROUTER_API_KEY=your_openrouter_api_key_here
OPEN_ROUTER_API_URL=https://openrouter.ai/api/v1

# PostgreSQL Configuration
POSTGRES_USER=raganything
POSTGRES_PASSWORD=raganything
POSTGRES_DATABASE=raganything
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Model Configuration
CHAT_MODEL=openai/gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIM=1536
MAX_TOKEN_SIZE=8192
VISION_MODEL=openai/gpt-4o

# Data Processing Configuration
ENABLE_IMAGE_PROCESSING=True
ENABLE_TABLE_PROCESSING=True
ENABLE_EQUATION_PROCESSING=True

# LightRAG Configuration
RAG_STORAGE_TYPE=postgres # 'postgres' (uses PGVector/AGE) or 'local' (uses NanoVectorDB/Json)
COSINE_THRESHOLD=0.2  # Similarity threshold (0.0-1.0, default: 0.2)
MAX_CONCURRENT_FILES=1  # Number of files to process concurrently

# Server Configuration
MCP_TRANSPORT=sse # 'stdio', 'sse', or 'streamable'
ALLOWED_ORIGINS=["*"] # List of allowed origins for CORS
HOST=0.0.0.0 # Server host
PORT=8000 # Server port
```

### COSINE_THRESHOLD Guide

- **0.0 - 0.1**: Very permissive (more results, less strict)
- **0.2** (default): Balanced for general use
- **0.3 - 0.5**: Strict (fewer, more precise results)
- **0.6 - 1.0**: Very strict (exact matches only)

## Usage

### Starting the HTTP Server

```bash
uv run uvicorn main:app --reload --port 8004
```

The API will be available at `http://127.0.0.1:8004`.

**API Documentation**: Visit `http://127.0.0.1:8004/docs` for interactive Swagger UI.

### Starting the MCP Server (for Claude Desktop)

```bash
uv run python main.py
```

## API Endpoints

All endpoints use the `/api/v1` prefix.

### 1. Index a Single Document (`POST /api/v1/index`)

Upload and process a single document into the knowledge base (background processing).

```bash
curl -X POST "http://127.0.0.1:8004/api/v1/index" \
     -F "file=@/path/to/document.pdf"
```

**Response** (HTTP 202 Accepted):
```json
{
  "status": "accepted",
  "message": "File indexing started in background"
}
```

### 2. Index a Folder (`POST /api/v1/index-folder`)

Process all documents in a folder in the background (supports recursive directory traversal).

```bash
curl -X POST "http://127.0.0.1:8004/api/v1/index-folder" \
     -H "Content-Type: application/json" \
     -d '{
           "folder_path": "/path/to/documents",
           "recursive": true,
           "file_extensions": [".pdf", ".docx"]
         }'
```

**Response** (HTTP 202 Accepted):
```json
{
  "status": "accepted",
  "message": "Folder indexing started in background"
}
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `folder_path` | string | required | Absolute path to folder |
| `recursive` | boolean | `true` | Process subdirectories |
| `file_extensions` | array | `null` | Filter specific file types (e.g., `[".pdf", ".docx"]`) |
| `display_stats` | boolean | `true` | Show processing statistics |

### 3. Query (`POST /api/v1/query`)

Query the knowledge base with advanced controls.

#### Basic Query

```bash
curl -X POST "http://127.0.0.1:8004/api/v1/query" \
     -H "Content-Type: application/json" \
     -d '{
           "query": "What are the main findings?",
           "mode": "hybrid"
         }'
```

#### Get Only Context (No LLM Generation)

```bash
curl -X POST "http://127.0.0.1:8004/api/v1/query" \
     -H "Content-Type: application/json" \
     -d '{
           "query": "What are the main findings?",
           "only_need_context": true,
           "chunk_top_k": 10
         }'
```

#### Advanced Query with All Parameters

```bash
curl -X POST "http://127.0.0.1:8004/api/v1/query" \
     -H "Content-Type: application/json" \
     -d '{
           "query": "Explain the methodology",
           "mode": "local",
           "top_k": 40,
           "chunk_top_k": 20,
           "enable_rerank": true,
           "include_references": true
         }'
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | The question to ask |
| `mode` | string | `"hybrid"` | Query mode (see [Query Modes](#query-modes) below) |
| `stream` | boolean | `false` | Enable streaming response |
| `only_need_context` | boolean | `false` | Return only chunks/entities (no LLM) |
| `only_need_prompt` | boolean | `false` | Return constructed prompt only |
| `top_k` | integer | `40` | Number of entities/relations to retrieve |
| `chunk_top_k` | integer | `20` | Number of chunks to retrieve |
| `enable_rerank` | boolean | `true` | Enable result reranking |
| `include_references` | boolean | `false` | Include sources in response |

#### Query Modes

Choose the appropriate mode based on your use case:

| Mode | Best For | Returns | Description |
|------|----------|---------|-------------|
| `local` | Specific entity lookups | Entities + related chunks | Focuses on entities and their related chunks based on **low-level keywords**. Best for precise, targeted queries about specific concepts. |
| `global` | High-level questions | Relationships + connected entities | Focuses on relationships and their connected entities based on **high-level keywords**. Best for understanding connections and themes. |
| `hybrid` | General questions | Combined local + global | Combines local and global results using **round-robin merging**. Recommended default for most queries. |
| `mix` | Comprehensive retrieval | KG data + vector chunks | Includes knowledge graph data **plus** vector-retrieved document chunks. Most comprehensive but potentially slower. |
| `naive` | Simple vector search | Chunks only | Only vector-retrieved chunks; **entities and relationships arrays are empty**. Fastest mode, good for simple document search. |
| `bypass` | Direct LLM queries | Empty data arrays | All data arrays are empty; query goes directly to LLM without retrieval. Use for general questions not requiring document context. |

**Response Structure:**

```json
{
  "status": "success",
  "message": "Query executed successfully",
  "answer": "LLM generated response...",
  "data": {
    "entities": [
      {
        "entity_name": "Entity Name",
        "entity_type": "CONCEPT",
        "description": "Entity description",
        "source_id": "chunk-abc123",
        "file_path": "/path/to/document.pdf",
        "created_at": 1765266671,
        "reference_id": {"ref": "1"}
      }
    ],
    "relationships": [
      {
        "src_id": "Source Entity",
        "tgt_id": "Target Entity",
        "description": "Relationship description",
        "keywords": "related, connected",
        "weight": 1.0,
        "source_id": "chunk-abc123",
        "file_path": "/path/to/document.pdf",
        "created_at": 1765266671,
        "reference_id": {"ref": "1"}
      }
    ],
    "chunks": [
      {
        "content": "Document text content...",
        "file_path": "/path/to/document.pdf",
        "chunk_id": "chunk-abc123",
        "reference_id": "1"
      }
    ],
    "references": [
      {
        "reference_id": "1",
        "file_path": "/path/to/document.pdf"
      }
    ]
  },
  "metadata": {
    "query_mode": "hybrid",
    "keywords": {
      "high_level": ["concept", "theme"],
      "low_level": ["specific", "term"]
    },
    "processing_info": {
      "total_entities_found": 50,
      "total_relations_found": 30,
      "entities_after_truncation": 20,
      "relations_after_truncation": 15,
      "merged_chunks_count": 25,
      "final_chunks_count": 10
    }
  }
}
```

> **Note:** The `processing_info` field is optional and may not be present in all responses, especially when the query result is empty or in `bypass`/`naive` modes.

**Context-Only Response** (`only_need_context=true`):

Returns the same structure but without the `answer` field (no LLM generation).

### 4. Health Check (`GET /api/v1/health`)

```bash
curl http://127.0.0.1:8004/api/v1/health
```

**Response:**

```json
{
  "message": "RAG Anything API is running"
}
```

## MCP Server (Claude Desktop Integration)

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

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
        "main.py"
      ],
      "env": {
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

Restart Claude Desktop to activate the MCP server.

## Project Structure

```
mcp-raganything/
├── main.py                    # FastAPI application entry point
├── src/
│   ├── config.py              # Configuration classes
│   ├── dependencies.py        # Dependency injection
│   ├── domain/                # Business logic layer
│   │   ├── entities/          # Domain entities (QueryResult, IndexingResult)
│   │   └── ports/             # Interfaces (RAGEnginePort)
│   ├── application/           # Application layer
│   │   ├── requests/          # Request DTOs
│   │   ├── use_cases/         # Use case implementations
│   │   └── api/               # FastAPI routes and MCP tools
│   └── infrastructure/        # Infrastructure layer
│       └── rag/               # LightRAG adapter
├── pyproject.toml             # Project dependencies
└── .env                       # Environment configuration
```

## Use Cases

### Query Mode Selection Guide

| Scenario | Recommended Mode | Reason |
|----------|------------------|--------|
| "What is X?" (specific concept) | `local` | Targets specific entities |
| "How does X relate to Y?" | `global` | Focuses on relationships |
| General knowledge questions | `hybrid` | Balances both approaches |
| Full document search with KG | `mix` | Most comprehensive |
| Simple keyword/semantic search | `naive` | Fast, no KG overhead |
| Chat without document context | `bypass` | Direct LLM access |

### Retrieval-Only (Without LLM Generation)

Perfect for:

- Building custom prompts with retrieved context
- Integrating with your own LLM
- Debugging retrieval quality
- Cost optimization (no LLM API calls)

```bash
curl -X POST "http://127.0.0.1:8004/api/v1/query" \
     -H "Content-Type: application/json" \
     -d '{
           "query": "your question",
           "only_need_context": true,
           "chunk_top_k": 20
         }'
```

### Knowledge Graph Exploration

```bash
curl -X POST "http://127.0.0.1:8004/api/v1/query" \
     -H "Content-Type: application/json" \
     -d '{
           "query": "specific entity name",
           "only_need_context": true,
           "include_references": true
         }'
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src
```

### Code Quality

```bash
# Format code
uv run black src/

# Type checking
uv run mypy src/
```

## Troubleshooting

### Rerank Warnings

If you see `WARNING: Rerank is enabled but no rerank model is configured`:

1. Disable reranking: Set `enable_rerank=false` in queries
2. Configure a rerank model in LightRAG configuration (advanced)

### Empty Context Results

If `only_need_context=true` returns empty results:

1. Lower `COSINE_THRESHOLD` in `.env` (e.g., `0.1`)
2. Increase `chunk_top_k` parameter in your query
3. Verify documents are indexed: Check PostgreSQL tables

### Server Restart Required

Changes to these variables require server restart:

- `COSINE_THRESHOLD`
- Database configuration  
- API keys
- `MAX_CONCURRENT_FILES`

### Port Already in Use

If you get "Address already in use" error:

```bash
# Kill processes on port 8004
lsof -ti:8004 | xargs kill -9

# Then restart the server
uv run uvicorn main:app --reload --port 8004
```

## Architecture Benefits

- **Domain Layer**: Pure business logic, no dependencies on frameworks
- **Application Layer**: Coordinates use cases, handles HTTP/MCP concerns
- **Infrastructure Layer**: Implements external integrations (RAG, database)
- **Dependency Injection**: All components wired through `dependencies.py`
- **Testability**: Each layer can be unit tested with mocks

## License

MIT License - see LICENSE file for details
