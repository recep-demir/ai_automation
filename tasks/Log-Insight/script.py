import os
import logging
from dotenv import load_dotenv

load_dotenv()

current_location = os.getcwd()
target_path = os.path.join(current_location,"tasks","Log-Insight","app.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        
        logging.FileHandler(target_path),
        logging.StreamHandler()
    ]
)

api_url = os.getenv("SECURITY_API_URL")

def connect_to_service():
    if not api_url:
        logging.error("SECURITY_API_URL environment variable is not set.")
        return
    
    else:
        logging.info("SECURITY_API_URL environment variable is set.")

connect_to_service()