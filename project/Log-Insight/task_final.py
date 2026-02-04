import json, os, sys, re, logging, requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


LOG_DIR = os.path.join(os.getcwd(), "project", "Log-Insight")
APP_LOG_FILE = os.path.join(LOG_DIR, "app.log")
JSON_ALERT_FILE = os.path.join(LOG_DIR, "security_alert.json")
os.makedirs(LOG_DIR, exist_ok=True)


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
        # LOG FORMATINA UYGUN REGEX: Önce Time, sonra IP
        LOG_PATTERN = re.compile(r"(?P<time>\d{4}[-.]\d{2}[-.]\d{2} \d{2}:\d{2}:\d{2}) - (?P<ip>\d{1,3}(?:\.\d{1,3}){3}) - ERROR - (?P<reason>.*)")
        
        try:
            with open(self.log_file, "r", encoding="utf-8") as file:
                for line in file:
                    match = LOG_PATTERN.search(line)
                    
                    if match:
                        ip_address = match.group("ip")
                        timestamp_str = match.group("time").replace(".", "-") # Bazı satırlarda nokta var, standardize ediyoruz
                        reason = match.group("reason").strip()
                        
                        current_log_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

                        if ip_address not in self.failed_attempts:
                            self.failed_attempts[ip_address] = []

                        self.failed_attempts[ip_address].append(current_log_time)

                        # 5 veya daha fazla hata kontrolü
                        if len(self.failed_attempts[ip_address]) >= 5:
                            first_of_five = self.failed_attempts[ip_address][0]
                            time_diff = (current_log_time - first_of_five).total_seconds()

                            if time_diff <= 60:
                                alerts.append({
                                    "ip": ip_address,
                                    "first_error": str(first_of_five),
                                    "last_error": str(current_log_time),
                                    "total_attempts": len(self.failed_attempts[ip_address]), 
                                    "reason": reason
                                })
                                
                                if self.api_url:
                                    self.report_ip_to_security(ip_address, self.api_url, timestamp_str, reason)
                                
                                self.failed_attempts[ip_address] = []
                            else:
                                # 60 saniyeyi geçtiyse, eski kayıtları temizle ve güncel hatayı ilk eleman yap
                                self.failed_attempts[ip_address] = [current_log_time]

            # JSON yazma işlemini döngü dışına, try bloğunun sonuna alıyoruz
            with open(JSON_ALERT_FILE, "w", encoding="utf-8") as jf:
                json.dump(alerts, jf, indent=4, ensure_ascii=False)
            
            logging.info(f"Analysis complete. Found {len(alerts)} security violations.")

        except Exception as e:
            logging.error(f"Error: {e}")


            
# 1. Ham log dosyasının yolunu sabit olarak tanımla
# server_log.txt dosyasının LOG_DIR içinde olduğunu varsayıyoruz
SERVER_LOG_FILE = os.path.join(LOG_DIR, "server_logs.txt")

# 2. Dosya var mı kontrol et
if not os.path.exists(SERVER_LOG_FILE):
    logging.error(f"Input file not found: {SERVER_LOG_FILE}")
    # Eğer dosya yoksa, kullanıcıya oluşturması gerektiğini hatırlat
    sys.exit(1)

# 3. Analizi başlat
analyzer = LogParser(SERVER_LOG_FILE)
analyzer.process_logs()

"""
if len(sys.argv)<2:
    logging.error("Usage: python script.py <log_file_path>")
    sys.exit(1)


file_name = sys.argv[1]

if not os.path.exists(file_name):
        logging.error(f"Input file not found: {file_name}")
        sys.exit(1)



analyzer = LogParser(file_name)

"""