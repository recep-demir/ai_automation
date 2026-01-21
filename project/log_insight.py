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

