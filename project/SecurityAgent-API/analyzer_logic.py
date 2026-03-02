import json, os, re, logging
from groq import Groq
from datetime import datetime

class SecurityLogAnalyzer:
    def __init__(self):
        # Initializing core components
        self.ai_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model_name = "llama-3.1-8b-instant"
        
        # State tracking (In-memory storage for brute force detection)
        self.failed_attempts = {} # Key: IP, Value: List of (timestamp, reason)
        self.total_scanned = 0
        self.incidents_found = 0

    def block_ip_on_firewall(self, ip: str):
        # Mocking a system command or API call to a firewall
        logging.info(f"🛡️ [FIREWALL ACTION] IP {ip} blocked successfully.")
        return f"IP {ip} restricted."

    async def analyze_with_ai(self, ip: str, log_data: str):
        """
        Sends potential threat logs to AI for final decision.
        """
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "block_ip_on_firewall",
                    "description": "Blocks an IP if brute force is detected.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ip": {"type": "string"}
                        },
                        "required": ["ip"]
                    }
                }
            }
        ]
        
        system_prompt = "You are a Security AI. Decide if logs indicate brute force. If yes, call 'block_ip_on_firewall'. Else, reply 'NORMAL'."
        
        try:
            # Groq Python client is typically sync, but we treat it as part of our async flow
            response = self.ai_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"IP: {ip}\nLogs:\n{log_data}"}
                ],
                tools=tools,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            if response_message.tool_calls:
                # We handle the tool call requested by AI
                tool_call = response_message.tool_calls[0]
                args = json.loads(tool_call.function.arguments)
                action_result = self.block_ip_on_firewall(args.get("ip"))
                return f"CRITICAL - {action_result}"
            
            return "NORMAL"
        except Exception as e:
            logging.error(f"AI Core Error: {e}")
            return "ERROR"

    async def process_single_batch(self, log_lines: list):
        """
        Processes a list of log strings and detects anomalies.
        Note: This method is now ASYNC.
        """
        current_alerts = [] # Alerts only for the current batch
        LOG_PATTERN = re.compile(r"(?P<time>\d{4}[-.]\d{2}[-.]\d{2} \d{2}:\d{2}:\d{2}) - (?P<ip>\d{1,3}(?:\.\d{1,3}){3}) - ERROR - (?P<reason>.*)")

        for line in log_lines:
            self.total_scanned += 1
            match = LOG_PATTERN.search(line)

            if match:
                ip_match = match.group("ip")
                timestamp_str = match.group("time").replace(".", "-")
                reason = match.group("reason").strip()
                current_log_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

                if ip_match not in self.failed_attempts:
                    self.failed_attempts[ip_match] = []

                self.failed_attempts[ip_match].append((current_log_time, reason))
                
                # Check for brute force (5 attempts in 60 seconds)
                if len(self.failed_attempts[ip_match]) >= 5:
                    first_of_five = self.failed_attempts[ip_match][0][0]
                    time_diff = (current_log_time - first_of_five).total_seconds()

                    if time_diff < 60:
                        logs_for_ai = "\n".join([item[1] for item in self.failed_attempts[ip_match][-5:]])
                        
                        # We MUST use 'await' here because analyze_with_ai is async
                        ai_decision = await self.analyze_with_ai(ip_match, logs_for_ai)

                        if "CRITICAL" in ai_decision:
                            self.incidents_found += 1
                            current_alerts.append({
                                "ip": ip_match,
                                "ai_analysis": ai_decision,
                                "status": "BLOCKED"
                            })
                        
                        # Reset counter after decision to avoid repetitive AI calls
                        self.failed_attempts[ip_match] = []
                    else:
                        # Slide the window
                        self.failed_attempts[ip_match].pop(0)
                        
        return current_alerts