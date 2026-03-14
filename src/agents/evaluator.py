"""
Evaluator Agent

LangGraph node that performs multi-step reasoning to evaluate a PR diff
against each extracted requirement. Populates the traceability map with
specific file paths, line numbers, and code snippets as evidence.
"""

import logging
import json
from src.state import AgentState
from src.utils import call_gemini

logger = logging.getLogger("evaluator.reasoning")

SYSTEM_PROMPT = """You are an elite Senior Software Engineer and Code Reviewer.
Your task is to evaluate a Pull Request Diff against a set of Acceptance Criteria (AC).
For each requirement, you must decide if it is:
- Pass: Fully implemented.
- Partial: Partially implemented or missing edge cases.
- Fail: Not implemented or incorrectly implemented.

For EACH requirement, provide:
1. id: The requirement ID (e.g., REQ-1).
2. verdict: Pass, Partial, or Fail.
3. reasoning: Detailed explanation of your assessment.
4. evidence: A list of objects with {file, lines, snippet} — the specific code locations that support your verdict. 'lines' should be a string like "L45-L60". 'snippet' should be the relevant code text.

Your output must be a JSON list of objects.
Example:
[
  {
    "id": "REQ-1",
    "verdict": "Pass",
    "reasoning": "The login endpoint is implemented with proper email/password validation.",
    "evidence": [{"file": "src/auth.ts", "lines": "L12-L25", "snippet": "app.post('/login', ...)"}]
  }
]"""


def evaluator_agent(state: AgentState) -> AgentState:
    requirements = state.get("requirements", [])
    pr_diff = state.get("pr_diff", "")
    pr_files = state.get("pr_files", [])
    pr_metadata = state.get("pr_metadata", {})
    
    logs = list(state.get("logs", []))
    logs.append(f"Evaluator Agent: Evaluating PR diff against {len(requirements)} requirements...")
    
    # Build rich context for the LLM
    req_context = "\n".join([f"{r['id']}: {r['description']}" for r in requirements])
    
    pr_context = f"PR Title: {pr_metadata.get('title', 'N/A')}\n"
    pr_context += f"PR Description: {pr_metadata.get('body', 'N/A')}\n"
    pr_context += f"Files Changed: {', '.join(pr_files) if pr_files else 'N/A'}\n"
    
    prompt = f"Requirements:\n{req_context}\n\n{pr_context}\nPull Request Diff:\n{pr_diff}"
    
    try:
        response = call_gemini(prompt, system_instruction=SYSTEM_PROMPT)
        clean_json = response.strip().replace("```json", "").replace("```", "")
        evaluation_data = json.loads(clean_json)
        
        # Update requirements with results and build traceability map
        updated_requirements = []
        traceability_map = {}
        eval_map = {e["id"]: e for e in evaluation_data}
        
        for req in requirements:
            eval_result = eval_map.get(req["id"], {})
            
            # Extract evidence — may be list of strings or list of dicts
            raw_evidence = eval_result.get("evidence", [])
            evidence_list = []
            traceability_entries = []
            
            for ev in raw_evidence:
                if isinstance(ev, dict):
                    evidence_list.append(
                        f"{ev.get('file', '?')}:{ev.get('lines', '?')}"
                    )
                    traceability_entries.append({
                        "file": ev.get("file", ""),
                        "lines": ev.get("lines", ""),
                        "snippet": ev.get("snippet", ""),
                        "verdict": eval_result.get("verdict", "Unknown")
                    })
                elif isinstance(ev, str):
                    evidence_list.append(ev)
                    traceability_entries.append({
                        "file": ev,
                        "lines": "",
                        "snippet": "",
                        "verdict": eval_result.get("verdict", "Unknown")
                    })
            
            updated_requirements.append({
                **req,
                "verdict": eval_result.get("verdict", "Unknown"),
                "reasoning": eval_result.get("reasoning", "No detail provided."),
                "evidence": evidence_list
            })
            
            # Populate traceability map: requirement ID -> list of code locations
            traceability_map[req["id"]] = traceability_entries
            
        logs.append(f"Evaluator Agent: Analysis complete. "
                     f"Traceability mapped for {len(traceability_map)} requirements.")
        
        return {
            **state,
            "requirements": updated_requirements,
            "traceability_map": traceability_map,
            "logs": logs,
            "current_agent": "Evaluator"
        }
    except Exception as e:
        logger.error(f"Evaluator error: {e}")
        logs.append(f"Evaluator Agent Error: {e}")
        return {**state, "error": str(e), "logs": logs}
