# Requirement Traceability Matrix (RTM)

This matrix maps each hackathon requirement to the specific component in the Jira Ticket Evaluator that satisfies it.

| ID | Requirement | Implementation Component | Evidence / Artifact |
|:---|:---|:---|:---|
| **M1** | GitHub Integration | `RetrieverAgent` | `src/agents/retriever.py` |
| **M2** | MCP Integration | `RetrieverAgent` + GitKraken MCP | `src/agents/retriever.py` |
| **M3** | AI Agents (Multi-step) | LangGraph `StateGraph` | `src/orchestrator.py` |
| **M4** | AI APIs (Gemini) | `call_gemini` utility | `src/utils.py` |
| **F1** | Requirement Parsing | `RequirementsAgent` | `src/agents/parser.py` |
| **F2** | Structured Verdict | `SynthesisAgent` | `src/agents/synthesis.py` |
| **F3** | Evidence Mapping | `EvaluatorAgent` (Line/Path focus) | `src/agents/evaluator.py` |
| **O1** | Custom Test Gen | `VerificationAgent` | `src/agents/verification.py` |
| **O2** | Dashboard UI | React Dashboard | `frontend/src/App.tsx` |
| **O3** | Confidence Score | `SynthesisAgent` scoring logic | `src/agents/synthesis.py` |

## Mapping Summary

### Feature: Feature Request
- **AC Parsing**: Handled by `parser.py` node.
- **Diff Logic**: Validated in `evaluator.py` node.
- **Traceability**: Output results contain specific `evidence` arrays (e.g., `["src/auth.ts:L45-L60"]`).

### Feature: Bug Report
- **Regression Check**: Evaluator Agent prioritizes finding missing fixes in the diff.
- **Verification**: `verification.py` generates a regression test script to verify the fix outcome.

### Feature: Refactor
- **Side-Effect Analysis**: Evaluator Agent checks for unintended logic changes outside the refactor scope.
