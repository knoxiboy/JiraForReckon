"""
MCP Client Utility

Provides a reusable MCP client that connects to the Jira and GitHub MCP servers
via stdio transport and calls their tools. Used by the Retriever Agent.
"""

import os
import sys
import json
import asyncio
import logging
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger("evaluator.mcp_client")


def _get_python_path():
    """Get the Python executable path for launching MCP servers."""
    return sys.executable


def _get_server_path(server_name: str) -> str:
    """Get the absolute path to an MCP server module."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "src", "mcp_servers", f"{server_name}.py")


@asynccontextmanager
async def connect_mcp_server(server_name: str):
    """
    Context manager that spawns an MCP server subprocess via stdio
    and yields an active ClientSession.
    
    Usage:
        async with connect_mcp_server("jira_server") as session:
            result = await session.call_tool("get_jira_ticket", {"issue_key": "PROJ-123"})
    """
    server_path = _get_server_path(server_name)
    
    server_params = StdioServerParameters(
        command=_get_python_path(),
        args=[server_path],
        env={
            **os.environ,
            "PYTHONPATH": os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        }
    )
    
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            logger.info(f"MCP session initialized for: {server_name}")
            yield session


async def call_mcp_tool(server_name: str, tool_name: str, arguments: dict) -> dict:
    """
    Convenience function to connect to an MCP server, call a single tool,
    and return the parsed JSON result.
    """
    try:
        async with connect_mcp_server(server_name) as session:
            result = await session.call_tool(tool_name, arguments)
            
            # Extract text content from MCP result
            if hasattr(result, 'content') and result.content:
                text_parts = []
                for block in result.content:
                    if hasattr(block, 'text'):
                        text_parts.append(block.text)
                raw_text = "\n".join(text_parts)
            else:
                raw_text = str(result)
            
            try:
                return json.loads(raw_text)
            except json.JSONDecodeError:
                return {"raw": raw_text}
                
    except Exception as e:
        logger.error(f"MCP tool call failed [{server_name}/{tool_name}]: {e}")
        return {"error": str(e)}


async def fetch_jira_ticket(issue_key: str) -> dict:
    """Fetch a Jira ticket via the Jira MCP server."""
    return await call_mcp_tool("jira_server", "get_jira_ticket", {"issue_key": issue_key})


async def fetch_jira_comments(issue_key: str) -> list:
    """Fetch Jira ticket comments via the Jira MCP server."""
    result = await call_mcp_tool("jira_server", "get_jira_ticket_comments", {"issue_key": issue_key})
    return result if isinstance(result, list) else []


async def fetch_pr_metadata(owner: str, repo: str, pr_number: int) -> dict:
    """Fetch PR metadata via the GitHub MCP server."""
    return await call_mcp_tool(
        "github_server", "get_pull_request",
        {"owner": owner, "repo": repo, "pr_number": pr_number}
    )


async def fetch_pr_diff(owner: str, repo: str, pr_number: int) -> str:
    """Fetch PR diff via the GitHub MCP server."""
    result = await call_mcp_tool(
        "github_server", "get_pull_request_diff",
        {"owner": owner, "repo": repo, "pr_number": pr_number}
    )
    return result.get("diff", "") if isinstance(result, dict) else ""


async def fetch_pr_files(owner: str, repo: str, pr_number: int) -> list:
    """Fetch PR changed files via the GitHub MCP server."""
    result = await call_mcp_tool(
        "github_server", "get_pull_request_files",
        {"owner": owner, "repo": repo, "pr_number": pr_number}
    )
    return result if isinstance(result, list) else []
