import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

AVAILABLE_AI_PROVIDERS = ["openai", "gemini", "groq", "ollama"] # "anthropic" NA 

# --- API Keys ---
API_KEYS = {
    "openai": os.getenv("OPENAI_API_KEY"),
    "groq": os.getenv("GROQ_API_KEY"),
    "gemini": os.getenv("GEMINI_API_KEY"),  # if using Gemini API
}

# --- Provider URLs ---
MODEL_ENDPOINTS = {
    "openai": "https://api.openai.com/v1/models",
    "groq": "https://api.groq.com/openai/v1/models",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/models",
}


def list_models_by_provider(provider: str):
    """List models for a given provider dynamically."""
    provider = provider.lower()
    api_key = API_KEYS.get(provider)

    if provider == "gemini":
        url = f"{MODEL_ENDPOINTS['gemini']}?key={api_key}"
        resp = requests.get(url).json()
        if resp.get("error"):
            st.warning(f"Gemini Error: {resp['error'].get('message','Unknown error')}")
            return []
        
        # Filter Gemini models to only include text generation models
        text_models = []
        for m in resp.get("models", []):
            model_name = m["name"].split("/")[1]
            # Only include models that support generateContent and are for text generation
            if ("generateContent" in m.get("supportedGenerationMethods", []) and
                not any(excluded in model_name.lower() for excluded in ["vision", "embedding", "code"])):
                text_models.append(model_name)
        return text_models

    if not api_key:
        st.warning(f"No API key found for {provider}")
        return []

    url = MODEL_ENDPOINTS.get(provider)
    if not url:
        st.warning(f"No endpoint mapped for {provider}")
        return []

    headers = {"Authorization": f"Bearer {api_key}"}

    resp = requests.get(url, headers=headers).json()

    if resp.get("error"):
        st.warning(f"{provider.title()} Error: {resp['error'].get('message','Unknown error')}")
        return []

    if provider in ["openai", "groq"]:
        # Filter out embedding, whisper, and TTS models
        excluded_keywords = ["embed", "whisper", "tts"]
        return [
            item["id"] for item in resp["data"] 
            if not any(keyword in item["id"].lower() for keyword in excluded_keywords)
        ]

    return []


def list_ollama_models():
    """List locally available Ollama models."""
    try:
        resp = requests.get("http://localhost:11434/api/tags").json()
        return [m["name"] for m in resp["models"] if "embed" not in m["name"]]
    except Exception as e:
        st.warning(f"Ollama Error: {str(e)}")
        return []
