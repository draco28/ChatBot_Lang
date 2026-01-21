# Middleware Assistant Chatbot - Specification Document

## Project Overview

Build a prototype AI-powered chatbot for middleware operations that allows business users to:
1. Check file/document processing status in middleware systems
2. Query internal documentation (SOPs, Ops Manuals) via RAG
3. Check DataPower handler health status
4. Monitor IBM MQ queue status

This is a **prototype** that simulates the production environment. External systems (MySQL, DataPower, IBM MQ) will be **mocked** for development purposes.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend Framework** | Python FastAPI |
| **AI Framework** | LangChain |
| **LLM** | Ollama (Llama 3.1 or any available model) |
| **Embeddings** | Ollama (nomic-embed-text) |
| **Vector Database** | Qdrant (Docker) |
| **Communication** | WebSocket (streaming) + REST API |
| **Session Memory** | In-memory (per session) |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CHATBOT UI                               │
│                    (Simple HTML/JS Client)                      │
└─────────────────────────────┬───────────────────────────────────┘
                              │ WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI SERVER                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    WebSocket Handler                      │  │
│  │                    /ws/chat                               │  │
│  └───────────────────────────┬───────────────────────────────┘  │
│                              │                                  │
│  ┌───────────────────────────▼───────────────────────────────┐  │
│  │                   LANGCHAIN AGENT                         │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  AgentExecutor                                      │  │  │
│  │  │  ├─ LLM: ChatOllama                                 │  │  │
│  │  │  ├─ Tools: [4 tools]                                │  │  │
│  │  │  ├─ Memory: ConversationBufferWindowMemory          │  │  │
│  │  │  └─ Callbacks: WebSocketStreamHandler               │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                  │
│         ┌────────────────────┼────────────────────┐             │
│         ▼                    ▼                    ▼             │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐      │
│  │ file_status │      │ rag_query   │      │ dp_health   │      │
│  │ _tool       │      │ _tool       │      │ _tool       │      │
│  │ (MOCK)      │      │ (Qdrant)    │      │ (MOCK)      │      │
│  └─────────────┘      └─────────────┘      └─────────────┘      │
│         │                    │                    │             │
│         │             ┌─────────────┐             │             │
│         │             │queue_status │             │             │
│         │             │_tool (MOCK) │             │             │
│         │             └─────────────┘             │             │
└─────────┼────────────────────┼────────────────────┼─────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
    [Mock Data]           [Qdrant DB]         [Mock Data]
```

---

## Project Structure

```
ChatBot_Lang/
│
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Configuration settings
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── websocket.py           # WebSocket chat endpoint
│   │   └── rest.py                # REST endpoints (health, ingest, docs)
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── setup.py               # LangChain agent setup
│   │   ├── prompts.py             # System prompts
│   │   └── callbacks.py           # WebSocket streaming callback
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── file_status.py         # File status tool (MOCK)
│   │   ├── rag_knowledge.py       # RAG retrieval tool
│   │   ├── datapower_health.py    # DataPower health tool (MOCK)
│   │   └── queue_status.py        # Queue status tool (MOCK)
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   └── pipeline.py            # Document ingestion pipeline
│   │
│   ├── mocks/
│   │   ├── __init__.py
│   │   ├── data.py                # Mock data definitions
│   │   └── generators.py          # Mock response generators
│   │
│   └── session/
│       ├── __init__.py
│       └── manager.py             # Session & memory management
│
├── static/
│   └── index.html                 # Simple chat UI for testing
│
├── sample_docs/
│   ├── partner_onboarding_sop.docx
│   └── operations_manual.docx
│
├── tests/
│   ├── __init__.py
│   ├── test_tools.py
│   └── test_agent.py
│
├── docker-compose.yml             # Qdrant + App
├── Dockerfile
├── requirements.txt
├── config.yaml
├── SPEC.md                        # This file
└── README.md
```

---

## Component Specifications

### 1. Configuration (config.py)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_CHAT_MODEL: str = "llama3.1:8b"  # Use 8b for prototype
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"
    
    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "middleware_knowledge"
    
    # Session
    MAX_HISTORY_MESSAGES: int = 10
    SESSION_TIMEOUT_MINUTES: int = 60
    
    class Config:
        env_file = ".env"
```

