import os
import json
import glob

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METRICS_DIR = os.path.join(BASE_DIR, 'static', 'metrics')
OUTPUT_FILE = os.path.join(BASE_DIR, 'static', 'metrics_data.json')

def aggregate():
    all_metrics = {}
    
    if not os.path.exists(METRICS_DIR):
        print("No metrics directory found.")
        return

    pattern = os.path.join(METRICS_DIR, "*_metrics.json")
    files = glob.glob(pattern)
    
    print(f"Found {len(files)} metrics files.")
    
    for fpath in files:
        fname = os.path.basename(fpath)
        domain = fname.replace("_metrics.json", "")
        
        try:
            with open(fpath, 'r') as f:
                data = json.load(f)
                all_metrics[domain] = data
                print(f"Loaded metrics for {domain}")
        except Exception as e:
            print(f"Error loading {fname}: {e}")

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(all_metrics, f, indent=4)
        
    print(f"Aggregated metrics saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    aggregate()
