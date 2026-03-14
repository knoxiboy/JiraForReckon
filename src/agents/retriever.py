import logging
import re
from src.state import AgentState

logger = logging.getLogger("evaluator.retriever")

def retriever_agent(state: AgentState) -> AgentState:
    """
    Node 1: Fetches context from Jira and GitHub.
    In a real implementation, this would call MCP tools or APIs.
    """
    jira_key = state.get("jira_key")
    pr_url = state.get("pr_url")
    logs = state.get("logs", [])
    
    logs.append(f"Retriever Agent: Starting context retrieval for {jira_key}...")
    
    # 1. Fetch Jira Data (Mock/Placeholder)
    # In a real tool-use environment, the agent would call:
    # mcp_GitKraken_issues_get_detail(issue_id=jira_key, provider="jira")
    jira_data = {
        "key": jira_key,
        "fields": {
            "summary": "Implement User Login API",
            "description": "Create a new POST endpoint for user login.\nAcceptance Criteria:\n- Endpoint: /api/login\n- Payload: {email, password}\n- Return 200 on success, 401 on failure."
        }
    }
    logs.append(f"Retriever Agent: Fetched Jira ticket: {jira_data['fields']['summary']}")
    
    # 2. Parse PR URL and Fetch PR Data (Mock/Placeholder)
    pr_match = re.match(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
    if pr_match:
        org, repo, pr_id = pr_match.groups()
        logs.append(f"Retriever Agent: Identified Repo: {org}/{repo}, PR: {pr_id}")
        
        # In real scenario, use mcp_GitKraken_pull_request_get_detail
        pr_metadata = {"title": "feat: login api", "body": "Implementing login endpoint."}
        pr_diff = """
+ @app.post('/api/login')
+ def login(data: LoginRequest):
+     if auth.verify(data.email, data.password):
+         return {"status": "ok"}
+     return {"status": "error"}, 401
        """
        pr_files = ["src/main.py"]
    else:
        logs.append("Retriever Agent Warning: Could not parse GitHub PR URL format. Using defaults.")
        pr_metadata = {}
        pr_diff = ""
        pr_files = []

    return {
        **state,
        "jira_data": jira_data,
        "pr_metadata": pr_metadata,
        "pr_diff": pr_diff,
        "pr_files": pr_files,
        "current_agent": "Retriever",
        "logs": logs
    }
