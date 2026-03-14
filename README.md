# Jira Ticket Evaluator 🚀

An AI-powered agentic system that autonomously evaluates whether a GitHub Pull Request satisfies the requirements of a linked Jira ticket. Built for the Hackathon - AI Engineering Track.

## 🏗 Architecture Overview

The system uses a **multi-agent orchestration** pattern powered by **LangGraph** and **Gemini 2.0**. It integrates with **Jira** and **GitHub** via custom **MCP (Model Context Protocol) servers**.

### Agents
1.  **Retriever Agent**: Fetches context from Jira and GitHub via MCP server tool calls.
2.  **Requirements Agent**: Parses Jira tickets into discrete, testable acceptance criteria.
3.  **Evaluator Agent**: Analyzes code diffs against requirements with line-level traceability.
4.  **Verification Agent**: Generates and **executes** validation tests to provide empirical evidence.
5.  **Synthesis Agent**: Aggregates findings into a final structured verdict (Pass/Partial/Fail) with a data-driven confidence score.

### Core Technologies
- **LLM**: Google Gemini 2.0 Flash
- **Orchestration**: LangGraph (StateGraph)
- **MCP**: Custom Jira MCP Server + Custom GitHub MCP Server (stdio transport)
- **Backend**: Python (FastAPI + Pydantic)
- **Frontend**: React + TypeScript + Tailwind CSS

### MCP Servers

| Server | Tools | Data Source |
|:-------|:------|:------------|
| **Jira MCP** (`src/mcp_servers/jira_server.py`) | `get_jira_ticket`, `get_jira_ticket_comments`, `search_jira_tickets` | Jira Cloud REST API v3 |
| **GitHub MCP** (`src/mcp_servers/github_server.py`) | `get_pull_request`, `get_pull_request_diff`, `get_pull_request_files`, `get_pull_request_reviews`, `get_file_content` | GitHub REST API v3 |

## 📂 Repository Structure

```text
jira-ticket-evaluator/
├── README.md               # Setup, architecture, usage
├── .env.example            # Required environment variables
├── requirements.txt        # Python dependencies
├── src/                    # Agent, tools, MCP integrations
│   ├── agents/             # Agent definitions (LangGraph nodes)
│   │   ├── retriever.py    # Context fetching via MCP
│   │   ├── parser.py       # Requirement extraction
│   │   ├── evaluator.py    # Diff evaluation + traceability
│   │   ├── verification.py # Test generation + execution
│   │   └── synthesis.py    # Verdict + confidence scoring
│   ├── mcp_servers/        # Custom MCP server implementations
│   │   ├── jira_server.py  # Jira MCP server (3 tools)
│   │   └── github_server.py # GitHub MCP server (5 tools)
│   ├── mcp_client.py       # MCP client (stdio transport)
│   ├── state.py            # Shared agent state definition
│   ├── utils.py            # Gemini API utilities
│   └── main.py             # FastAPI server and entry-point
├── tests/                  # Test suite
│   ├── test_agents.py      # Agent unit + integration tests
│   └── test_mcp_servers.py # MCP server tool tests
├── examples/               # Sample Jira tickets + PRs for demo
│   └── sample_cases.md     # Feature, Bug, and Refactor examples
├── docs/                   # Architecture diagrams, evaluation reports
│   ├── architecture.md     # System architecture + MCP details
│   └── traceability_matrix.md
└── frontend/               # React dashboard
```

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+

### Environment Variables
Copy `.env.example` to `.env` in the root directory and fill in your keys:
```env
GEMINI_API_KEY=...
GITHUB_TOKEN=...
JIRA_URL=https://your-domain.atlassian.net
JIRA_USER_EMAIL=...
JIRA_API_TOKEN=...
```

### Installation
```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

## 🚀 Usage
1. Start the backend: `python src/main.py`
2. Start the frontend: `cd frontend && npm run dev`
3. Enter a Jira Ticket Key (e.g., `PROJ-123`) and a GitHub PR URL in the dashboard.
4. Click **Evaluate PR** and watch the agents work in real-time.

## 🧪 Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_agents.py -v
python -m pytest tests/test_mcp_servers.py -v
```

## 📊 How It Works

1. **Input** → User provides a Jira ticket key and GitHub PR URL
2. **Retriever Agent** → Connects to MCP servers to fetch ticket data and PR diff
3. **Parser Agent** → Uses Gemini to extract testable acceptance criteria
4. **Evaluator Agent** → Assesses each requirement against the code diff with evidence
5. **Verification Agent** → Generates and runs Python tests for failed/partial requirements
6. **Synthesis Agent** → Produces final Pass/Partial/Fail verdict with confidence score
7. **Dashboard** → Displays results with pipeline visualization and requirement traceability
