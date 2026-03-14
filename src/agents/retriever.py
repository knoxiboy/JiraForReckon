import logging
import re
from src.state import AgentState

logger = logging.getLogger("evaluator.retriever")

def retriever_agent(state: AgentState) -> AgentState:
    """
    Node 1: Fetches context from Jira and GitHub using GitKraken MCP.
    """
    jira_key = state.get("jira_key")
    pr_url = state.get("pr_url")
    logs = state.get("logs", [])
    
    logs.append(f"Retriever Agent: Fetching Jira ticket {jira_key}...")
    
    # In a real tool-use environment, the agent would call:
    # mcp_GitKraken_issues_get_detail(issue_id=jira_key, provider="jira")
    # mcp_GitKraken_pull_request_get_detail(...)
    
    # We will assume these are populated by the tool-use layer
    # or provided in the initial state for the demo.
    
    # Parse PR URL to get repo and PR ID
    # https://github.com/owner/repo/pull/45
    pr_match = re.match(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
    if pr_match:
        org, repo, pr_id = pr_match.groups()
        logs.append(f"Retriever Agent: Identified Repo: {org}/{repo}, PR: {pr_id}")
    else:
        logs.append("Retriever Agent Warning: Could not parse GitHub PR URL format.")

    return {
        **state,
        "current_agent": "Retriever",
        "logs": logs
    }