---

### 2. Tools Specification

#### 2.1 file_status_tool (MOCK)

**Purpose**: Simulate querying ACE middleware database for file status.

**Input Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| document_id | string | No | Unique document/file identifier |
| queue_name | string | No | Source or destination queue name |
| ean_code | string | No | Target/destination EAN code |
| start_date | string | No | Search from date (YYYY-MM-DD) |
| end_date | string | No | Search until date (YYYY-MM-DD) |

**Mock Response Schema**:
```json
{
  "success": true,
  "record_count": 2,
  "records": [
    {
      "document_id": "DOC-2024-001234",
      "status": "DELIVERED",
      "source_queue": "PARTNER_A_IN",
      "dest_queue": "PARTNER_B_OUT",
      "ean_code": "5012345678901",
      "received_at": "2024-01-15T10:30:00Z",
      "processed_at": "2024-01-15T10:30:05Z",
      "delivered_at": "2024-01-15T10:30:10Z",
      "error_message": null
    }
  ]
}
```

**Mock Data Scenarios**:
- Document found with status: RECEIVED, PROCESSING, DELIVERED, ERROR
- Multiple documents matching queue/EAN
- No documents found
- Error status with error_message

---

#### 2.2 rag_knowledge_tool (REAL - Qdrant)

**Purpose**: Search internal documentation via RAG.

**Input Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| query | string | Yes | Natural language search query |
| doc_type | string | No | Filter: "SOP", "OPS_MANUAL", "ALL" |
| top_k | int | No | Number of results (default: 5) |

**Response Schema**:
```json
{
  "success": true,
  "chunks_retrieved": 3,
  "context": "Combined relevant text...",
  "sources": [
    {
      "doc_title": "Partner Onboarding SOP",
      "section": "3.2 Connection Setup",
      "relevance_score": 0.89
    }
  ]
}
```

---

#### 2.3 datapower_health_tool (MOCK)

**Purpose**: Simulate checking DataPower handler status.

**Input Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| handler_name | string | No | Specific handler to check |
| domain | string | No | DataPower domain name |
| check_type | string | No | "specific_handler", "all_handlers" |

**Mock Response Schema**:
```json
{
  "success": true,
  "domain": "PROD_DOMAIN",
  "check_time": "2024-01-15T10:30:00Z",
  "handlers": [
    {
      "name": "PARTNER_A_HANDLER",
      "type": "MultiProtocolGateway",
      "status": "up",
      "admin_state": "enabled",
      "op_state": "up",
      "connection_count": 15
    },
    {
      "name": "PARTNER_B_HANDLER",
      "type": "MultiProtocolGateway", 
      "status": "down",
      "admin_state": "enabled",
      "op_state": "down",
      "last_error": "Connection refused to backend"
    }
  ],
  "summary": {
    "total": 10,
    "up": 8,
    "down": 2
  }
}
```

**Mock Data Scenarios**:
- All handlers up
- Some handlers down
- Specific handler status
- Handler with degraded performance

---

#### 2.4 queue_status_tool (MOCK)

**Purpose**: Simulate checking IBM MQ queue status.

**Input Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| queue_name | string | No | Specific queue to check (supports wildcards) |
| queue_manager | string | No | Queue manager name |
| include_metrics | bool | No | Include depth, rates (default: true) |

**Mock Response Schema**:
```json
{
  "success": true,
  "queue_manager": "QM_PROD_01",
  "check_time": "2024-01-15T10:30:00Z",
  "queues": [
    {
      "name": "PARTNER_A_IN",
      "type": "LOCAL",
      "depth": 5,
      "max_depth": 5000,
      "status": "normal",
      "oldest_message_age_seconds": 120,
      "open_input_count": 2,
      "open_output_count": 3
    },
    {
      "name": "PARTNER_B_OUT",
      "type": "LOCAL",
      "depth": 450,
      "max_depth": 5000,
      "status": "warning",
      "oldest_message_age_seconds": 3600,
      "open_input_count": 5,
      "open_output_count": 1
    }
  ],
  "alerts": [
    {
      "queue": "PARTNER_B_OUT",
      "alert_type": "HIGH_DEPTH",
      "message": "Queue depth 450 exceeds warning threshold 100"
    }
  ]
}
```

