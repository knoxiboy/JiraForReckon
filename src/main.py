import os
import re
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from dotenv import load_dotenv

# Import our agents and state
from src.state import AgentState
from src.orchestrator import create_orchestrator

load_dotenv()

app = FastAPI(title="Jira Ticket Evaluator API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("evaluator.api")

# Regex patterns for validation
GITHUB_PR_PATTERN = re.compile(
    r'^https?://github\.com/[\w.\-]+/[\w.\-]+/pull/\d+/?$'
)
JIRA_KEY_PATTERN = re.compile(
    r'^[A-Z][A-Z0-9_]+-\d+$'
)

class EvaluationRequest(BaseModel):
    jira_key: str
    pr_url: str

    @field_validator('pr_url')
    @classmethod
    def validate_pr_url(cls, v: str) -> str:
        v = v.strip()
        if not GITHUB_PR_PATTERN.match(v):
            raise ValueError(
                'Invalid GitHub PR URL. Expected format: https://github.com/{owner}/{repo}/pull/{number}'
            )
        return v

    @field_validator('jira_key')
    @classmethod
    def validate_jira_key(cls, v: str) -> str:
        v = v.strip().upper()
        if not JIRA_KEY_PATTERN.match(v):
            raise ValueError(
                'Invalid Jira ticket key. Expected format: PROJECT-123 (e.g., ENG-456, PROJ-12)'
            )
        return v

@app.get("/")
async def root():
    return {"message": "Jira Ticket Evaluator API is running"}

@app.post("/api/evaluate")
async def evaluate_pr(request: EvaluationRequest):
    """
    Triggers the autonomous evaluation pipeline.
    """
    logger.info(f"Evaluation requested for Jira: {request.jira_key}, PR: {request.pr_url}")
    
    initial_state = AgentState(
        jira_key=request.jira_key,
        pr_url=request.pr_url,
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
        logs=["Initializing evaluation..."],
        error=None
    )
    
    try:
        orchestrator = create_orchestrator()
        final_state = orchestrator.invoke(initial_state)
        return final_state
    except Exception as e:
        logger.error(f"Error during evaluation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
