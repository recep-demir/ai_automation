import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    

    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./chroma_db")
    
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls):
        required = ["GROQ_API_KEY", "EMBEDDING_MODEL"]
        for var in required:
            if not getattr(cls, var):
                raise EnvironmentError(f"CRITICAL: {var} is not set in .env file!")

Config.validate()
