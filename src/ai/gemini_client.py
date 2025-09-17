import os
from google import genai
from google.genai import types as genai_types

def get_gemini_client():
    """Get configured Gemini client instance."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    return genai.Client(api_key=api_key)

def get_model(tools=None, model_name=None):
    """Legacy function for backward compatibility."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    client = genai.Client(api_key=api_key)
    return client