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
        
        self.tp = 0  # True Positives
        self.fp = 0  # False Positives
        self.total_logs = 0
        self.total_time = 0

    async def run_evaluation(self):
        logging.info("Starting evaluation...")

        try:
            df = pd.read_csv(self.csv_path)
            logging.info(f"Dataset loaded successfully with {len(df)} logs.")
        except Exception as e:
            logging.error(f"Error occurred while loading dataset: {e}")
            return
        
        self.total_logs = len(df)

        for index, row in df.iterrows():
            log_line = row['log_line']
            ground_truth = row['label']
            start_mark = time.perf_counter()

            results = await self.analyzer.process_single_batch([log_line])

            end_mark = time.perf_counter()
            self.total_time += (end_mark - start_mark)

            is_alert_generated = len(results) > 0

            if is_alert_generated:
                if ground_truth == 1:
                    self.tp += 1
                    logging.info(f"Line {index}: CORRECT - True Positive (Attack detected)")
                else:
                    self.fp += 1
                    logging.warning(f"Line {index}: FALSE POSITIVE - False positive alert generated!")

        self.report_results()

    def report_results(self):
        avg_latency = (self.total_time / self.total_logs) * 1000

        logging.info("=" * 40)
        logging.info("FINAL PERFORMANCE REPORT")
        logging.info("-" * 40)
        logging.info(f"Total Logs Processed : {self.total_logs}")
        logging.info(f"True Positives (TP)  : {self.tp}")
        logging.info(f"False Positives (FP) : {self.fp}")
        logging.info(f"Avg Latency Per Log  : {avg_latency:.2f} ms")
        logging.info("=" * 40)

if __name__ == "__main__":
    evaluator = SecurityEvaluator("test_logs.csv")
    asyncio.run(evaluator.run_evaluation())