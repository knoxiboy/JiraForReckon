# Jira Ticket Evaluator 🚀

An AI-powered agentic system that autonomously evaluates whether a GitHub Pull Request satisfies the requirements of a linked Jira ticket. Built for the Hackathon - AI Engineering Track.

## 🏗 Architecture Overview

The system uses a **multi-agent orchestration** pattern powered by **LangGraph** and **Gemini 2.0**. It integrates with **Jira** and **GitHub** via the **Model Context Protocol (MCP)**.

### Agents
1.  **Retriever Agent**: Discovers and fetches context from Jira and GitHub.
2.  **Requirements Agent**: Parses Jira tickets into discrete, testable acceptance criteria.
3.  **Evaluator Agent**: Analyzes code diffs against requirements using multi-step reasoning.
4.  **Verification Agent**: Generates and executes validation tests to provide empirical evidence.
5.  **Synthesis Agent**: Aggregates findings into a final structured verdict (Pass/Partial/Fail).

### Core Technologies
- **LLM**: Google Gemini 2.0 Flash
- **Orchestration**: LangGraph (StateGraph)
- **MCP**: GitKraken MCP (GitHub & Jira connectivity)
- **Backend**: Python (FastAPI + Pydantic)
- **Frontend**: React + TypeScript + Tailwind CSS

## 📂 Repository Structure

```text
jira-ticket-evaluator/
├── README.md           # Setup, architecture, usage
├── src/                # Agent, tools, MCP integrations
│   ├── agents/         # Agent definitions (LangGraph nodes)
│   ├── tools/          # Custom tools and MCP wrappers
│   ├── state.py        # Shared agent state definition
│   └── main.py         # FastAPI server and entry-point
├── tests/              # Custom test generation scripts
├── examples/           # Sample Jira tickets + PRs used for demo
├── docs/               # Architecture diagrams, evaluation reports
└── frontend/           # React dashboard
```

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- [GitKraken MCP Server](https://github.com/GitKraken/mcp-server) configured

### Environment Variables
Copy `.env.example` to `.env` in the root directory and fill in your keys:
```env
GEMINI_API_KEY=...
GITHUB_TOKEN=...
JIRA_URL=...
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
