# AI Chat Providers
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
load_dotenv()

class LLMFactory:
    def __init__(self, temperature: float = 0.5, streaming: bool = False):
        self.temperature = temperature
        self.streaming = streaming

        # provider -> class, their any special kwargs
        self.__provider_map = {
            "openai" : (ChatOpenAI, {}),
            "gemini" : (ChatGoogleGenerativeAI, {"google_api_key" : os.getenv("GEMINI_API_KEY"), "disable_streaming" : not streaming}),
            "groq" : (ChatGroq, {}),
            "ollama" : (ChatOllama, {"stream" : streaming, "num_predict" : 360}), # we can add num_predict, max_tokens, etc params if needed
        }
    
    def create(self, provider:str, model: str):
        provider = provider.lower()
        if provider not in self.__provider_map:
            raise ValueError(f"Unsupported Provider: {provider}")
        
        llm_chat_model, extra_kwargs = self.__provider_map[provider]

        kwargs = {
            "model" : model,
            "temperature" : self.temperature,
            "streaming" : self.streaming,
            **extra_kwargs
        }

        # case for ollama
        if "stream" or "disable_streaming" in kwargs: kwargs.pop("streaming", None) # remove streaming, since stream is used

        return llm_chat_model(**kwargs)
