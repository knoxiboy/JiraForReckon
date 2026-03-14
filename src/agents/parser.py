import logging
import json
from src.state import AgentState, Requirement
from src.utils import call_gemini

logger = logging.getLogger("evaluator.parser")

SYSTEM_PROMPT = """You are an expert Requirements Engineer.
Your task is to parse a Jira ticket (Summary and Description) and extract a list of discrete, testable Acceptance Criteria (AC).
For each criteria, provide:
1. ID: A unique identifier (e.g., REQ-1).
2. Description: A clear, concise statement of what must be implemented.

Output your response as a JSON list of objects."""

def requirements_agent(state: AgentState) -> AgentState:
    jira_data = state.get("jira_data", {})
    description = jira_data.get("fields", {}).get("description", "")
    summary = jira_data.get("fields", {}).get("summary", "")
    
    logs = state.get("logs", [])
    logs.append("Requirements Agent: Analyzing ticket description for requirements...")
    
    prompt = f"Summary: {summary}\nDescription: {description}"
    
    try:
        response = call_gemini(prompt, system_instruction=SYSTEM_PROMPT)
        # Clean potential markdown from response
        clean_json = response.strip().replace("```json", "").replace("```", "")
        requirements_data = json.loads(clean_json)
        
        requirements = [
            Requirement(
                id=r["id"],
                description=r["description"],
                verdict="Unknown",
                reasoning="",
                evidence=[]
            ) for r in requirements_data
        ]
        
        logs.append(f"Requirements Agent: Extracted {len(requirements)} requirements.")
        return {
            **state,
            "requirements": requirements,
            "logs": logs,
            "current_agent": "RequirementsParser"
        }
    except Exception as e:
        logger.error(f"Parser error: {e}")
        logs.append(f"Requirements Agent Error: {e}")
        return {**state, "error": str(e), "logs": logs}
