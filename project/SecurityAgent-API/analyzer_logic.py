import json, os, re, logging
from groq import Groq
from datetime import datetime

class SecurityLogAnalyzer:
    def __init__(self,api_key:str):
        self.api_url = os.getenv("API_URL")
        self.ai_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model_name = "llama-3.1-8b-instant"
        self.failed_attempts = {}
        self.total_scanned = 0
        self.incidents_found = 0

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
        system_prompt = "You are a Security AI. Decide if logs indicate brute force. If yes, call 'block_ip_on_firewall'. Else, reply 'NORMAL'."

        
        try:
          
          response = self.ai_client.chat.completions.create(
              model=self.model_name,
              messages=[
              {"role": "system", "content": system_prompt},
              {"role": "user", "content": f"Analyze these logs for IP {ip}:\n{log_data}"}
          ],
              tools=tools,
              tool_choice="auto",
              temperature=0.1
          )
          
          response_message = response.choices[0].message
          if response_message.tool_calls:
                tool_call = response_message.tool_calls[0]
                args = json.loads(tool_call.function.arguments)
                action_result = self.block_ip_on_firewall(args.get("ip"))
                return f"CRITICAL - {action_result}"
                
          return "NORMAL - No tool call requested by AI."
    
        except Exception as e:
            logging.error(f"AI Analysis Error: {e}")
            return "ERROR"

    async def process_single_batch(self, log_lines: list):
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
                    self.failed_attempts[ip_match]=[]

                self.failed_attempts[ip_match].append((current_log_time, reason))
                
                if len(self.failed_attempts[ip_match]) >=5:
                    first_of_five = self.failed_attempts[ip_match][0][0]
                    time_diff = (current_log_time - first_of_five).total_seconds()

                    if time_diff <60:

                        logs_for_ai = "\n".join([item[1] for item in self.failed_attempts[ip_match][-5:]])

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
                        self.failed_attempts[ip_match].pop(0)

        return current_alerts

        
        