"""
Retriever Agent

LangGraph node that fetches context from Jira and GitHub via MCP servers.
Falls back to direct API calls if MCP connection fails, and to mock data
if no API credentials are configured.
"""

import os
import re
import json
import asyncio
import logging
import requests
from requests.auth import HTTPBasicAuth
from src.state import AgentState

logger = logging.getLogger("evaluator.retriever")


def retriever_agent(state: AgentState) -> AgentState:
    """
    Node 1: Fetches context from Jira and GitHub.
    
    Priority chain:
        1. MCP servers (preferred — satisfies hackathon requirement)
        2. Direct REST API calls (fallback)
        3. Mock data (development/demo only)
    """
    jira_key = state.get("jira_key")
    pr_url = state.get("pr_url")
    logs = list(state.get("logs", []))
    
    logs.append(f"Retriever Agent: Starting context retrieval for Jira={jira_key}, PR={pr_url}")
    
    # ── 1. Fetch Jira Data ──
    jira_data = _fetch_jira_data(jira_key, logs)
    
    # ── 2. Parse PR URL and Fetch GitHub Data ──
    pr_metadata, pr_diff, pr_files = _fetch_github_data(pr_url, logs)
    
    logs.append(f"Retriever Agent: Context retrieval complete. "
                f"Jira='{jira_data.get('fields', {}).get('summary', 'N/A')}', "
                f"PR files={len(pr_files)}")
    
    return {
        **state,
        "jira_data": jira_data,
        "pr_metadata": pr_metadata,
        "pr_diff": pr_diff,
        "pr_files": pr_files,
        "current_agent": "Retriever",
        "logs": logs
    }


def _fetch_jira_data(jira_key: str, logs: list) -> dict:
    """Fetch Jira ticket data via MCP, then API, then mock."""
    
    # ── Attempt 1: MCP Server ──
    if _has_jira_credentials():
        try:
            logs.append("Retriever Agent: Connecting to Jira MCP server...")
            result = asyncio.run(_mcp_fetch_jira(jira_key))
            if "error" not in result:
                logs.append(f"Retriever Agent: ✓ Fetched Jira via MCP: {result.get('fields', {}).get('summary', '')}")
                return result
            else:
                logs.append(f"Retriever Agent: MCP returned error, falling back to direct API: {result['error']}")
        except Exception as e:
            logs.append(f"Retriever Agent: MCP connection failed, trying direct API: {e}")
    
    # ── Attempt 2: Direct Jira REST API ──
    if _has_jira_credentials():
        try:
            logs.append("Retriever Agent: Fetching Jira ticket via REST API...")
            result = _direct_jira_fetch(jira_key)
            if result:
                logs.append(f"Retriever Agent: ✓ Fetched Jira via REST API: {result.get('fields', {}).get('summary', '')}")
                return result
        except Exception as e:
            logs.append(f"Retriever Agent: Direct API call failed: {e}")
    
    # ── Attempt 3: Mock Data ──
    logs.append("Retriever Agent: No Jira credentials configured. Using mock data for demo.")
    return _mock_jira_data(jira_key)


