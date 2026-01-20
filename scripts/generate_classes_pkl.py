import pickle
from pathlib import Path

# Define the classes list
classes = [
    'hyundai',
    'lexus',
    'mazda',
    'mercedes',
    'opel',
    'skoda',
    'toyota',
    'volkswagen',
    'background'
]

# Save to models/cars/classes.pkl
output_path = Path("models/cars/classes.pkl")
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, 'wb') as f:
    pickle.dump(classes, f)

print(f"[SUCCESS] Created {output_path} with {len(classes)} classes")
