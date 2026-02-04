import json, os, sys, re, logging, requests
from groq import Groq
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
client = Groq(
    api_key = os.environ.get("GROQ_API_KEY")
)