def _fetch_github_data(pr_url: str, logs: list) -> tuple:
    """Parse PR URL and fetch GitHub PR data via MCP, then API, then mock."""
    
    pr_match = re.match(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
    if not pr_match:
        logs.append("Retriever Agent: ⚠ Could not parse GitHub PR URL. Using defaults.")
        return {}, "", []
    
    owner, repo, pr_number = pr_match.groups()
    pr_number = int(pr_number)
    logs.append(f"Retriever Agent: Identified repo={owner}/{repo}, PR=#{pr_number}")
    
    github_token = os.getenv("GITHUB_TOKEN", "")
    
    # ── Attempt 1: MCP Server ──
    if github_token:
        try:
            logs.append("Retriever Agent: Connecting to GitHub MCP server...")
            pr_meta, pr_diff, pr_files = asyncio.run(
                _mcp_fetch_github(owner, repo, pr_number)
            )
            if "error" not in pr_meta:
                logs.append(f"Retriever Agent: ✓ Fetched PR via MCP — {pr_meta.get('changed_files', 0)} files changed")
                file_names = [f.get("filename", "") for f in pr_files] if isinstance(pr_files, list) else []
                return pr_meta, pr_diff, file_names
            else:
                logs.append(f"Retriever Agent: MCP returned error, falling back to direct API: {pr_meta.get('error')}")
        except Exception as e:
            logs.append(f"Retriever Agent: MCP connection failed, trying direct API: {e}")
    
    # ── Attempt 2: Direct GitHub REST API ──
    if github_token:
        try:
            logs.append("Retriever Agent: Fetching PR via GitHub REST API...")
            pr_meta, pr_diff, pr_files = _direct_github_fetch(owner, repo, pr_number, github_token)
            logs.append(f"Retriever Agent: ✓ Fetched PR via REST API — {len(pr_files)} files changed")
            return pr_meta, pr_diff, pr_files
        except Exception as e:
            logs.append(f"Retriever Agent: Direct API call failed: {e}")
    
    # ── Attempt 3: Mock Data ──
    logs.append("Retriever Agent: No GITHUB_TOKEN configured. Using mock data for demo.")
    return _mock_github_data()


# ════════════════════════════════════════════
# MCP-powered fetchers
# ════════════════════════════════════════════

async def _mcp_fetch_jira(issue_key: str) -> dict:
    """Fetch Jira ticket via the Jira MCP server."""
    from src.mcp_client import fetch_jira_ticket
    return await fetch_jira_ticket(issue_key)


async def _mcp_fetch_github(owner: str, repo: str, pr_number: int) -> tuple:
    """Fetch PR data via the GitHub MCP server."""
    from src.mcp_client import fetch_pr_metadata, fetch_pr_diff, fetch_pr_files
    
    # Fetch all three in parallel via MCP
    pr_meta = await fetch_pr_metadata(owner, repo, pr_number)
    pr_diff = await fetch_pr_diff(owner, repo, pr_number)
    pr_files = await fetch_pr_files(owner, repo, pr_number)
    
    return pr_meta, pr_diff, pr_files


# ════════════════════════════════════════════
# Direct API fetchers (fallback)
# ════════════════════════════════════════════

def _has_jira_credentials() -> bool:
    return all([
        os.getenv("JIRA_URL"),
        os.getenv("JIRA_USER_EMAIL"),
        os.getenv("JIRA_API_TOKEN")
    ])


def _direct_jira_fetch(issue_key: str) -> dict:
    """Direct Jira REST API v3 call without MCP."""
    base_url = os.getenv("JIRA_URL", "").rstrip("/")
    auth = HTTPBasicAuth(os.getenv("JIRA_USER_EMAIL", ""), os.getenv("JIRA_API_TOKEN", ""))
    
    url = f"{base_url}/rest/api/3/issue/{issue_key}"
    resp = requests.get(url, auth=auth, headers={"Accept": "application/json"}, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    
    fields = data.get("fields", {})
    description = fields.get("description", "")
    if isinstance(description, dict):
        description = _extract_adf_text(description)
    
    return {
        "key": data.get("key", issue_key),
        "fields": {
            "summary": fields.get("summary", ""),
            "description": str(description or ""),
            "status": fields.get("status", {}).get("name", ""),
            "priority": fields.get("priority", {}).get("name", ""),
            "issuetype": fields.get("issuetype", {}).get("name", ""),
            "labels": fields.get("labels", []),
        }
    }


def _direct_github_fetch(owner: str, repo: str, pr_number: int, token: str) -> tuple:
    """Direct GitHub REST API calls without MCP."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {token}"
    }
    
    # PR metadata
    resp = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}",
        headers=headers, timeout=15
    )
    resp.raise_for_status()
    pr_data = resp.json()
    pr_meta = {
        "title": pr_data.get("title", ""),
        "body": pr_data.get("body", ""),
        "state": pr_data.get("state", ""),
        "additions": pr_data.get("additions", 0),
        "deletions": pr_data.get("deletions", 0),
        "changed_files": pr_data.get("changed_files", 0),
    }
    
    # PR diff
    diff_headers = {**headers, "Accept": "application/vnd.github.v3.diff"}
    resp = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}",
        headers=diff_headers, timeout=30
    )
    resp.raise_for_status()
    pr_diff = resp.text[:50000]  # Limit for LLM context
    
    # PR files
    resp = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files",
        headers=headers, timeout=15
    )
    resp.raise_for_status()
    pr_files = [f.get("filename", "") for f in resp.json()]
    
    return pr_meta, pr_diff, pr_files


# ════════════════════════════════════════════
# Mock data (demo/development fallback)
# ════════════════════════════════════════════

def _mock_jira_data(jira_key: str) -> dict:
    return {
        "key": jira_key,
        "fields": {
            "summary": "Implement User Login API",
            "description": (
                "Create a new POST endpoint for user login.\n"
                "Acceptance Criteria:\n"
                "- Endpoint: /api/login\n"
                "- Payload: {email, password}\n"
                "- Return 200 on success, 401 on failure."
            ),
            "status": "In Progress",
            "priority": "High",
            "issuetype": "Story",
            "labels": ["backend", "auth"],
        }
    }


def _mock_github_data() -> tuple:
    pr_metadata = {
        "title": "feat: login api",
        "body": "Implementing login endpoint as per PROJ-123.",
        "state": "open",
        "additions": 25,
        "deletions": 0,
        "changed_files": 1,
    }
    pr_diff = """
+ @app.post('/api/login')
+ def login(data: LoginRequest):
+     if auth.verify(data.email, data.password):
+         return {"status": "ok"}
+     return {"status": "error"}, 401
    """
    pr_files = ["src/main.py"]
    return pr_metadata, pr_diff, pr_files


def _extract_adf_text(adf_node) -> str:
    """Recursively extract plain text from Atlassian Document Format."""
    if not isinstance(adf_node, dict):
        return str(adf_node) if adf_node else ""
    texts = []
    if adf_node.get("type") == "text":
        texts.append(adf_node.get("text", ""))
    for child in adf_node.get("content", []):
        texts.append(_extract_adf_text(child))
        if child.get("type") in ("paragraph", "heading", "listItem"):
            texts.append("\n")
    return "".join(texts).strip()
