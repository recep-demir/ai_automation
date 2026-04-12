import re
import logging
from datetime import datetime
from config import Config
from retriever import get_ai_support

class SecurityLogAnalyzer:
    def __init__(self):
        self.model_name = Config.MODEL_NAME
        
        self.failed_attempts = {} 
        self.total_scanned = 0
        self.incidents_found = 0

        # Regex pattern to capture Time, IP, and the Error Reason
        self.LOG_PATTERN = re.compile(
            r"(?P<time>\d{4}[-.]\d{2}[-.]\d{2} \d{2}:\d{2}:\d{2}) - "
            r"(?P<ip>\d{1,3}(?:\.\d{1,3}){3}) - ERROR - "
            r"(?P<reason>.*)"
        )

    async def process_single_batch(self, log_lines: list):
        """
        Processes logs and generates an 'AI-Enhanced Smart Report' with precision filtering.
        """
        current_alerts = []
        
        # Define security-related keywords to filter out non-attack errors
        # This is crucial for increasing PRECISION
        auth_keywords = ["password", "login", "auth", "invalid credentials", "unauthorized", "access denied"]

        for line in log_lines:
            self.total_scanned += 1
            match = self.LOG_PATTERN.search(line)

            if match:
                reason = match.group("reason").strip().lower()
                
                # --- STEP 1: PRECISION FILTERING ---
                # Check if the error is actually related to authentication/security
                if not any(keyword in reason for keyword in auth_keywords):
                    # Skip non-security errors (e.g., DB errors, missing files)
                    continue

                ip_match = match.group("ip")
                timestamp_str = match.group("time").replace(".", "-")
                current_log_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

                # --- STEP 2: STATE MANAGEMENT ---
                if ip_match not in self.failed_attempts:
                    self.failed_attempts[ip_match] = []

                self.failed_attempts[ip_match].append((current_log_time, reason))

                # --- STEP 3: BRUTE FORCE DETECTION LOGIC ---
                # Check if there are 5 attempts within 60 seconds
                if len(self.failed_attempts[ip_match]) >= 5:
                    first_attempt_time = self.failed_attempts[ip_match][0][0]
                    time_diff = (current_log_time - first_attempt_time).total_seconds()

                    if time_diff < 60:
                        logging.warning(f"🚨 [ALERT] Brute force detected from IP: {ip_match}")
                        
                        query_for_rag = f"Brute force attempt detected from {ip_match}. Reason: {reason}"

                        try:
                            # AI-Augmented Analysis via RAG
                            ai_data = await get_ai_support(query_for_rag)
                            recommendation = ai_data.get("answer")
                            sources = ai_data.get("sources", [])
                        except Exception as e:
                            logging.error(f"AI Support Error: {e}")
                            recommendation = "Manual intervention required. AI recommendation unavailable."
                            sources = []

                        current_alerts.append({
                            "ip": ip_match,
                            "status": "CRITICAL",
                            "analysis": "Brute force attack signature matched based on security keywords.",
                            "ai_recommendation": recommendation,
                            "policy_sources": sources
                        })

                        self.incidents_found += 1
                        self.failed_attempts[ip_match] = [] # Reset for this IP after detection
                    
                    else:
                        # Slide the window: remove the oldest attempt if time difference is more than 60s
                        self.failed_attempts[ip_match].pop(0)

        return current_alerts