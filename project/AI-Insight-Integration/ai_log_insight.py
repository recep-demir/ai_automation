import json, os, sys, re, logging, requests
from groq import Groq
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

LOG_DIR = os.path.join(os.getcwd(),"project","AI-Insight-Integration")
APP_LOG_FILE = os.path.join(LOG_DIR,"app.log")
JSON_ALERT_FILE = os.path.join(LOG_DIR,"security_alert.json")

os.makedirs(LOG_DIR,exist_ok=True)




class SecurityLogAnalyer:
    def __init__(self,log_file)
        