import json, os, sys, re, logging, requests
from datetime import datetime
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
        self.failed_attempts = {}

    def report_ip_to_security(self, ip, url, time, reason):
        data = {"detected_ip": ip, "occured_at": time,"reason" : reason, "status": "alert"}
        try:
            response = requests.post(url, json=data, timeout=5)
            if response.status_code in [200, 201]:
                logging.info(f"Reported IP {ip} successfully.")
            else:
                logging.warning(f"API rejection: {response.status_code}")
        except Exception as e:
            logging.error(f"Network error:{ip}: {e}")

    def process_logs(self):
        alerts = []
        
        try:
            with open(self.log_file, "r", encoding="utf-8") as file:
                for line in file:
                    # Tüm verileri tek seferde yakalayan pattern    
                    LOG_PATTERN = re.compile(r"(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - (?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - ERROR - (?P<reason>.*)")
                    match = LOG_PATTERN.search(line)
                    if match:
                        ip_match = match.group("ip")
                        time_match = match.group("time")
                    reason_match = re.search(r" - ([^-]+)$", line)

                    if "ERROR" in line and ip_match and time_match:
                        timestamp = time_match.group(1) if time_match else "Unknown"
                        ip_address = ip_match.group(1)
                        reason = reason_match.group(1).strip() if reason_match else "Unknown"
                        current_log_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

                        if not ip_address in self.failed_attempts:
                            self.failed_attempts[ip_address] = []

                        self.failed_attempts[ip_address].append(current_log_time)

                        if len(self.failed_attempts[ip_address]) >= 5:
                            first_of_five = self.failed_attempts[ip_address][0]
                            time_diff = (current_log_time - first_of_five).total_seconds()

                            if time_diff <= 60:
                                new_entry = {
                                    "ip": ip_address,
                                    "first_error": str(first_of_five),
                                    "last_error": str(current_log_time),
                                    "total_attempts": len(self.failed_attempts[ip_address]), 
                                    "reason": reason}
                                alerts.append(new_entry)
                                
                                if self.api_url:
                                    self.report_ip_to_security(ip_address, self.api_url, timestamp, reason)
                                
                                self.failed_attempts[ip_address] = []
                            else:
                                self.failed_attempts[ip_address] = [current_log_time]


                                  



                            
                        

            with open(JSON_ALERT_FILE, "w", encoding="utf-8") as jf:
                json.dump(alerts, jf, indent=4, ensure_ascii=False)
            
            logging.info(f"Analysis complete. Found {len(alerts)} security violations.")

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

