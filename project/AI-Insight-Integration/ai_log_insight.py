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

    def analyze_with_ai(self, ip, log_data):
        try:
          prompt = f"""
          IP to be analysed: {ip}
          Log data: {log_data}
          Task: Review the logs above. Is this a brute force attack? Briefly (in no more than 2 sentences) state the risk level and your recommendation.
          """

          response = self.ai_client.chat.completions.create(
              model=self.model_name,
              messages=[
                  {"role": "system", "content": "You are a senior cyber security analyst."},
                  {"role": "user", "content": prompt}
              ],
              temperature=0.5
          )
          return response.choices[0].message.content
        
    
        except Exception as e:
          return f"AI analysis could not be performed: {e}"



    def report_ip_to_security(self, ip,url, time, reason,ai):
        data = {"detected_ip": ip, "occured_at": time,"reason" : reason, "status": "alert", "ai_result": ai}

        try:
            response = requests.post(url, json=data, timeout=5)

            if response.status_code in [200,201]:
                logging.info(f"Reported IP {ip} successfully.")
            else:
                logging.warning(f"API rejection: {response.status_code}")
          


        except Exception as e:
            logging.error(f"Network error:{ip}: {e}")




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

                        self.failed_attempts[ip_match].append((current_log_time, reason))
                        
                        if len(self.failed_attempts[ip_match]) >=5:
                            first_of_five = self.failed_attempts[ip_match][0][0]
                            time_diff = (current_log_time - first_of_five).total_seconds()

                            if time_diff <60:
                                logs_for_ai = "\n".join([line[1] for line in self.failed_attempts[ip_match][-5:] if isinstance(line[1], str)])
                                ai_result = self.analyze_with_ai(ip_match, logs_for_ai)

                                self.alerts.append({
                                    "ip": ip_match,
                                    "first_error": str(first_of_five),
                                    "last_error": str(current_log_time),
                                    "total_attempts": len(self.failed_attempts[ip_match]), 
                                    "reason": reason,
                                    "ai_result": ai_result
                                })

                                
                                self.incidents_found +=1

                                
                                

                                if self.api_url:
                                    self.report_ip_to_security(ip_match, self.api_url, timestamp_str, reason,ai_result)
                                    self.failed_attempts[ip_match] = []
                            else:
                                self.failed_attempts[ip_match] = [(current_log_time,reason)]


            with open (JSON_ALERT_FILE,"a", encoding="utf-8") as jf:
                json.dump(self.alerts, jf, indent=4, ensure_ascii=False)
                
                logging.info(f"Analysis complete. Found {len(self.alerts)} security violations.")




        except Exception as e: logging.error(f"Hata: {e}")

    




SERVER_LOG_FILE = os.path.join(LOG_DIR, "server_logs.txt")

if not os.path.exists(SERVER_LOG_FILE):
    logging.error(f"Input file not found: {SERVER_LOG_FILE}")
    sys.exit(1)


analyzer = SecurityLogAnalyer(SERVER_LOG_FILE)
analyzer.process_logs()