"""
Tests for the Jira Ticket Evaluator

Unit tests covering agent logic, state management, and orchestration pipeline.
"""

import json
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.state import AgentState


def _create_initial_state(**overrides) -> AgentState:
    """Helper to create a valid initial AgentState for testing."""
    defaults = {
        "jira_key": "TEST-100",
        "pr_url": "https://github.com/owner/repo/pull/1",
        "jira_data": {},
        "pr_metadata": {},
        "pr_diff": "",
        "pr_files": [],
        "requirements": [],
        "overall_verdict": "Unknown",
        "confidence_score": 0.0,
        "traceability_map": {},
        "test_outputs": [],
        "current_agent": "Start",
        "logs": [],
        "error": None
    }
    defaults.update(overrides)
    return AgentState(**defaults)


class TestRetrieverAgent(unittest.TestCase):
    """Tests for the Retriever Agent."""
    
    def test_mock_fallback_when_no_credentials(self):
        """Without API keys, retriever should fall back to mock data."""
        from src.agents.retriever import retriever_agent
        
        state = _create_initial_state()
        
        with patch.dict(os.environ, {}, clear=True):
            result = retriever_agent(state)
        
        # Should still return valid data (mock)
        self.assertIn("jira_data", result)
        self.assertIn("key", result["jira_data"])
        self.assertIn("pr_diff", result)
        self.assertEqual(result["current_agent"], "Retriever")
    
    def test_pr_url_parsing(self):
        """Should correctly parse GitHub PR URLs."""
        from src.agents.retriever import retriever_agent
        
        state = _create_initial_state(
            pr_url="https://github.com/myorg/myrepo/pull/42"
        )
        
        with patch.dict(os.environ, {}, clear=True):
            result = retriever_agent(state)
        
        # Logs should show parsed URL
        logs_text = " ".join(result.get("logs", []))
        self.assertIn("myorg/myrepo", logs_text)
    
    def test_invalid_pr_url(self):
        """Should handle invalid PR URLs gracefully."""
        from src.agents.retriever import retriever_agent
        
        state = _create_initial_state(pr_url="not-a-valid-url")
        
        with patch.dict(os.environ, {}, clear=True):
            result = retriever_agent(state)
        
        self.assertEqual(result["pr_diff"], "")
        self.assertEqual(result["pr_files"], [])


class TestParserAgent(unittest.TestCase):
    """Tests for the Requirements Parser Agent."""
    
    @patch("src.agents.parser.call_gemini")
    def test_requirement_extraction(self, mock_gemini):
        """Should parse Gemini response into structured requirements."""
        mock_gemini.return_value = '[{"id": "REQ-1", "description": "Login endpoint"}]'
        
        from src.agents.parser import requirements_agent
        
        state = _create_initial_state(
            jira_data={
                "key": "TEST-1",
                "fields": {
                    "summary": "Login API",
                    "description": "Create login endpoint."
                }
            }
        )
        
        result = requirements_agent(state)
        
        self.assertEqual(len(result["requirements"]), 1)
        self.assertEqual(result["requirements"][0]["id"], "REQ-1")
        self.assertEqual(result["requirements"][0]["verdict"], "Unknown")
    
    @patch("src.agents.parser.call_gemini")
    def test_handles_json_in_markdown(self, mock_gemini):
        """Should handle Gemini responses wrapped in markdown code fences."""
        mock_gemini.return_value = '```json\n[{"id": "REQ-1", "description": "Test"}]\n```'
        
        from src.agents.parser import requirements_agent
        
        state = _create_initial_state(
            jira_data={"key": "T-1", "fields": {"summary": "X", "description": "Y"}}
        )
        
        result = requirements_agent(state)
        self.assertEqual(len(result["requirements"]), 1)


class TestEvaluatorAgent(unittest.TestCase):
    """Tests for the Evaluator Agent."""
    
    @patch("src.agents.evaluator.call_gemini")
    def test_evaluation_with_evidence(self, mock_gemini):
        """Should evaluate requirements and populate traceability map."""
        mock_gemini.return_value = json.dumps([{
            "id": "REQ-1",
            "verdict": "Pass",
            "reasoning": "Found the endpoint.",
            "evidence": [{"file": "src/main.py", "lines": "L10-L15", "snippet": "app.post(...)"}]
        }])
        
        from src.agents.evaluator import evaluator_agent
        
        state = _create_initial_state(
            requirements=[{"id": "REQ-1", "description": "Login API", "verdict": "Unknown", "reasoning": "", "evidence": []}],
            pr_diff="+ app.post('/login')"
        )
        
        result = evaluator_agent(state)
        
        self.assertEqual(result["requirements"][0]["verdict"], "Pass")
        self.assertIn("REQ-1", result["traceability_map"])
        self.assertEqual(result["traceability_map"]["REQ-1"][0]["file"], "src/main.py")


