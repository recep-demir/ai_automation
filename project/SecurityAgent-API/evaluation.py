import requests
import pandas as pd
import time
import logging

# Configure standard logging format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [EVALUATION] - %(message)s'
)

class SecurityEvaluator:
    def __init__(self, csv_path: str, api_endpoint: str = "http://127.0.0.1:8000/analyze"):
        self.csv_path = csv_path
        self.api_endpoint = api_endpoint # API Endpoint address for the Docker container
        
        self.actual_attack_ips = set()
        
        # Performance and Accuracy Metrics
        self.tp = 0  # True Positives
        self.fp = 0  # False Positives
        self.fn = 0  # False Negatives
        self.total_logs = 0

    def run_evaluation(self):
        logging.info("End-to-End API Evaluation Pipeline starting...")

        # 1. Load Dataset
        try:
            df = pd.read_csv(self.csv_path)
            self.total_logs = len(df)
            
            # Extract actual malicious IPs based on label == 1
            temp_ips = df[df['label'] == 1]['log_line'].str.extract(r'(\d{1,3}(?:\.\d{1,3}){3})')[0]
            self.actual_attack_ips = set(temp_ips.unique())
            
            logging.info(f"Dataset loaded. Total Logs: {self.total_logs}, Total Attacking IPs to Catch: {len(self.actual_attack_ips)}")
        except Exception as e:
            logging.error(f"Data loading failed: {e}")
            return

        # 2. Prepare Payload for API
        log_batch = df['log_line'].tolist()
        payload = {"logs": log_batch}
        headers = {"Content-Type": "application/json"}

        # 3. HTTP POST Request and Latency Measurement
        start_time = time.perf_counter()
        
        try:
            # Sending the request to the FastAPI container
            logging.info(f"Sending {self.total_logs} logs to {self.api_endpoint}...")
            response = requests.post(
                self.api_endpoint, 
                json=payload, 
                headers=headers,
                timeout=120 # Timeout set to 120 seconds for heavy AI processing
            )
            response.raise_for_status() # Raise exception if HTTP status code is not 200 OK
            
            api_result = response.json()
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Network or API Error: {e}")
            return
            
        end_time = time.perf_counter()

        # 4. Metric Calculations
        duration_ms = (end_time - start_time) * 1000

        # Safely extract IPs from the API JSON response
        # Assuming the API returns a list of dictionaries directly, or inside an 'alerts' key
        if isinstance(api_result, list):
            detected_alerts = api_result
        elif isinstance(api_result, dict):
            detected_alerts = api_result.get("alerts", api_result.get("analysis", []))
        else:
            detected_alerts = []

        detected_ips = {alert.get("ip") for alert in detected_alerts if isinstance(alert, dict) and alert.get("ip")}

        self.tp = len(self.actual_attack_ips.intersection(detected_ips))
        self.fp = len(detected_ips - self.actual_attack_ips)
        self.fn = len(self.actual_attack_ips - detected_ips)
        
        self.report_final_metrics(duration_ms)

    def report_final_metrics(self, duration_ms: float):
        recall = (self.tp / (self.tp + self.fn)) * 100 if (self.tp + self.fn) > 0 else 0
        precision = (self.tp / (self.tp + self.fp)) * 100 if (self.tp + self.fp) > 0 else 0
        
        # Calculate Throughput
        throughput = self.total_logs / (duration_ms / 1000) if duration_ms > 0 else 0

        logging.info("=" * 50)
        logging.info("🏆 FINAL E2E SYSTEM EVALUATION REPORT")
        logging.info("-" * 50)
        logging.info(f"Total Logs Processed       : {self.total_logs}")
        logging.info(f"Total Network Latency      : {duration_ms:.2f} ms")
        logging.info(f"Throughput                 : {throughput:.2f} logs/sec")
        logging.info("-" * 50)
        logging.info(f"True Positives (TP)        : {self.tp} (Doğru Teşhis)")
        logging.info(f"False Positives (FP)       : {self.fp} (Yanlış Alarm)")
        logging.info(f"False Negatives (FN)       : {self.fn} (Kaçırılan Tehdit)")
        logging.info("-" * 50)
        logging.info(f"RECALL (Duyarlılık)        : %{recall:.2f}")
        logging.info(f"PRECISION (Kesinlik)       : %{precision:.2f}")
        logging.info("=" * 50)

if __name__ == "__main__":
    # If the file 'test_logs.csv' is in another directory, update the path
    evaluator = SecurityEvaluator("test_logs.csv")
    evaluator.run_evaluation()