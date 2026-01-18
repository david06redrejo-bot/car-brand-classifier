import pytest
import requests
import os
import json

BASE_URL = "http://localhost:8000"
DOMAINS = ["cars", "fashion", "laliga", "tech", "food"]

def is_server_running():
    try:
        requests.get(BASE_URL)
        return True
    except:
        return False

@pytest.mark.skipif(not is_server_running(), reason="Server not running")
def test_metrics_availability():
    """
    Verifies that all domain metric files exist and are valid JSON.
    """
    for domain in DOMAINS:
        url = f"{BASE_URL}/static/metrics/{domain}_metrics.json"
        print(f"Checking {url}...")
        
        # We allow 404 for domains not yet trained in this environment, 
        # BUT the requirement says "Fail... if any domain metric file is missing".
        # So we expect them to exist. If they don't, we fail.
        # Note: If setup_all.sh hasn't run, these WILL fail.
        # We'll assert status_code 200.
        
        resp = requests.get(url)
        assert resp.status_code == 200, f"Metrics for {domain} missing! (Did you run setup_all.sh?)"
        
        data = resp.json()
        assert "accuracy" in data
        assert "matrix" in data
        assert "classes" in data
        assert data["accuracy"] > 0.5, f"Validation Failed: Accuracy for {domain} is too low ({data['accuracy']})"

if __name__ == "__main__":
    # Manually run if needed
    test_metrics_availability()
