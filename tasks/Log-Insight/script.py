import os
import sys
import re
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

file_name = sys.argv[1]

if not os.path.exists(file_name):
    logging.error(f"Error: The file '{file_name}' was not found!")
    sys.exit(1)

try:
    with open(file_name,"r",encoding="utf-8") as file:
        for line in file:
            match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", line)
            if "ERROR" in line and match:
                ip_address = match.group(1)
                logging.error(f"Crirical Error! Source IP: {ip_address}")



except Exception as e:
    logging.error(f"An error occurred: {e}") 
    sys.exit()