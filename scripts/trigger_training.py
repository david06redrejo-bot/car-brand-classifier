
import sys
import os
sys.path.append(os.getcwd())

from app.services.training import TrainingService

print("Triggering sync training for 'cars'...")
success = TrainingService.run_sync("cars")
if success:
    print("Training started/completed.")
else:
    print("Training failed to start.")
