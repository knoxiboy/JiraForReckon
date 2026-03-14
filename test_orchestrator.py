import os
import sys
import logging
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.state import AgentState
from src.orchestrator import create_orchestrator

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_orchestrator")

def run_test():
    jira_key = "PROJ-123"
    pr_url = "https://github.com/owner/repo/pull/45"
    
    initial_state = AgentState(
        jira_key=jira_key,
        pr_url=pr_url,
        jira_data={},
        pr_metadata={},
        pr_diff="",
        pr_files=[],
        requirements=[],
        overall_verdict="Unknown",
        confidence_score=0.0,
        traceability_map={},
        test_outputs=[],
        current_agent="Start",
        logs=["Initializing test run..."],
        error=None
    )
    
    try:
        logger.info("Starting orchestrator...")
        orchestrator = create_orchestrator()
        final_state = orchestrator.invoke(initial_state)
        
        print("\n=== FINAL STATE ===")
        print(f"Verdict: {final_state.get('overall_verdict')}")
        print(f"Confidence: {final_state.get('confidence_score')}")
        print(f"Requirements: {len(final_state.get('requirements', []))}")
        for req in final_state.get('requirements', []):
            print(f" - [{req['verdict']}] {req['id']}: {req['description']}")
        
        print("\n=== LOGS ===")
        for log in final_state.get("logs", []):
            print(f" > {log}")
            
    except Exception as e:
        logger.error(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
