"""
GitHub MCP Server

A Model Context Protocol server that exposes GitHub REST API operations as tools.
Provides PR retrieval, diff analysis, and file listing for the Jira Ticket Evaluator.
"""

import os
import json
import logging
import requests
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp.github")

# Initialize MCP Server
mcp = FastMCP(
    "github-server",
    instructions="MCP server for GitHub PR retrieval and code analysis"
)

def _get_github_headers():
    """Returns GitHub API headers with authentication."""
    token = os.getenv("GITHUB_TOKEN", "")
    if not token:
        raise ValueError("GITHUB_TOKEN must be set. See .env.example for details.")
    
    return {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }


@mcp.tool()
def get_pull_request(owner: str, repo: str, pr_number: int) -> str:
    """
    Fetch Pull Request metadata including title, body, state, author,
    base/head branches, and merge status.
    """
    headers = _get_github_headers()
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        result = {
            "number": data.get("number"),
            "title": data.get("title", ""),
            "body": data.get("body", ""),
            "state": data.get("state", ""),
            "author": data.get("user", {}).get("login", ""),
            "base_branch": data.get("base", {}).get("ref", ""),
            "head_branch": data.get("head", {}).get("ref", ""),
            "mergeable": data.get("mergeable"),
            "additions": data.get("additions", 0),
            "deletions": data.get("deletions", 0),
            "changed_files": data.get("changed_files", 0),
            "created_at": data.get("created_at", ""),
            "updated_at": data.get("updated_at", ""),
            "labels": [l.get("name", "") for l in data.get("labels", [])],
        }
        
        logger.info(f"Fetched PR #{pr_number} from {owner}/{repo}")
        return json.dumps(result, indent=2)
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"GitHub API error for PR #{pr_number}: {e.response.status_code} - {e.response.text}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})
    except Exception as e:
        error_msg = f"Failed to fetch PR #{pr_number}: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})


@mcp.tool()
def get_pull_request_diff(owner: str, repo: str, pr_number: int) -> str:
    """
    Fetch the full unified diff of a Pull Request.
    Returns the raw diff text showing all code additions and deletions.
    """
    token = os.getenv("GITHUB_TOKEN", "")
    if not token:
        return json.dumps({"error": "GITHUB_TOKEN not set"})
    
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {
        "Accept": "application/vnd.github.v3.diff",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        diff_text = response.text
        
        # Truncate very large diffs to avoid LLM token limits
        max_chars = 50000
        if len(diff_text) > max_chars:
            diff_text = diff_text[:max_chars] + f"\n\n... [TRUNCATED: diff was {len(response.text)} chars, showing first {max_chars}]"
            logger.warning(f"PR #{pr_number} diff truncated from {len(response.text)} to {max_chars} chars")
        
        logger.info(f"Fetched diff for PR #{pr_number} ({len(diff_text)} chars)")
        return json.dumps({"diff": diff_text})
        
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch diff: {str(e)}"})


@mcp.tool()
def get_pull_request_files(owner: str, repo: str, pr_number: int) -> str:
    """
    List all files changed in a Pull Request with their status
    (added, modified, removed, renamed) and change statistics.
    """
    headers = _get_github_headers()
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    
    try:
        # Handle pagination — fetch up to 300 files
        all_files = []
        page = 1
        while True:
            params = {"per_page": 100, "page": page}
            response = requests.get(url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            files = response.json()
            
            if not files:
                break
            
            for f in files:
                all_files.append({
                    "filename": f.get("filename", ""),
                    "status": f.get("status", ""),
                    "additions": f.get("additions", 0),
                    "deletions": f.get("deletions", 0),
                    "changes": f.get("changes", 0),
                    "patch": f.get("patch", "")[:3000],  # Limit patch size per file
                })
            
            if len(files) < 100:
                break
            page += 1
        
        logger.info(f"Fetched {len(all_files)} changed files for PR #{pr_number}")
        return json.dumps(all_files, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch PR files: {str(e)}"})


@mcp.tool()
def get_pull_request_reviews(owner: str, repo: str, pr_number: int) -> str:
    """
    Fetch code reviews and review comments on a Pull Request.
    Useful for understanding reviewer feedback and requested changes.
    """
    headers = _get_github_headers()
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        reviews = []
        for review in response.json():
            reviews.append({
                "user": review.get("user", {}).get("login", ""),
                "state": review.get("state", ""),
                "body": review.get("body", ""),
                "submitted_at": review.get("submitted_at", "")
            })
        
        logger.info(f"Fetched {len(reviews)} reviews for PR #{pr_number}")
        return json.dumps(reviews, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch reviews: {str(e)}"})


@mcp.tool()
def get_file_content(owner: str, repo: str, path: str, ref: str = "main") -> str:
    """
    Fetch the content of a specific file from the repository at a given branch or commit ref.
    Useful for retrieving full file context beyond what the diff shows.
    """
    headers = _get_github_headers()
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    params = {"ref": ref}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        import base64
        content = ""
        if data.get("encoding") == "base64" and data.get("content"):
            content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        
        # Truncate very large files
        if len(content) > 20000:
            content = content[:20000] + "\n... [TRUNCATED]"
        
        return json.dumps({
            "path": data.get("path", path),
            "size": data.get("size", 0),
            "content": content
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch file {path}: {str(e)}"})


if __name__ == "__main__":
    mcp.run(transport="stdio")
