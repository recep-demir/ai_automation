from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import logging
from analyzer_logic import SecurityLogAnalyzer
from config import Config


logging.basicConfig(
    level=Config.LOG_LEVEL,
    format='%(asctime)s - %(levelname)s - [API] - %(message)s'
)

app = FastAPI(
    title="AI-Powered Security Guard",
    description="Automated log analysis with RAG-based AI recommendations.",
    version="1.0.0"
)
security_agent = SecurityLogAnalyzer()

class LogRequest(BaseModel):
    logs: List[str]

    
@app.get("/")
async def root():
    return {"message": "AI Security Guard is Online", "status": "Ready"}

@app.post("/analyze")
async def analyze_logs(data: LogRequest):
    """
    Endpoint to receive logs and return security analysis.
    """
    if not data.logs:
        raise HTTPException(status_code=400, detail="Log list cannot be empty.")

    logging.info(f"Received batch of {len(data.logs)} logs for analysis.")

    try:
        analysis_results = await security_agent.process_single_batch(data.logs)
        
        return {
            "status": "success",
            "summary": {
                "total_scanned": len(data.logs),
                "incidents_found": len(analysis_results)
            },
            "alerts": analysis_results
        }

    except Exception as e:
        logging.error(f"Unexpected error during analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error during log processing.")
