"""
scripts/generate_report.py

Responsibility:
    - Analyzes training results.
    - Generates a Markdown report `metrics/REPORT_Car_Brand_Logos.md`.
    - Identifies top confused class pairs.
"""

import json
import os
import sys
import numpy as np

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import BASE_DIR

def generate_report(domain_name="Car_Brand_Logos"):
    print(f"Generating report for {domain_name}...")
    
    # Paths
    static_dir = os.path.join(BASE_DIR, 'static')
    config_dir = os.path.join(BASE_DIR, 'config')
    metrics_dir = os.path.join(BASE_DIR, 'metrics')
    os.makedirs(metrics_dir, exist_ok=True)
    
    cm_path = os.path.join(static_dir, 'confusion_matrix.json')
    params_path = os.path.join(config_dir, 'hyperparams.json')
    
    # Load Data
    if not os.path.exists(cm_path):
        print(f"Error: {cm_path} not found.")
        return
        
    with open(cm_path, 'r') as f:
        cm_data = json.load(f)
        
    hyperparams = {}
    if os.path.exists(params_path):
        with open(params_path, 'r') as f:
            hyperparams = json.load(f)

    classes = cm_data['classes']
    matrix = np.array(cm_data['matrix'])
    accuracy = cm_data['accuracy']
    
    # Calculate Top 3 Confused Pairs
    confusions = []
    num_classes = len(classes)
    for i in range(num_classes):
        for j in range(num_classes):
            if i != j:
                count = matrix[i][j]
                if count > 0:
                    confusions.append((classes[i], classes[j], count))
                    
    # Sort by count descending
    confusions.sort(key=lambda x: x[2], reverse=True)
    top_3_confused = confusions[:3]
    
    # Generate Markdown
    md_content = f"""# Model Training Report: {domain_name}

**Status**: Training Completed
**Accuracy**: {accuracy * 100:.2f}%
**Best Vocabulary Size (k)**: {hyperparams.get('best_k', 'N/A')}

## Hyperparameter Tuning
"""
    if 'all_results' in hyperparams:
        md_content += "| k (Vocab Size) | Accuracy |\n|---|---|\n"
        for k, acc in hyperparams['all_results'].items():
            md_content += f"| {k} | {acc * 100:.2f}% |\n"
    else:
        md_content += "No tuning data available.\n"
        
    md_content += """
## Confusion Matrix Analysis

### Top 3 Most Confused Pairs
The model most frequently confuses:
"""
    if top_3_confused:
        for true_label, pred_label, count in top_3_confused:
            md_content += f"- **{true_label}** predicted as **{pred_label}**: {count} times\n"
    else:
        md_content += "- None (Perfect Classification)\n"
        
    md_content += "\n### Full Confusion Matrix\n"
    # Create an ASCII table for the matrix
    # Header
    md_content += "| Actual \ Predicted | " + " | ".join(classes) + " |\n"
    md_content += "|---|" + "|".join(["---"] * len(classes)) + "|\n"
    
    for i, row in enumerate(matrix):
        row_str = " | ".join(map(str, row))
        md_content += f"| **{classes[i]}** | {row_str} |\n"
        
    # Save Report
    report_path = os.path.join(metrics_dir, f'REPORT_{domain_name}.md')
    with open(report_path, 'w') as f:
        f.write(md_content)
        
    print(f"Report generated: {report_path}")

if __name__ == "__main__":
    generate_report()