**Mock Data Scenarios**:
- Normal queue status
- Warning (high depth)
- Critical (near max depth)
- Queue with stuck messages (high age)
- Queue with no consumers

---

### 3. WebSocket Protocol

**Endpoint**: `ws://localhost:8000/ws/chat`

**Connection Flow**:
```
Client                              Server
  │                                   │
  │──── Connect ─────────────────────►│
  │                                   │
  │◄─── {"type": "connected",         │
  │      "session_id": "xxx"} ────────│
  │                                   │
  │──── {"type": "message",           │
  │      "content": "..."} ──────────►│
  │                                   │
  │◄─── {"type": "status",            │
  │      "status": "thinking"} ───────│
  │                                   │
  │◄─── {"type": "tool_start",        │
  │      "tool": "file_status_tool",  │
  │      "input": "..."} ─────────────│
  │                                   │
  │◄─── {"type": "tool_end",          │
  │      "tool": "file_status_tool",  │
  │      "success": true} ────────────│
  │                                   │
  │◄─── {"type": "stream",            │
  │      "content": "token"} ─────────│  (repeated)
  │                                   │
  │◄─── {"type": "stream_end"} ───────│
  │                                   │
```

**Message Types**:

Client → Server:
- `message`: User chat message
- `ping`: Keep-alive

Server → Client:
- `connected`: Connection established with session_id
- `status`: Processing status (thinking, processing)
- `tool_start`: Tool execution started
- `tool_end`: Tool execution completed
- `stream`: Streamed response token
- `stream_end`: Response complete
- `error`: Error occurred

---

### 4. REST API Endpoints

