import asyncio
import pandas as pd
import time
import logging
from analyzer_logic import SecurityLogAnalyzer
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [EVALUATION] - %(message)s'
)

class SecurityEvaluator:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.analyzer = SecurityLogAnalyzer()
        
        self.actual_attack_ips = set()
        
        # Metrics
        self.tp = 0  # True Positives
        self.fp = 0  # False Positives
        self.fn = 0  # False Negatives
        self.total_logs = 0

    async def run_evaluation(self):
        logging.info("Optimized Evaluation Pipeline starting...")

        try:
            df = pd.read_csv(self.csv_path)
            self.total_logs = len(df)
            
            temp_ips = df[df['label'] == 1]['log_line'].str.extract(r'(\d{1,3}(?:\.\d{1,3}){3})')[0]
            self.actual_attack_ips = set(temp_ips.unique())
            
            logging.info(f"Dataset loaded. Total Logs: {self.total_logs}, Total Attacking IPs to Catch: {len(self.actual_attack_ips)}")
        except Exception as e:
            logging.error(f"Data loading failed: {e}")
            return


        log_batch = df['log_line'].tolist()

        start_time = time.perf_counter()
        detected_alerts = await self.analyzer.process_single_batch(log_batch)        
        end_time = time.perf_counter()

        duration_ms = (end_time - start_time) * 1000

        detected_ips = {alert.get("ip") for alert in detected_alerts if alert.get("ip")}

        self.tp = len(self.actual_attack_ips.intersection(detected_ips))
        self.fp = len(detected_ips - self.actual_attack_ips)
        self.fn = len(self.actual_attack_ips - detected_ips)
        self.report_final_metrics(duration_ms)

    def report_final_metrics(self, duration_ms):
        recall = (self.tp / (self.tp + self.fn)) * 100 if (self.tp + self.fn) > 0 else 0
        
        precision = (self.tp / (self.tp + self.fp)) * 100 if (self.tp + self.fp) > 0 else 0

        logging.info("=" * 50)
        logging.info("🏆 FINAL SYSTEM EVALUATION REPORT")
        logging.info("-" * 50)
        logging.info(f"Total Logs Processed       : {self.total_logs}")
        logging.info(f"Execution Time             : {duration_ms:.2f} ms")
        logging.info(f"Avg Latency per Log        : {duration_ms / self.total_logs:.2f} ms")
        logging.info("-" * 50)
        logging.info(f"True Positives (TP)        : {self.tp} (Doğru Teşhis)")
        logging.info(f"False Positives (FP)       : {self.fp} (Yanlış Alarm)")
        logging.info(f"False Negatives (FN)       : {self.fn} (Kaçırılan Tehdit)")
        logging.info("-" * 50)
        logging.info(f"RECALL (Duyarlılık)        : %{recall:.2f}")
        logging.info(f"PRECISION (Kesinlik)       : %{precision:.2f}")
        logging.info("=" * 50)

if __name__ == "__main__":
    evaluator = SecurityEvaluator("test_logs.csv")
    asyncio.run(evaluator.run_evaluation())