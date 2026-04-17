import pytest
from analyzer_logic import SecurityLogAnalyzer

@pytest.mark.anyio
async def test_threat_detection():
    analyzer = SecurityLogAnalyzer()
    
    fake_log_list = ["CRITICAL: SQL injection attempt DROP TABLE users;"]
    
    result = await analyzer.process_single_batch(fake_log_list)

    assert result is not None
    print(f"\nTest Sonucu: {result}")