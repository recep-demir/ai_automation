import json, os, sys, re, logging, requests
from groq import Groq
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

LOG_DIR = os.path.join(os.getcwd(),"project","AI-Insight-Integration")
APP_LOG_FILE = os.path.join(LOG_DIR,"app.log")
JSON_ALERT_FILE = os.path.join(LOG_DIR,"security_alert.json")

os.makedirs(LOG_DIR,exist_ok=True)



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(APP_LOG_FILE), logging.StreamHandler()]
)

class SecurityLogAnalyer:
    def __init__(self,file_name):
        self.log_file = file_name
        self.api_url = os.getenv("API_URL")
        self.ai_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model_name = "llama-3.1-8b-instant"
        self.failed_attempts = {}
        self.total_scanned = 0
        self.incidents_found = 0

    def process_logs(self):
        alerts = []
        LOG_PATTERN = re.compile(r"(?P<time>\d{4}[-.]\d{2}[-.]\d{2} \d{2}:\d{2}:\d{2}) - (?P<ip>\d{1,3}(?:\.\d{1,3}){3}) - ERROR - (?P<reason>.*)")

        try:
            with open(self.log_file, "r", encoding="utf-8") as file:
                for line in file:
                    match = LOG_PATTERN.search(line)

                    if match:
                        ip_match = match.group("ip")
                        timestamp_str = match.group("time").replace(".", "-")
                        reason = match.group("reason").strip()

                        current_log_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")



          





        except:
          print('An exception occurred')

        



    




SERVER_LOG_FILE = os.path.join(LOG_DIR, "server_logs.txt")

if not os.path.exists(SERVER_LOG_FILE):
    logging.error(f"Input file not found: {SERVER_LOG_FILE}")
    sys.exit(1)


analyzer = SecurityLogAnalyer(SERVER_LOG_FILE)
analyzer.process_logs()