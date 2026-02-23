import json, os, re, logging
from groq import Groq
from datetime import datetime

class SecurityLogAnalyzer:
    def __init__(self,api_key:str):
        self.api_url = os.getenv("API_URL")
        self.ai_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model_name = "llama-3.1-8b-instant"
        self.failed_attempts = {}
        self.alerts = []

    def block_ip_on_firewall(self, ip: str):
        logging.info(f"🛡️ [FIREWALL ACTION] IP {ip} blocked.")
        return f"IP {ip} restricted."
    
    async def analyze_with_ai(self, ip: str, log_data: str):
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "block_ip_on_firewall", 
                    "description": "Blocks an IP address if brute force activity is detected.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ip": {"type": "string", "description": "The IP to block"}
                        },
                        "required": ["ip"]
                    }
                }
            }
        ]
        
        try:
          system_prompt = "You are a strict Security Automated System. Your ONLY task is to decide if the logs indicate a brute force attack. If you detect a brute force attack, you MUST call the 'block_ip_on_firewall' function with the offending IP. Do NOT provide any explanations or say you cannot access data. If the logs do not indicate a brute force attack, simply respond with 'NORMAL'."

          user_prompt = f"Analyze these logs for IP {ip}:\n{log_data}"

          messages = [
              {"role": "system", "content": system_prompt},
              {"role": "user", "content": user_prompt}
          ]

          response = self.ai_client.chat.completions.create(
              model=self.model_name,
              messages=messages,
              tools=tools,
              tool_choice="auto",
              temperature=0.1
          )
          
          response_message = response.choices[0].message
          tool_calls = response_message.tool_calls

          if tool_calls:
              for tool_call in tool_calls:
                
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                if function_name == "block_ip_on_firewall":
                    result = self.block_ip_on_firewall(ip=function_args.get("ip"))
                    return f"CRITICAL - AI ACTION: {result}"
                
          return "NORMAL - No tool call requested by AI."
    
        except Exception as e:
            logging.error(f"AI Analysis Error: {e}")
            return "ERROR"

        pass

    def process_single_batch(self, log_lines: list):
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
                            self.failed_attempts[ip_match]=[]

                        self.failed_attempts[ip_match].append((current_log_time, reason))
                        
                        if len(self.failed_attempts[ip_match]) >=5:
                            first_of_five = self.failed_attempts[ip_match][0][0]
                            time_diff = (current_log_time - first_of_five).total_seconds()

                            if time_diff <60:

                                logs_for_ai = "\n".join([item[1] for item in self.failed_attempts[ip_match][-5:]])

                                ai_decision = self.analyze_with_ai(ip_match, logs_for_ai)

                                if "CRITICAL" in ai_decision:
                                    logging.info(f"AI DETECTED CRITICAL THREAT for IP: {ip_match}")

                                    self.alerts.append({
                                        "ip": ip_match,
                                        "first_error": str(first_of_five),
                                        "last_error": str(current_log_time),
                                        "total_attempts": len(self.failed_attempts[ip_match]), 
                                        "reason": reason,
                                        "ai_analysis": ai_decision,
                                        "status": "CRITICAL"
                                    })

                                    self.incidents_found +=1

                                    if self.api_url:
                                        self.report_ip_to_security(ip_match, self.api_url, timestamp_str, reason,ai_decision)
                                    
                                else:
                                    logging.info(f"AI marked activity as NORMAL for IP: {ip_match}. No action taken.")

                                self.failed_attempts[ip_match] = []
                            else:
                                self.failed_attempts[ip_match].pop(0)

                        pass
        return self.alerts

        
        