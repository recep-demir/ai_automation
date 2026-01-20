import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

api_url = os.getenv("SECURITY_API_URL")

def connect_to_service():
    if not api_url:
        print("Error:Api_url not found in enviroment variables!")
        return
    
    else:
        print(f"Connecting to service using: {api_url}...")

connect_to_service()