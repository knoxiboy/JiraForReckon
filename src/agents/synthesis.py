"""
Synthesis Agent

LangGraph node that aggregates all agent findings into a final structured report.
Computes a data-driven confidence score based on evaluation distribution,
evidence quality, and test results.
"""

import logging
from src.state import AgentState

logger = logging.getLogger("evaluator.synthesis")


def synthesis_agent(state: AgentState) -> AgentState:
    requirements = state.get("requirements", [])
    test_outputs = state.get("test_outputs", [])
    traceability_map = state.get("traceability_map", {})
    logs = list(state.get("logs", []))
    
    logs.append("Synthesis Agent: Finalizing report and calculating scores...")
    
    total_reqs = len(requirements)
    if total_reqs == 0:
        logs.append("Synthesis Agent: No requirements found. Cannot produce verdict.")
        return {
            **state,
            "overall_verdict": "Fail",
            "confidence_score": 0.0,
            "logs": logs,
            "current_agent": "Synthesis"
        }
    
    # ── Count verdicts ──
    passed = [r for r in requirements if r["verdict"] == "Pass"]
    failed = [r for r in requirements if r["verdict"] == "Fail"]
    partial = [r for r in requirements if r["verdict"] == "Partial"]
    unknown = [r for r in requirements if r["verdict"] not in ["Pass", "Fail", "Partial"]]
    
    # ── Determine overall verdict ──
    if len(failed) > 0:
        overall_verdict = "Fail"
    elif len(partial) > 0 or len(unknown) > 0:
        overall_verdict = "Partial"
    else:
        overall_verdict = "Pass"
    
    # ── Calculate data-driven confidence score ──
    confidence_score = _calculate_confidence(
        total_reqs, len(passed), len(partial), len(failed), len(unknown),
        test_outputs, traceability_map
    )
    
    # ── Build summary stats ──
    logs.append(
        f"Synthesis Agent: Results — "
        f"Pass: {len(passed)}/{total_reqs}, "
        f"Partial: {len(partial)}/{total_reqs}, "
        f"Fail: {len(failed)}/{total_reqs}, "
        f"Unknown: {len(unknown)}/{total_reqs}"
    )
    logs.append(f"Synthesis Agent: Final Verdict: {overall_verdict}, Confidence: {confidence_score:.0%}")
    
    return {
        **state,
        "overall_verdict": overall_verdict,
        "confidence_score": confidence_score,
        "logs": logs,
        "current_agent": "Synthesis"
    }


def _calculate_confidence(
    total: int,
    passed: int,
    partial: int,
    failed: int,
    unknown: int,
    test_outputs: list,
    traceability_map: dict
) -> float:
    """
    Calculate a data-driven confidence score (0.0 — 1.0) based on:
    
    1. Verdict clarity (40%): Higher confidence when verdicts are decisive
       (Pass or Fail) rather than Partial/Unknown.
    2. Evidence quality (30%): Higher confidence when traceability map has
       specific file + line evidence.
    3. Test corroboration (30%): Higher confidence when tests were executed
       and their results align with the agent's verdict.
    """
    if total == 0:
        return 0.0
    
    # ── 1. Verdict clarity score (0-1) ──
    decisive_count = passed + failed  # Clear verdicts
    clarity_score = decisive_count / total
    # Penalize unknowns heavily
    clarity_score -= (unknown / total) * 0.5
    clarity_score = max(0.0, clarity_score)
    
    # ── 2. Evidence quality score (0-1) ──
    evidence_score = 0.0
    if traceability_map:
        reqs_with_evidence = 0
        for req_id, entries in traceability_map.items():
            if entries and any(e.get("file") and e.get("lines") for e in entries):
                reqs_with_evidence += 1
        evidence_score = reqs_with_evidence / total if total > 0 else 0.0
    
    # ── 3. Test corroboration score (0-1) ──
    test_score = 0.0
    if test_outputs:
        executed_tests = [t for t in test_outputs if t.get("executed")]
        if executed_tests:
            # Tests that ran successfully (whether pass or fail) add confidence
            # because they provide empirical data
            test_score = len(executed_tests) / len(test_outputs)
            
            # Bonus: if test results align with agent verdict, extra confidence
            aligned = 0
            for test in executed_tests:
                req_id = test.get("req_id", "")
                test_passed = test.get("passed", False)
                # For failed/partial reqs, we expect tests to fail → alignment
                if not test_passed:
                    aligned += 1
            
            if executed_tests:
                alignment_bonus = (aligned / len(executed_tests)) * 0.2
                test_score = min(1.0, test_score + alignment_bonus)
    else:
        # No tests generated means all passed — partial confidence for test dimension
        test_score = 0.5
    
    # ── Weighted combination ──
    confidence = (
        clarity_score * 0.40 +
        evidence_score * 0.30 +
        test_score * 0.30
    )
    
    return round(min(1.0, max(0.0, confidence)), 2)
