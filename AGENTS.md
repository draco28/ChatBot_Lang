# ChatBot_Lang - OpenCode Workflow Guide

**Project ID**: 8
**MCP Server**: https://projectpulsemcp.dracodev.dev/mcp
**Dashboard**: https://projectpulse.dracodev.dev/

---

## Quick Start

Initialize the project session:
```bash
/init
```

Chat with the agent:
```
"Implement the user authentication feature"
"Fix the bug in the search API"
```

---

## 🚀 Daily Workflow

### 1. Load Context (Crucial)
Start every session by loading the project context from ProjectPulse:
```javascript
projectpulse_context_load({ projectId: 8 })
```
This loads the project brief, tech stack, and active tasks into memory.

### 2. Manage Tasks
Use the ProjectPulse ticket system to track work:
```javascript
// Find your tickets
projectpulse_ticket_search({ sprintNumber: 1, status: ["todo"] })

// Start a session for a ticket
projectpulse_agent_session_start({
  projectId: 8,
  name: "Implement Feature X",
  activeTicketIds: [123]
})
```

---

## 🤖 Specialized Agents
We have specialized agents available as subagents. Invoke them with `@` or let the main agent delegate to them.

| Agent | Mention | Expertise |
|-------|---------|-----------|
| **Python Backend** | `@python-backend` | FastAPI, Pydantic, Async, SQLAlchemy |
| **LangChain Engineer** | `@langchain-engineer` | LangChain, Agents, Tools, Memory |
| **RAG Specialist** | `@rag-specialist` | Qdrant, Embeddings, Chunking |
| **DevOps Engineer** | `@devops-engineer` | Docker, CI/CD, Deployment |
| **QA Engineer** | `@qa-engineer` | Pytest, Integration Tests |
| **Security Engineer** | `@security-engineer` | Auth, OWASP, Input Validation |

Example:
> `@python-backend` Refactor the auth middleware to use async/await.

---

## 🧠 Skills & SOPs
Reusable patterns and procedures are available via the `skill` tool.

**Usage:**
```javascript
skill({ name: "docker-deployment" })
skill({ name: "git-workflow-sop" })
```

**Available Skills:**
- `docker-deployment`: Containerization patterns
- `fastapi-websocket`: WebSocket implementation
- `pydantic-validation`: Data validation patterns
- `qdrant-rag`: RAG system implementation
- `langchain-tool-creation`: Creating custom tools

**Standard Operating Procedures (SOPs):**
- `git-workflow-sop`: Branching and committing
- `deployment-sop`: Deploying to production
- `incident-response-sop`: Handling emergencies
- `code-review-sop`: Review guidelines

---

## 🛠 ProjectPulse MCP Tools
Full access to the ProjectPulse ecosystem is available via MCP tools:

- **Knowledge Base**: `projectpulse_knowledge_search`
- **Wiki**: `projectpulse_wiki_search`
- **Roadmap**: `projectpulse_sprint_getCurrentPosition`
- **Kanban**: `projectpulse_kanban_getBoard`

---

## Token Efficiency
1. **Load Context First**: Use `projectpulse_context_load`.
2. **Use Specialized Agents**: They have focused system prompts.
3. **Load Skills On-Demand**: Don't ask for "all skills", ask for specific ones using `skill()`.
