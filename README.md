# Middleware Assistant Chatbot - Prototype

An AI-powered chatbot for middleware operations using LangChain + FastAPI + Ollama.

## Quick Start

### Prerequisites

1. **Ollama** running locally with models:
   ```bash
   ollama pull llama3.1:8b
   ollama pull nomic-embed-text
   ```

2. **Docker** for Qdrant vector database

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Qdrant
docker-compose up -d qdrant

# Run the app
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Access

- **Chat UI**: http://localhost:8000/static/index.html
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## Features

| Feature | Tool | Status |
|---------|------|--------|
| File Status Query | file_status_tool | Mock |
| Knowledge Search (RAG) | rag_knowledge_tool | Real (Qdrant) |
| DataPower Health | datapower_health_tool | Mock |
| Queue Status | queue_status_tool | Mock |

## Sample Queries

- "What's the status of document DOC-2024-001234?"
- "How do I onboard a new partner?"
- "Check all DataPower handlers"
- "What's the depth of PARTNER_B_OUT queue?"
- "Partner B files are stuck, diagnose the issue"

## Documentation

See [SPEC.md](./SPEC.md) for complete technical specification.

## Project Structure

```
ChatBot_Lang/
├── app/
│   ├── main.py           # FastAPI entry
│   ├── config.py         # Settings
│   ├── api/              # WebSocket + REST
│   ├── agent/            # LangChain agent
│   ├── tools/            # Tool implementations
│   ├── ingestion/        # RAG pipeline
│   ├── mocks/            # Mock data
│   └── session/          # Session management
├── static/               # Chat UI
├── sample_docs/          # Sample .docx files
├── docker-compose.yml
├── requirements.txt
├── SPEC.md
└── README.md
```
