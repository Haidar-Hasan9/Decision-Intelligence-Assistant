import os
from dotenv import load_dotenv

load_dotenv()  # Load .env from project root (or wherever)

class Settings:
    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    # Chroma
    CHROMA_PERSIST_DIR: str = os.path.join(os.path.dirname(__file__), "..", "chroma_db")
    # Embedding model name (same as used in preparation)
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    # LLM model
    LLM_MODEL_NAME: str = "llama-3.3-70b-versatile"
    # Retrieval
    TOP_K_RETRIEVAL: int = 5

settings = Settings()