from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv
from analyzer_logic import SecurityLogAnalyzer # Import your logic

load_dotenv()

app = FastAPI(title="AI Security Guard")

# Initialize our specialized analyzer
# Using English names for attributes and instances
security_agent = SecurityLogAnalyzer(api_key=os.getenv("GROQ_API_KEY"))

# Define what the incoming data should look like
class LogData(BaseModel):
    lines: List[str]

@app.post("/analyze")
async def analyze_endpoint(data: LogData):
    """
    Receives logs via POST and returns AI security analysis.
    """
    try:
        # Pass the data to our logic class
        results = security_agent.process_single_batch(data.lines)
        return {
            "status": "processed",
            "incidents_detected": len(results),
            "details": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Logic explanation:
# 1. Client sends a JSON with {"lines": ["log line 1", "log line 2"]}
# 2. Pydantic validates this format via 'LogData' class.
# 3. 'analyze_endpoint' calls our security agent.
# 4. Result is returned as a clean JSON.