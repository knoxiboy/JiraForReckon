from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict

class Requirement(TypedDict):
    id: str
    description: str
    verdict: str  # Pass, Partial, Fail, Unknown
    reasoning: str
    evidence: List[str]  # File paths or code snippets

class AgentState(TypedDict):
    # Inputs
    jira_key: str
    pr_url: str
    
    # Fetched Context
    jira_data: Dict[str, Any]
    pr_metadata: Dict[str, Any]
    pr_diff: str
    pr_files: List[str]
    
    # Processed Data
    requirements: List[Requirement]
    
    # Evaluation Results
    overall_verdict: str
    confidence_score: float
    traceability_map: Dict[str, List[Dict[str, Any]]]
    
    # Test Results
    test_outputs: List[Dict[str, Any]]
    
    # System Metadata
    current_agent: str
    logs: List[str]
    error: Optional[str]
