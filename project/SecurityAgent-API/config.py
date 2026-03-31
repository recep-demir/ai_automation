import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API & Model Settings
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    # Paths
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./chroma_db")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")



Config.validate()
