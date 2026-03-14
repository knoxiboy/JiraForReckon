"""
Verification Agent

LangGraph node that generates and EXECUTES Python validation tests
for failed or partially met requirements. Provides empirical evidence
to support or challenge the Evaluator Agent's assessment.
"""

import logging
import os
import tempfile
import subprocess
from src.state import AgentState
from src.utils import call_gemini

logger = logging.getLogger("evaluator.verification")

SYSTEM_PROMPT = """You are a Test Automation Engineer.
Given a requirement and its evaluation result (including the PR diff context),
generate a minimal Python test script using `unittest` that would verify whether
the requirement is correctly implemented.

Rules:
- Use the `unittest` framework.
- Mock any external dependencies (database, auth services, etc.) using `unittest.mock`.
- Include at least one positive test and one negative test.
- The test must be self-contained and runnable with `python -m pytest <file>`.
- Return ONLY the python code, no markdown or explanation."""

# Maximum time allowed for test execution (seconds)
TEST_TIMEOUT = 30


def verification_agent(state: AgentState) -> AgentState:
    requirements = state.get("requirements", [])
    pr_diff = state.get("pr_diff", "")
    logs = list(state.get("logs", []))
    
    # Identify requirements that need verification
    to_verify = [r for r in requirements if r["verdict"] in ["Fail", "Partial"]]
    
    if not to_verify:
        logs.append("Verification Agent: All requirements passed. No tests needed.")
        return {**state, "logs": logs, "current_agent": "Verification"}
    
    logs.append(f"Verification Agent: Generating and running tests for {len(to_verify)} requirements...")
    
    test_outputs = []
    
    for req in to_verify:
        test_result = _generate_and_run_test(req, pr_diff, logs)
        test_outputs.append(test_result)
    
    # Summary
    executed = sum(1 for t in test_outputs if t.get("executed"))
    logs.append(f"Verification Agent: Completed. {executed}/{len(test_outputs)} tests executed successfully.")
    
    return {
        **state,
        "test_outputs": test_outputs,
        "logs": logs,
        "current_agent": "Verification"
    }


def _generate_and_run_test(req: dict, pr_diff: str, logs: list) -> dict:
    """Generate a test script for a requirement and attempt to execute it."""
    req_id = req.get("id", "UNKNOWN")
    
    prompt = (
        f"Requirement: {req['description']}\n"
        f"Current Verdict: {req['verdict']}\n"
        f"Reasoning: {req['reasoning']}\n"
        f"PR Diff Context:\n{pr_diff[:5000]}"
    )
    
    test_result = {
        "req_id": req_id,
        "test_code": "",
        "executed": False,
        "passed": False,
        "output": "",
        "error": ""
    }
    
    try:
        # Generate test code via LLM
        test_code = call_gemini(prompt, system_instruction=SYSTEM_PROMPT)
        clean_code = test_code.strip().replace("```python", "").replace("```", "").strip()
        test_result["test_code"] = clean_code
        
        logs.append(f"Verification Agent: Generated test for {req_id} ({len(clean_code)} chars)")
        
        # Write to temp file and execute
        with tempfile.NamedTemporaryFile(
            mode="w", suffix="_test.py", delete=False, prefix=f"eval_{req_id}_"
        ) as f:
            f.write(clean_code)
            temp_path = f.name
        
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", temp_path, "-v", "--tb=short", "--no-header"],
                capture_output=True,
                text=True,
                timeout=TEST_TIMEOUT,
                cwd=tempfile.gettempdir()
            )
            
            test_result["executed"] = True
            test_result["output"] = result.stdout[-2000:] if result.stdout else ""
            test_result["error"] = result.stderr[-1000:] if result.stderr else ""
            test_result["passed"] = result.returncode == 0
            
            status = "PASSED" if result.returncode == 0 else "FAILED"
            logs.append(f"Verification Agent: Test for {req_id} — {status}")
            
        except subprocess.TimeoutExpired:
            test_result["executed"] = True
            test_result["error"] = f"Test timed out after {TEST_TIMEOUT}s"
            logs.append(f"Verification Agent: Test for {req_id} — TIMED OUT")
            
        except FileNotFoundError:
            # pytest not installed — fall back to direct unittest
            try:
                result = subprocess.run(
                    ["python", temp_path],
                    capture_output=True,
                    text=True,
                    timeout=TEST_TIMEOUT
                )
                test_result["executed"] = True
                test_result["output"] = result.stdout[-2000:] if result.stdout else ""
                test_result["error"] = result.stderr[-1000:] if result.stderr else ""
                test_result["passed"] = result.returncode == 0
                
                status = "PASSED" if result.returncode == 0 else "FAILED"
                logs.append(f"Verification Agent: Test for {req_id} (direct) — {status}")
            except Exception as e:
                test_result["error"] = f"Execution failed: {str(e)}"
                logs.append(f"Verification Agent: Test execution failed for {req_id}: {e}")
        
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except OSError:
                pass
                
    except Exception as e:
        logger.error(f"Verification error for {req_id}: {e}")
        test_result["error"] = str(e)
        logs.append(f"Verification Agent: Failed to generate/run test for {req_id}: {e}")
    
    return test_result
