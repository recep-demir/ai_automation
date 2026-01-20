import os
import sys
import re
import logging
import requests
from dotenv import load_dotenv

# Initialize Environment Variables
load_dotenv()

# Setup Paths
current_location = os.getcwd()
target_path = os.path.join(current_location, "tasks", "Log-Insight", "app.log")

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(target_path),
        logging.StreamHandler()
    ]
)

# Constants from .env
API_URL = os.getenv("SECURITY_API_URL")

def report_ip_to_security(ip, url, time):
    """Sends detected malicious IP details to a security API."""
    data = {
        "detected_ip": ip,
        "occured_at": time,
        "status": "alert"
    }
    
    try:
        # We use a timeout to prevent the script from hanging if the API is down
        response = requests.post(url, json=data, timeout=5)
        
        if response.status_code == 201 or response.status_code == 200:
            logging.info(f"Reported IP {ip} successfully.")
        else:
            logging.warning(f"API rejection: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Network error during API report: {e}")

def process_logs():
    # 1. Check if the user provided the file argument
    if len(sys.argv) < 2:
        logging.error("Usage: python script.py <log_file_path>")
        sys.exit(1)

    file_name = sys.argv[1]

    # 2. Check if file exists
    if not os.path.exists(file_name):
        logging.error(f"Input file not found: {file_name}")
        sys.exit(1)

    # 3. Process the file
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            for line in file:
                # Regex for IP address
                ip_match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", line)
                # Regex for Timestamp (YYYY-MM-DD HH:MM:SS)
                time_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)

                if "ERROR" in line and ip_match:
                    ip_address = ip_match.group(1)
                    # Safe extraction of time
                    timestamp = time_match.group(1) if time_match else "Unknown Time"
                    
                    logging.error(f"Critical error detected from IP: {ip_address}")
                    
                    # Call API if URL is available
                    if API_URL:
                        report_ip_to_security(ip_address, API_URL, timestamp)
                    else:
                        logging.warning("Skipping API report: SECURITY_API_URL is not set.")

    except Exception as e:
        logging.critical(f"Unexpected system error: {e}")

if __name__ == "__main__":
    process_logs()