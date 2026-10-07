import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen2.5:3b")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.55"))
    MAX_CANDIDATES_PER_TASK: int = int(os.getenv("MAX_CANDIDATES_PER_TASK", "5"))
    DEPENDENCY_WEIGHTS: dict = {
        "semantic": 0.25,
        "io": 0.25,
        "llm": 0.50
    }

settings = Settings()