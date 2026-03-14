import logging
from src.state import AgentState

logger = logging.getLogger("evaluator.synthesis")

def synthesis_agent(state: AgentState) -> AgentState:
    requirements = state.get("requirements", [])
    logs = state.get("logs", [])
    
    logs.append("Synthesis Agent: Finalizing report and calculating scores...")
    
    total_reqs = len(requirements)
    passed_reqs = len([r for r in requirements if r["verdict"] == "Pass"])
    failed_reqs = len([r for r in requirements if r["verdict"] == "Fail"])
    partial_reqs = len([r for r in requirements if r["verdict"] == "Partial"])
    
    overall_verdict = "Pass"
    if failed_reqs > 0:
        overall_verdict = "Fail"
    elif partial_reqs > 0 or passed_reqs < total_reqs:
        overall_verdict = "Partial"
        
    confidence_score = 0.9 if total_reqs > 0 else 0.0
    # Penalty for partials
    if partial_reqs > 0:
        confidence_score -= 0.1
    
    logs.append(f"Synthesis Agent: Final Verdict: {overall_verdict}, Confidence: {confidence_score}")
    
    return {
        **state,
        "overall_verdict": overall_verdict,
        "confidence_score": confidence_score,
        "logs": logs,
        "current_agent": "Synthesis"
    }
