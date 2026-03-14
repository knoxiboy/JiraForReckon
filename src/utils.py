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
    Generalized call to Gemini 2.0 Flash.
    """
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
