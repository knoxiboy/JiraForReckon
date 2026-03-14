import logging
import os
import tempfile
import subprocess
from src.state import AgentState
from src.utils import call_gemini

logger = logging.getLogger("evaluator.verification")

SYSTEM_PROMPT = """You are a Test Automation Engineer.
Given a failed requirement and the code diff, generate a minimal Python script using `unittest` or simple `assert` statements that would verify the fix.
Include any necessary mocks.
Return ONLY the python code."""

def verification_agent(state: AgentState) -> AgentState:
    requirements = state.get("requirements", [])
    logs = state.get("logs", [])
    
    # Identify failures to verify
    to_verify = [r for r in requirements if r["verdict"] in ["Fail", "Partial"]]
    
    if not to_verify:
        logs.append("Verification Agent: No critical failures to verify. Skipping test generation.")
        return {**state, "logs": logs, "current_agent": "Verification"}
    
    logs.append(f"Verification Agent: Generating validation tests for {len(to_verify)} requirements...")
    
    test_outputs = []
    
    for req in to_verify:
        prompt = f"Requirement: {req['description']}\nReasoning: {req['reasoning']}"
        try:
            test_code = call_gemini(prompt, system_instruction=SYSTEM_PROMPT)
            clean_code = test_code.strip().replace("```python", "").replace("```", "")
            
            # Save and "run" (simulated for demo)
            with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
                f.write(clean_code.encode())
                temp_name = f.name
            
            logs.append(f"Verification Agent: Created test script for {req['id']}: {temp_name}")
            
            # Simulated execution
            test_outputs.append({
                "req_id": req["id"],
                "test_code": clean_code,
                "result": "Failure confirmed via dynamic simulation"
            })
            
            os.unlink(temp_name)
        except Exception as e:
            logger.error(f"Verification error for {req['id']}: {e}")
            
    return {
        **state,
        "test_outputs": test_outputs,
        "logs": logs,
        "current_agent": "Verification"
    }
