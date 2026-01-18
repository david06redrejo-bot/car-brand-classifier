import json
import os
import random

DOMAINS = ["cars", "fashion", "laliga", "tech", "food"]
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METRICS_DIR = os.path.join(BASE_DIR, "static", "metrics")

os.makedirs(METRICS_DIR, exist_ok=True)

def generate_dummy_metrics():
    for domain in DOMAINS:
        path = os.path.join(METRICS_DIR, f"{domain}_metrics.json")
        if not os.path.exists(path):
            print(f"Generating dummy metrics for {domain}...")
            data = {
                "accuracy": 0.85,
                "classes": ["Class A", "Class B", "Class C"],
                "matrix": [
                    [10, 2, 0],
                    [1, 12, 1],
                    [0, 3, 9]
                ]
            }
            with open(path, "w") as f:
                json.dump(data, f)
    print("Dummy metrics generated.")

if __name__ == "__main__":
    generate_dummy_metrics()
