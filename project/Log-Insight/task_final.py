import json, os, sys, re, logging, requests, datetime
from dotenv import load_dotenv

load_dotenv()


LOG_DIR = os.path.join(os.getcwd(), "project", "Log-Insight")
APP_LOG_FILE = os.path.join(LOG_DIR, "app.log")
JSON_ALERT_FILE = os.path.join(LOG_DIR, "security_alert.json")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(APP_LOG_FILE), logging.StreamHandler()]
)

class LogParser:
    def __init__(self, file_name):
        self.log_file = file_name
        self.api_url = os.getenv("API_URL")

    def report_ip_to_security(self, ip, url, time):
        data = {"detected_ip": ip, "occured_at": time, "status": "alert"}
        try:
            response = requests.post(url, json=data, timeout=5)
            if response.status_code in [200, 201]:
                logging.info(f"Reported IP {ip} successfully.")
            else:
                logging.warning(f"API rejection: {response.status_code}")
        except Exception as e:
            logging.error(f"Network error: {e}")

    def process_logs(self):
        alerts = []
        
        try:
            with open(self.log_file, "r", encoding="utf-8") as file:
                for line in file:
                    # Regexler
                    ip_match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", line)
                    time_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
                    reason_match = re.search(r" - ([^-]+)$", line)

                    if "ERROR" in line and ip_match:
                        timestamp = time_match.group(1) if time_match else "Unknown"
                        ip_address = ip_match.group(1)
                        reason = reason_match.group(1).strip() if reason_match else "Unknown"
                        time_obj = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                        

                        new_entry = {"time": timestamp, "ip": ip_address, "reason": reason}
                        alerts.append(new_entry)

                        if self.api_url:
                            self.report_ip_to_security(ip_address, self.api_url, timestamp)


                            


                        

            with open(JSON_ALERT_FILE, "w", encoding="utf-8") as jf:
                json.dump(alerts, jf, indent=4, ensure_ascii=False)
            
            logging.info(f"Found {len(alerts)} alerts. Saved to JSON.")

        except Exception as e:
            logging.critical(f"System error: {e}")






if len(sys.argv)<2:
    logging.error("Usage: python script.py <log_file_path>")
    sys.exit(1)


file_name = sys.argv[1]

if not os.path.exists(file_name):
        logging.error(f"Input file not found: {file_name}")
        sys.exit(1)








analyzer = LogParser(file_name)

