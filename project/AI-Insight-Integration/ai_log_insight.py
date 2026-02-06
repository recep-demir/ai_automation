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
        self.alerts = []


    def process_logs(self):
        LOG_PATTERN = re.compile(r"(?P<time>\d{4}[-.]\d{2}[-.]\d{2} \d{2}:\d{2}:\d{2}) - (?P<ip>\d{1,3}(?:\.\d{1,3}){3}) - ERROR - (?P<reason>.*)")

        try:
            with open(self.log_file, "r", encoding="utf-8") as file:
                for line in file:
                    self.total_scanned +=1
                    match = LOG_PATTERN.search(line)

                    if match:
                        ip_match = match.group("ip")
                        timestamp_str = match.group("time").replace(".", "-")
                        reason = match.group("reason").strip()

                        current_log_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

                        if ip_match not in self.failed_attempts:
                            self.failed_attempts[ip_match]=[]

                        self.failed_attempts[ip_match].append(current_log_time)
                        
                        if len(self.failed_attempts[ip_match]) >=5:
                            first_of_five = self.failed_attempts[ip_match][0]
                            time_diff = (current_log_time - first_of_five).total_seconds()

                            if time_diff <60:
                                self.alerts.append({
                                    "ip": ip_match,
                                    "first_error": str(first_of_five),
                                    "last_error": str(current_log_time),
                                    "total_attempts": len(self.failed_attempts[ip_match]), 
                                    "reason": reason
                                })
                                self.incidents_found +=1

                                if self.api_url:
                                    self.report_ip_to_security(ip_match, self.api_url, timestamp_str, reason)








          





        except Exception as e: print(f"Hata: {e}")

        



    




SERVER_LOG_FILE = os.path.join(LOG_DIR, "server_logs.txt")

if not os.path.exists(SERVER_LOG_FILE):
    logging.error(f"Input file not found: {SERVER_LOG_FILE}")
    sys.exit(1)


analyzer = SecurityLogAnalyer(SERVER_LOG_FILE)
analyzer.process_logs()