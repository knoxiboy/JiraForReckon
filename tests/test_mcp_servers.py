"""
Tests for MCP Server Tool Functions

Unit tests for the Jira and GitHub MCP server tool implementations.
Tests the tool functions directly (without MCP transport).
"""

import os
import sys
import json
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestJiraMCPServer(unittest.TestCase):
    """Tests for the Jira MCP server tools."""
    
    @patch("src.mcp_servers.jira_server.requests.get")
    def test_get_jira_ticket_success(self, mock_get):
        """Should fetch and format Jira ticket data correctly."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "key": "PROJ-123",
            "fields": {
                "summary": "Implement Login",
                "description": {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Create login API"}]}]},
                "status": {"name": "In Progress"},
                "priority": {"name": "High"},
                "issuetype": {"name": "Story"},
                "labels": ["backend"],
                "customfield_10016": ""
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        with patch.dict(os.environ, {
            "JIRA_URL": "https://test.atlassian.net",
            "JIRA_USER_EMAIL": "test@test.com",
            "JIRA_API_TOKEN": "fake-token"
        }):
            from src.mcp_servers.jira_server import get_jira_ticket
            result = json.loads(get_jira_ticket("PROJ-123"))
        
        self.assertEqual(result["key"], "PROJ-123")
        self.assertEqual(result["fields"]["summary"], "Implement Login")
        self.assertIn("Create login API", result["fields"]["description"])
    
    def test_get_jira_ticket_no_credentials(self):
        """Should raise ValueError when credentials are missing."""
        with patch.dict(os.environ, {}, clear=True):
            from src.mcp_servers.jira_server import get_jira_ticket
            with self.assertRaises(ValueError):
                get_jira_ticket("PROJ-123")


class TestGitHubMCPServer(unittest.TestCase):
    """Tests for the GitHub MCP server tools."""
    
    @patch("src.mcp_servers.github_server.requests.get")
    def test_get_pull_request_success(self, mock_get):
        """Should fetch and format PR metadata correctly."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "number": 42,
            "title": "feat: add login",
            "body": "Implements login endpoint",
            "state": "open",
            "user": {"login": "dev"},
            "base": {"ref": "main"},
            "head": {"ref": "feature/login"},
            "mergeable": True,
            "additions": 50,
            "deletions": 5,
            "changed_files": 3,
            "created_at": "2024-01-01",
            "updated_at": "2024-01-02",
            "labels": [{"name": "feature"}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        with patch.dict(os.environ, {"GITHUB_TOKEN": "fake-token"}):
            from src.mcp_servers.github_server import get_pull_request
            result = json.loads(get_pull_request("owner", "repo", 42))
        
        self.assertEqual(result["number"], 42)
        self.assertEqual(result["title"], "feat: add login")
        self.assertEqual(result["changed_files"], 3)
    
    @patch("src.mcp_servers.github_server.requests.get")
    def test_get_pull_request_diff(self, mock_get):
        """Should fetch and return diff text."""
        mock_response = MagicMock()
        mock_response.text = "+ new line added\n- old line removed"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        with patch.dict(os.environ, {"GITHUB_TOKEN": "fake-token"}):
            from src.mcp_servers.github_server import get_pull_request_diff
            result = json.loads(get_pull_request_diff("owner", "repo", 42))
        
        self.assertIn("diff", result)
        self.assertIn("new line added", result["diff"])


class TestADFParser(unittest.TestCase):
    """Tests for the Atlassian Document Format parser."""
    
    def test_simple_text_extraction(self):
        """Should extract text from simple ADF structure."""
        from src.mcp_servers.jira_server import _extract_adf_text
        
        adf = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Hello World"}]
                }
            ]
        }
        
        result = _extract_adf_text(adf)
        self.assertIn("Hello World", result)
    
    def test_nested_content(self):
        """Should handle nested ADF content."""
        from src.mcp_servers.jira_server import _extract_adf_text
        
        adf = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Line 1"},
                    ]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Line 2"},
                    ]
                }
            ]
        }
        
        result = _extract_adf_text(adf)
        self.assertIn("Line 1", result)
        self.assertIn("Line 2", result)
    
    def test_non_dict_input(self):
        """Should handle non-dict input gracefully."""
        from src.mcp_servers.jira_server import _extract_adf_text
        
        self.assertEqual(_extract_adf_text("plain text"), "plain text")
        self.assertEqual(_extract_adf_text(None), "")


if __name__ == "__main__":
    unittest.main()