class TestSynthesisAgent(unittest.TestCase):
    """Tests for the Synthesis Agent."""
    
    def test_all_pass_verdict(self):
        """All passing requirements should yield Pass verdict."""
        from src.agents.synthesis import synthesis_agent
        
        state = _create_initial_state(
            requirements=[
                {"id": "R1", "verdict": "Pass", "description": "...", "reasoning": "...", "evidence": ["a.py"]},
                {"id": "R2", "verdict": "Pass", "description": "...", "reasoning": "...", "evidence": ["b.py"]},
            ]
        )
        
        result = synthesis_agent(state)
        self.assertEqual(result["overall_verdict"], "Pass")
    
    def test_any_fail_yields_fail(self):
        """Any failed requirement should yield Fail verdict."""
        from src.agents.synthesis import synthesis_agent
        
        state = _create_initial_state(
            requirements=[
                {"id": "R1", "verdict": "Pass", "description": "...", "reasoning": "...", "evidence": []},
                {"id": "R2", "verdict": "Fail", "description": "...", "reasoning": "...", "evidence": []},
            ]
        )
        
        result = synthesis_agent(state)
        self.assertEqual(result["overall_verdict"], "Fail")
    
    def test_partial_verdict(self):
        """Partial requirements (no fails) should yield Partial verdict."""
        from src.agents.synthesis import synthesis_agent
        
        state = _create_initial_state(
            requirements=[
                {"id": "R1", "verdict": "Pass", "description": "...", "reasoning": "...", "evidence": []},
                {"id": "R2", "verdict": "Partial", "description": "...", "reasoning": "...", "evidence": []},
            ]
        )
        
        result = synthesis_agent(state)
        self.assertEqual(result["overall_verdict"], "Partial")
    
    def test_confidence_score_range(self):
        """Confidence score should always be between 0.0 and 1.0."""
        from src.agents.synthesis import synthesis_agent
        
        state = _create_initial_state(
            requirements=[
                {"id": "R1", "verdict": "Fail", "description": "...", "reasoning": "...", "evidence": []},
            ]
        )
        
        result = synthesis_agent(state)
        self.assertGreaterEqual(result["confidence_score"], 0.0)
        self.assertLessEqual(result["confidence_score"], 1.0)
    
    def test_empty_requirements(self):
        """Empty requirements should yield Fail with 0 confidence."""
        from src.agents.synthesis import synthesis_agent
        
        state = _create_initial_state(requirements=[])
        
        result = synthesis_agent(state)
        self.assertEqual(result["overall_verdict"], "Fail")
        self.assertEqual(result["confidence_score"], 0.0)


class TestOrchestrator(unittest.TestCase):
    """Tests for the LangGraph orchestration pipeline."""
    
    @patch("src.agents.verification.call_gemini")
    @patch("src.agents.evaluator.call_gemini")
    @patch("src.agents.parser.call_gemini")
    def test_full_pipeline_mock(self, mock_parser, mock_evaluator, mock_verifier):
        """Full pipeline should run end-to-end with mocked LLM calls."""
        import json
        
        mock_parser.return_value = json.dumps([
            {"id": "REQ-1", "description": "Implement login"},
            {"id": "REQ-2", "description": "Return 200 on success"}
        ])
        
        mock_evaluator.return_value = json.dumps([
            {"id": "REQ-1", "verdict": "Pass", "reasoning": "Found.", "evidence": [{"file": "main.py", "lines": "L1", "snippet": "..."}]},
            {"id": "REQ-2", "verdict": "Pass", "reasoning": "Returns 200.", "evidence": [{"file": "main.py", "lines": "L5", "snippet": "..."}]}
        ])
        
        from src.orchestrator import create_orchestrator
        
        initial_state = _create_initial_state()
        
        with patch.dict(os.environ, {}, clear=True):
            orchestrator = create_orchestrator()
            final_state = orchestrator.invoke(initial_state)
        
        self.assertEqual(final_state["overall_verdict"], "Pass")
        self.assertGreater(final_state["confidence_score"], 0.0)
        self.assertEqual(len(final_state["requirements"]), 2)
        self.assertIn("REQ-1", final_state["traceability_map"])


if __name__ == "__main__":
    unittest.main()
