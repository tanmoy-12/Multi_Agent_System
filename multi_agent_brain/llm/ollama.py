import httpx
from .base import LLMProvider
from ..config import settings
import logging

logger = logging.getLogger(__name__)

class OllamaLLMProvider(LLMProvider):
    def __init__(self, model: str = None, base_url: str = None):
        self.model = model or settings.LLM_MODEL
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.endpoint = f"{self.base_url}/api/generate"

    async def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(self.endpoint, json=payload)
                response.raise_for_status()
                return response.json().get("response", "")
            except Exception as e:
                logger.error(f"Ollama generation failed: {e}")
                raise e