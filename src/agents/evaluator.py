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

Provide very clear reasoning and evidence (file paths and line numbers).
Your output must be a JSON list of objects, one for each input requirement ID."""

def evaluator_agent(state: AgentState) -> AgentState:
    requirements = state.get("requirements", [])
    pr_diff = state.get("pr_diff", "")
    
    logs = state.get("logs", [])
    logs.append(f"Evaluator Agent: Evaluating PR diff against {len(requirements)} requirements...")
    
    req_context = "\n".join([f"{r['id']}: {r['description']}" for r in requirements])
    prompt = f"Requirements:\n{req_context}\n\nPull Request Diff:\n{pr_diff}"
    
    try:
        response = call_gemini(prompt, system_instruction=SYSTEM_PROMPT)
        clean_json = response.strip().replace("```json", "").replace("```", "")
        evaluation_data = json.loads(clean_json)
        
        # Update requirements with results
        updated_requirements = []
        eval_map = {e["id"]: e for e in evaluation_data}
        
        for req in requirements:
            eval_result = eval_map.get(req["id"], {})
            updated_requirements.append({
                **req,
                "verdict": eval_result.get("verdict", "Unknown"),
                "reasoning": eval_result.get("reasoning", "No detail provided."),
                "evidence": eval_result.get("evidence", [])
            })
            
        logs.append("Evaluator Agent: Analysis complete.")
        return {
            **state,
            "requirements": updated_requirements,
            "logs": logs,
            "current_agent": "Evaluator"
        }
    except Exception as e:
        logger.error(f"Evaluator error: {e}")
        logs.append(f"Evaluator Agent Error: {e}")
        return {**state, "error": str(e), "logs": logs}