#### GET /api/health
Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "components": {
    "ollama": "connected",
    "qdrant": "connected"
  }
}
```

---

#### POST /api/ingest
Upload and ingest a document.

**Request**: `multipart/form-data`
- `file`: .docx file
- `doc_type`: "SOP" | "OPS_MANUAL"
- `doc_id`: (optional) Custom document ID
- `version`: (optional) Document version

**Response**:
```json
{
  "success": true,
  "doc_id": "doc_12345",
  "doc_title": "Partner Onboarding SOP",
  "chunks_created": 15,
  "processing_time_ms": 3500
}
```

---

#### GET /api/documents
List ingested documents.

**Response**:
```json
{
  "documents": [
    {
      "doc_id": "doc_12345",
      "doc_title": "Partner Onboarding SOP",
      "doc_type": "SOP",
      "chunk_count": 15,
      "ingested_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

#### DELETE /api/documents/{doc_id}
Remove a document from the knowledge base.

**Response**:
```json
{
  "success": true,
  "doc_id": "doc_12345",
  "chunks_deleted": 15
}
```

---

### 5. Document Ingestion Pipeline

**Flow**:
```
.docx file
    │
    ▼
┌─────────────────────┐
│  Docx2txtLoader     │  (LangChain)
│  Extract text       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  RecursiveCharacter │  (LangChain)
│  TextSplitter       │
│  - chunk_size: 600  │
│  - overlap: 80      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Add Metadata       │
│  - doc_id           │
│  - doc_type         │
│  - doc_title        │
│  - chunk_index      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  OllamaEmbeddings   │  (LangChain)
│  nomic-embed-text   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  QdrantVectorStore  │  (LangChain)
│  add_documents()    │
└─────────────────────┘
```

**Chunking Configuration**:
```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=80,
    separators=["\n\n", "\n", ". ", " ", ""],
    length_function=len
)
```

---

### 6. LangChain Agent Setup

**Components**:

```python
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory

# LLM
llm = ChatOllama(
    model="llama3.1:8b",
    base_url="http://localhost:11434",
    temperature=0,
    streaming=True
)

# Tools
tools = [
    file_status_tool,
    rag_knowledge_tool,
    datapower_health_tool,
    queue_status_tool
]

# Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

# Agent
agent = create_tool_calling_agent(llm, tools, prompt)

# Executor
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=5
)
```

---

### 7. System Prompt

```
You are an AI assistant for middleware operations at a large enterprise. You help business users with:

1. **File/Document Status**: Check the processing status of files in the middleware system
2. **Knowledge Queries**: Answer questions about procedures, workflows, and partner connections using internal documentation (SOPs, Ops Manuals)
3. **System Health**: Check DataPower handler status and IBM MQ queue health

## Available Tools:

- **file_status_tool**: Query file/document processing status. Use when user asks about:
  - "What's the status of document X?"
  - "Where is my file?"
  - "Show files for queue Y"
  - "Files processed today"

- **rag_knowledge_tool**: Search internal documentation. Use when user asks about:
  - "How do I onboard a new partner?"
  - "What's the process for X?"
  - "Explain the workflow for Y"
  - Questions about procedures, SOPs, or operations

- **datapower_health_tool**: Check DataPower handler status. Use when user asks about:
  - "Is handler X running?"
  - "Check DataPower health"
  - "Why is partner connection down?"

- **queue_status_tool**: Check IBM MQ queue status. Use when user asks about:
  - "What's the depth of queue X?"
  - "Are there stuck messages?"
  - "Check queue health"
  - "Why are messages not processing?"

## Guidelines:

1. Always use the appropriate tool to get real-time information
2. If the user's request is unclear, ask for clarification
3. For complex issues (e.g., "partner files are stuck"), use multiple tools to diagnose
4. Provide concise, actionable responses
5. If a tool returns an error, explain the issue and suggest next steps
6. When reporting status, include relevant details (timestamps, counts, etc.)

Be helpful, professional, and concise.
```

---

### 8. Mock Data Definitions

Located in `app/mocks/data.py`:

```python
# Sample file records
MOCK_FILE_RECORDS = [
    {
        "document_id": "DOC-2024-001234",
        "status": "DELIVERED",
        "source_queue": "PARTNER_A_IN",
        "dest_queue": "PARTNER_B_OUT",
        "ean_code": "5012345678901",
        "received_at": "2024-01-15T10:30:00Z",
        "processed_at": "2024-01-15T10:30:05Z",
        "delivered_at": "2024-01-15T10:30:10Z",
        "error_message": None
    },
    {
        "document_id": "DOC-2024-001235",
        "status": "ERROR",
        "source_queue": "PARTNER_C_IN",
        "dest_queue": "PARTNER_D_OUT",
        "ean_code": "5012345678902",
        "received_at": "2024-01-15T11:00:00Z",
        "processed_at": "2024-01-15T11:00:05Z",
        "delivered_at": None,
        "error_message": "Validation failed: Invalid EAN format"
    },
    # ... more records
]

# Sample DataPower handlers
MOCK_HANDLERS = [
    {
        "name": "PARTNER_A_HANDLER",
        "type": "MultiProtocolGateway",
        "status": "up",
        "admin_state": "enabled",
        "op_state": "up",
        "connection_count": 15
    },
    {
        "name": "PARTNER_B_HANDLER",
        "type": "MultiProtocolGateway",
        "status": "down",
        "admin_state": "enabled",
        "op_state": "down",
        "last_error": "Connection refused to backend"
    },
    # ... more handlers
]

# Sample MQ queues
MOCK_QUEUES = [
    {
        "name": "PARTNER_A_IN",
        "type": "LOCAL",
        "depth": 5,
        "max_depth": 5000,
        "status": "normal",
        "oldest_message_age_seconds": 120
    },
    {
        "name": "PARTNER_B_OUT",
        "type": "LOCAL",
        "depth": 450,
        "max_depth": 5000,
        "status": "warning",
        "oldest_message_age_seconds": 3600
    },
    # ... more queues
]
```

---

### 9. Sample Documents for RAG

Create sample `.docx` files in `sample_docs/`:

#### partner_onboarding_sop.docx
```
Partner Onboarding SOP
Version 2.1

1. Introduction
This document describes the standard operating procedure for onboarding new trading partners into the middleware system.

2. Prerequisites
- Partner agreement signed
- Technical specifications received
- Connection type determined (AS2, SFTP, API)

3. Partner Setup
3.1 Initial Configuration
Create partner profile in the admin console...

3.2 Connection Setup
For AS2 connections:
1. Obtain partner's AS2 ID
2. Exchange certificates
3. Configure endpoint URL
...

3.3 Testing Procedures
After connection setup, conduct the following tests:
1. Connectivity test
2. Message format validation
3. End-to-end transaction test
...

4. Go-Live Checklist
- [ ] All tests passed
- [ ] Partner sign-off received
- [ ] Monitoring alerts configured
- [ ] Documentation updated
```

#### operations_manual.docx
```
Middleware Operations Manual
Version 3.0

1. System Overview
The middleware system processes B2B transactions between trading partners...

2. Daily Operations
2.1 Morning Health Check
- Check all DataPower handlers
- Verify queue depths are normal
- Review overnight error logs

2.2 Monitoring Dashboards
Access the monitoring dashboard at...

3. Troubleshooting Guide
3.1 Files Not Processing
1. Check source queue depth
2. Verify handler is running
3. Check error logs for validation failures

3.2 Partner Connection Issues
1. Verify certificate validity
2. Check network connectivity
3. Review DataPower logs
...

4. Escalation Procedures
Level 1: On-call support
Level 2: Middleware team lead
Level 3: Architecture team
```

---

### 10. Simple Chat UI (static/index.html)

A minimal HTML/JS interface for testing:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Middleware Assistant</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        #chat-container { border: 1px solid #ccc; height: 400px; overflow-y: auto; padding: 10px; margin-bottom: 10px; }
        .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .user { background: #e3f2fd; text-align: right; }
        .assistant { background: #f5f5f5; }
        .tool-status { background: #fff3e0; font-size: 0.9em; font-style: italic; }
        #input-container { display: flex; gap: 10px; }
        #user-input { flex: 1; padding: 10px; }
        button { padding: 10px 20px; cursor: pointer; }
        .streaming { border-left: 3px solid #4caf50; }
    </style>
</head>
<body>
    <h1>🤖 Middleware Assistant</h1>
    <div id="chat-container"></div>
    <div id="input-container">
        <input type="text" id="user-input" placeholder="Ask about file status, procedures, or system health..." />
        <button onclick="sendMessage()">Send</button>
    </div>

    <script>
        let ws;
        let currentAssistantMessage = null;
        
        function connect() {
            ws = new WebSocket('ws://localhost:8000/ws/chat');
            
            ws.onopen = () => {
                console.log('Connected');
                addMessage('system', 'Connected to Middleware Assistant');
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                handleMessage(data);
            };
            
            ws.onclose = () => {
                console.log('Disconnected');
                setTimeout(connect, 3000);
            };
        }
        
        function handleMessage(data) {
            switch(data.type) {
                case 'connected':
                    console.log('Session:', data.session_id);
                    break;
                case 'status':
                    addMessage('tool-status', `Status: ${data.status}`);
                    break;
                case 'tool_start':
                    addMessage('tool-status', `🔧 Using ${data.tool}...`);
                    break;
                case 'tool_end':
                    addMessage('tool-status', `✅ ${data.tool} completed`);
                    break;
                case 'stream':
                    appendToCurrentMessage(data.content);
                    break;
                case 'stream_end':
                    finalizeCurrentMessage();
                    break;
                case 'error':
                    addMessage('assistant', `❌ Error: ${data.message}`);
                    break;
            }
        }
        
        function addMessage(type, content) {
            const container = document.getElementById('chat-container');
            const div = document.createElement('div');
            div.className = `message ${type}`;
            div.textContent = content;
            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
        }
        
        function appendToCurrentMessage(content) {
            if (!currentAssistantMessage) {
                const container = document.getElementById('chat-container');
                currentAssistantMessage = document.createElement('div');
                currentAssistantMessage.className = 'message assistant streaming';
                container.appendChild(currentAssistantMessage);
            }
            currentAssistantMessage.textContent += content;
            document.getElementById('chat-container').scrollTop = document.getElementById('chat-container').scrollHeight;
        }
        
        function finalizeCurrentMessage() {
            if (currentAssistantMessage) {
                currentAssistantMessage.classList.remove('streaming');
                currentAssistantMessage = null;
            }
        }
        
        function sendMessage() {
            const input = document.getElementById('user-input');
            const message = input.value.trim();
            if (message && ws.readyState === WebSocket.OPEN) {
                addMessage('user', message);
                ws.send(JSON.stringify({ type: 'message', content: message }));
                input.value = '';
            }
        }
        
        document.getElementById('user-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
        
        connect();
    </script>
</body>
</html>
```

---

### 11. Docker Compose

```yaml
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_storage:/qdrant/storage
    environment:
      - QDRANT__SERVICE__GRPC_PORT=6334

  app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - qdrant
    environment:
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
      - OLLAMA_BASE_URL=http://host.docker.internal:11434
    volumes:
      - ./sample_docs:/app/sample_docs

volumes:
  qdrant_storage:
```

---

### 12. Requirements

```
# Core
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
websockets>=12.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-multipart>=0.0.6

# LangChain
langchain>=0.1.0
langchain-core>=0.1.0
langchain-community>=0.0.10
langchain-ollama>=0.1.0
langchain-qdrant>=0.1.0

# Vector Store
qdrant-client>=1.7.0

# Document Processing
docx2txt>=0.8
python-docx>=1.1.0

# Utilities
pyyaml>=6.0
python-dotenv>=1.0.0
```

---

## Sample User Queries for Testing

| Query | Expected Tool(s) | Expected Behavior |
|-------|-----------------|-------------------|
| "What's the status of document DOC-2024-001234?" | file_status_tool | Return specific document status |
| "Show me files for queue PARTNER_A_IN" | file_status_tool | Return files for that queue |
| "How do I onboard a new partner?" | rag_knowledge_tool | Search SOPs for onboarding procedure |
| "What's the process for AS2 connection setup?" | rag_knowledge_tool | Search documentation |
| "Is PARTNER_A_HANDLER running?" | datapower_health_tool | Check specific handler |
| "Check all DataPower handlers" | datapower_health_tool | Return all handler statuses |
| "What's the depth of PARTNER_B_OUT queue?" | queue_status_tool | Return specific queue status |
| "Are there any queue alerts?" | queue_status_tool | Return queues with warnings/alerts |
| "Partner B files are stuck, what's wrong?" | queue_status_tool, datapower_health_tool, file_status_tool | Multi-tool diagnosis |
| "Good morning, can you do a health check?" | datapower_health_tool, queue_status_tool | Combined health status |

---

## Implementation Priority

### Phase 1: Core Setup
1. Project structure and configuration
2. FastAPI app with WebSocket endpoint
3. LangChain agent setup with Ollama
4. Basic streaming callback

### Phase 2: Tools
1. Mock data definitions
2. file_status_tool (mock)
3. datapower_health_tool (mock)
4. queue_status_tool (mock)

### Phase 3: RAG
1. Qdrant setup via Docker
2. Document ingestion pipeline
3. rag_knowledge_tool
4. Sample documents

### Phase 4: UI & Testing
1. Simple chat UI
2. REST endpoints
3. Integration testing
4. Documentation

---

## Success Criteria

1. ✅ WebSocket chat works with streaming responses
2. ✅ All 4 tools are callable by the agent
3. ✅ RAG retrieval returns relevant documentation
4. ✅ Mock tools return realistic responses
5. ✅ Multi-tool queries work (agent uses multiple tools)
6. ✅ Session memory maintains conversation context
7. ✅ Simple UI allows testing all features

---

## Notes for Claude Code

1. **Ollama Setup**: Ensure Ollama is running locally with `llama3.1:8b` and `nomic-embed-text` models pulled
2. **Qdrant**: Use Docker Compose to start Qdrant before running the app
3. **Async**: Use async/await throughout for WebSocket and tool execution
4. **Error Handling**: Add proper error handling for Ollama connection issues
5. **Streaming**: Use LangChain's callback system for WebSocket streaming
