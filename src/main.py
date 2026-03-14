import os
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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

class EvaluationRequest(BaseModel):
    jira_key: str
    pr_url: str

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
