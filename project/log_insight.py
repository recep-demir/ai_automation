import sys
import os
import requests
import re
import logging
from dotenv import load_dotenv

load_dotenv()

current_location = os.getcwd()
target_path = os.path.join(current_location,"project","final_error_report.txt")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(target_path),
        logging.StreamHandler()
    ]
)

API_URL = os.getenv("API_URL")




def process_logs():
    if len(sys.argv) < 2 :
        logging.error("Usage:python <script_name> <log_file_path>")
        sys.exit(1)

    if not os.path.exists(sys.argv(1)):
        logging.error(f"Input file not found: {sys.argv(1)}")
        sys.exit(1)

    file_name = sys.argv[1]

    try:
        with open (file_name,"r",encoding="utf-8") as file:
            for line in file:
                ip_match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", line)
                time_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)

                if 


    


