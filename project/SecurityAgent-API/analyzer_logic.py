import json, os, re, logging
from groq import Groq
from datetime import datetime
from dotenv import load_dotenv

from retriever import get_ai_support

load_dotenv()
class SecurityLogAnalyzer:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        model_name = os.getenv("MODEL_NAME")

        if not api_key or not model_name:
            logging.critical("Environment Variable Error: GROQ_API_KEY and MODEL_NAME must be set.")
            raise EnvironmentError("Missing configuration for GROQ_API_KEY or MODEL_NAME")


        self.ai_client = Groq(api_key=api_key)
        self.model_name = model_name

        self.failed_attempts = {} 
        self.total_scanned = 0
        self.incidents_found = 0

    async def process_single_batch(self, log_lines: list):
        """
        Processes logs and generates an 'AI-Enhanced Smart Report'.
        """
        current_alerts = []
        LOG_PATTERN = re.compile(r"(?P<time>\d{4}[-.]\d{2}[-.]\d{2} \d{2}:\d{2}:\d{2}) - (?P<ip>\d{1,3}(?:\.\d{1,3}){3}) - ERROR - (?P<reason>.*)")

        for line in log_lines:
            self.total_scanned +=1
            match = LOG_PATTERN.search(line)

            if match:
                ip_match = match.group("ip")
                timestamp_str = match.group("time").replace(".", "-")
                reason = match.group("reason").strip()
                current_log_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

                if ip_match not in self.failed_attempts:
                    self.failed_attempts[ip_match] = []

                self.failed_attempts[ip_match].append((current_log_time, reason))


                if len(self.failed_attempts[ip_match]) >= 5:
                    first_attempt_time = self.failed_attempts[ip_match][0][0]
                    time_diff = (current_log_time - first_attempt_time).total_seconds()


                    if time_diff < 60:
                        error_detail = f"Brute Force attempt detected from IP: {ip_match}. Multiple failed login attempts in less than 60 seconds."

                        try:
                            ai_response = get_ai_support(error_detail)
                            recommendation = ai_response.get("answer")
                            sources = ai_response.get("sources", [])
                        
                        except Exception as e:
                            logging.error(f"RAG Module Failure: {e}")
                            recommendation = "AI recommendation is currently unavailable. Please follow standard firewall blocking procedures."
                            sources = ["Fallback Logic"]

                        current_alerts.append({
                            "status": "threat_detected",
                            "analysis": f"Brute Force attempt from {ip_match}",
                            "ai_recommendation": recommendation,
                            "sources": sources
                        })

                        self.incidents_found += 1
                        self.failed_attempts[ip_match] = []
                    
                    else:
                        self.failed_attempts[ip_match].pop(0)


        return current_alerts