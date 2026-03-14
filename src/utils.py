import os
import logging
from google import genai
from google.genai import types

logger = logging.getLogger("evaluator.utils")

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")
    return genai.Client(api_key=api_key)

def call_gemini(prompt: str, system_instruction: str = None) -> str:
    """
    Generalized call to Gemini 2.0 Flash with mock fallback.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.info("GEMINI_API_KEY not set. Returning mock response based on prompt.")
        # Return mock JSON based on context
        if "Acceptance Criteria" in prompt or "Jira" in system_instruction:
            return '[{"id": "REQ-1", "description": "Implement User Login API"}, {"id": "REQ-2", "description": "Return 200 on success"}]'
        elif "Pull Request Diff" in prompt:
            if "users" in prompt:  # Trigger a fail
                return '[{"id": "REQ-1", "verdict": "Fail", "reasoning": "Requirement was for login API, but implementation shows user fetching.", "evidence": ["src/main.py"]}, {"id": "REQ-2", "verdict": "Fail", "reasoning": "No 200 OK return found for login.", "evidence": ["src/main.py"]}]'
            return '[{"id": "REQ-1", "verdict": "Pass", "reasoning": "Found login endpoint.", "evidence": ["src/main.py"]}, {"id": "REQ-2", "verdict": "Pass", "reasoning": "Returns 200.", "evidence": ["src/main.py"]}]'
        elif "Test Automation Engineer" in system_instruction:
            return 'def test_login(): assert True'
        return "Mock Gemini Response"

    client = get_gemini_client()
    
    config = types.GenerateContentConfig(
        temperature=0.1,
        max_output_tokens=4096,
        system_instruction=system_instruction
    )
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=config
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise
