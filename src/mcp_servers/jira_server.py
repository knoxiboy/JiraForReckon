"""
Jira MCP Server

A Model Context Protocol server that exposes Jira REST API operations as tools.
Provides ticket retrieval, search, and comment access for the Jira Ticket Evaluator.
"""

import os
import json
import logging
import requests
from requests.auth import HTTPBasicAuth
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp.jira")

# Initialize MCP Server
mcp = FastMCP(
    "jira-server",
    instructions="MCP server for Jira ticket retrieval and analysis"
)

def _get_jira_auth():
    """Returns Jira base URL and auth object from environment variables."""
    base_url = os.getenv("JIRA_URL", "").rstrip("/")
    email = os.getenv("JIRA_USER_EMAIL", "")
    token = os.getenv("JIRA_API_TOKEN", "")
    
    if not all([base_url, email, token]):
        raise ValueError(
            "JIRA_URL, JIRA_USER_EMAIL, and JIRA_API_TOKEN must be set. "
            "See .env.example for details."
        )
    
    return base_url, HTTPBasicAuth(email, token)


@mcp.tool()
def get_jira_ticket(issue_key: str) -> str:
    """
    Fetch a Jira ticket by its key (e.g., PROJ-123).
    Returns the ticket summary, description, status, priority,
    issue type, acceptance criteria, and labels.
    """
    base_url, auth = _get_jira_auth()
    
    url = f"{base_url}/rest/api/3/issue/{issue_key}"
    headers = {"Accept": "application/json"}
    
    try:
        response = requests.get(url, headers=headers, auth=auth, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        fields = data.get("fields", {})
        
        # Extract description - handle Atlassian Document Format (ADF)
        description_raw = fields.get("description", {})
        description_text = _extract_adf_text(description_raw) if isinstance(description_raw, dict) else str(description_raw or "")
        
        result = {
            "key": data.get("key"),
            "fields": {
                "summary": fields.get("summary", ""),
                "description": description_text,
                "status": fields.get("status", {}).get("name", "Unknown"),
                "priority": fields.get("priority", {}).get("name", "Unknown"),
                "issuetype": fields.get("issuetype", {}).get("name", "Unknown"),
                "labels": fields.get("labels", []),
                "acceptance_criteria": fields.get("customfield_10016", ""),  # Common AC field
            }
        }
        
        logger.info(f"Successfully fetched Jira ticket: {issue_key}")
        return json.dumps(result, indent=2)
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"Jira API error for {issue_key}: {e.response.status_code} - {e.response.text}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})
    except Exception as e:
        error_msg = f"Failed to fetch Jira ticket {issue_key}: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})


@mcp.tool()
def get_jira_ticket_comments(issue_key: str) -> str:
    """
    Fetch all comments on a Jira ticket.
    Comments often contain additional context, clarifications,
    or updated acceptance criteria.
    """
    base_url, auth = _get_jira_auth()
    
    url = f"{base_url}/rest/api/3/issue/{issue_key}/comment"
    headers = {"Accept": "application/json"}
    
    try:
        response = requests.get(url, headers=headers, auth=auth, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        comments = []
        for comment in data.get("comments", []):
            body = comment.get("body", {})
            text = _extract_adf_text(body) if isinstance(body, dict) else str(body or "")
            comments.append({
                "author": comment.get("author", {}).get("displayName", "Unknown"),
                "created": comment.get("created", ""),
                "body": text
            })
        
        logger.info(f"Fetched {len(comments)} comments for {issue_key}")
        return json.dumps(comments, indent=2)
        
    except Exception as e:
        error_msg = f"Failed to fetch comments for {issue_key}: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})


@mcp.tool()
def search_jira_tickets(jql_query: str, max_results: int = 5) -> str:
    """
    Search Jira tickets using JQL (Jira Query Language).
    Useful for finding related tickets or verifying ticket context.
    Example JQL: 'project = PROJ AND type = Bug AND status = "In Progress"'
    """
    base_url, auth = _get_jira_auth()
    
    url = f"{base_url}/rest/api/3/search"
    headers = {"Accept": "application/json"}
    params = {
        "jql": jql_query,
        "maxResults": max_results,
        "fields": "summary,status,issuetype,priority"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, auth=auth, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for issue in data.get("issues", []):
            fields = issue.get("fields", {})
            results.append({
                "key": issue.get("key"),
                "summary": fields.get("summary", ""),
                "status": fields.get("status", {}).get("name", ""),
                "type": fields.get("issuetype", {}).get("name", ""),
                "priority": fields.get("priority", {}).get("name", "")
            })
        
        return json.dumps(results, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"JQL search failed: {str(e)}"})


def _extract_adf_text(adf_node: dict) -> str:
    """
    Recursively extract plain text from Atlassian Document Format (ADF).
    Jira Cloud v3 API returns descriptions in ADF JSON format.
    """
    if not isinstance(adf_node, dict):
        return str(adf_node) if adf_node else ""
    
    texts = []
    
    if adf_node.get("type") == "text":
        texts.append(adf_node.get("text", ""))
    
    if adf_node.get("type") == "hardBreak":
        texts.append("\n")
    
    for child in adf_node.get("content", []):
        child_text = _extract_adf_text(child)
        if child_text:
            texts.append(child_text)
        # Add newline after block-level elements
        if child.get("type") in ("paragraph", "heading", "listItem", "blockquote"):
            texts.append("\n")
    
    return "".join(texts).strip()


if __name__ == "__main__":
    mcp.run(transport="stdio")
