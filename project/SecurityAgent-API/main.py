from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from analyzer_logic import SecurityLogAnalyzer
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Security Guard")
# Single instance of our analyzer (Global state within the app)
security_agent = SecurityLogAnalyzer()

class LogData(BaseModel):
    lines: List[str]

@app.post("/analyze")
async def analyze_endpoint(data: LogData):
    try:
        # Await the async processing
        results = await security_agent.process_single_batch(data.lines)
        return {
            "status": "success",
            "batch_size": len(data.lines),
            "incidents": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")