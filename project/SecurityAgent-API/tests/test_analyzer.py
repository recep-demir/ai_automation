import pytest
from datetime import datetime, timedelta
from analyzer_logic import SecurityLogAnalyzer 

def test_threat_detection():
    analyzer = SecurityLogAnalyzer()
    
    now = datetime.now()
    log_time = now - timedelta(seconds=30)
    fake_log = "CRITICAL: SQL injection attempt DROP TABLE users;"
    
    # Kendi class'ındaki fonksiyon ismin neyse onu çağır (örn: process_logs veya analyze)
    result = analyzer.process_single_batch(fake_log, log_time, now) 
    
    assert result == True