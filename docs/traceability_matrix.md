# Requirement Traceability Matrix (RTM)

This matrix maps each hackathon requirement to the specific component in the Jira Ticket Evaluator that satisfies it.

| ID | Requirement | Implementation Component | Evidence / Artifact |
|:---|:---|:---|:---|
| **M1** | GitHub Integration | `RetrieverAgent` + GitHub MCP Server | `src/mcp_servers/github_server.py`, `src/agents/retriever.py` |
| **M2** | MCP Integration (≥1 server) | Jira MCP Server + GitHub MCP Server | `src/mcp_servers/jira_server.py`, `src/mcp_servers/github_server.py`, `src/mcp_client.py` |
| **M3** | AI Agents (Multi-step) | LangGraph `StateGraph` (5 nodes) | `src/orchestrator.py` |
| **M4** | AI APIs (Gemini) | `call_gemini` utility | `src/utils.py` |
| **F1** | Requirement Parsing | `RequirementsAgent` | `src/agents/parser.py` |
| **F2** | Structured Verdict (Pass/Partial/Fail) | `SynthesisAgent` | `src/agents/synthesis.py` |
| **F3** | Evidence Mapping (file, line, snippet) | `EvaluatorAgent` + traceability map | `src/agents/evaluator.py` |
| **O1** | Custom Test Generation + Execution | `VerificationAgent` (subprocess) | `src/agents/verification.py` |
| **O2** | Dashboard UI | React Dashboard | `frontend/src/App.tsx` |
| **O3** | Confidence Score (data-driven) | `SynthesisAgent` (3-dimension scoring) | `src/agents/synthesis.py` |

## Ticket Type Support

| Type | Handled By | Demo Example |
|:-----|:-----------|:-------------|
| Feature Request | Parser → Evaluator (AC matching) | `examples/sample_cases.md` → PROJ-101 |
| Bug Report | Evaluator (regression focus) + Verification (fix validation) | `examples/sample_cases.md` → PROJ-202 |
| Refactor/Cleanup | Evaluator (side-effect analysis) | `examples/sample_cases.md` → PROJ-303 |

## MCP Tool Inventory

### Jira MCP Server (3 tools)
| Tool | Purpose |
|:-----|:--------|
| `get_jira_ticket` | Fetch ticket with ADF → plaintext description parsing |
| `get_jira_ticket_comments` | Fetch comments for additional context |
| `search_jira_tickets` | JQL search for related tickets |

### GitHub MCP Server (5 tools)
| Tool | Purpose |
|:-----|:--------|
| `get_pull_request` | PR metadata (title, body, branches, stats) |
| `get_pull_request_diff` | Full unified diff (50K char limit) |
| `get_pull_request_files` | Changed files with per-file patches |
| `get_pull_request_reviews` | Code reviews and approval status |
| `get_file_content` | File content at any ref/branch |
