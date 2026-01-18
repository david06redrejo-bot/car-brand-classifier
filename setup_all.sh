#!/bin/bash
# setup_all.sh

echo "--- OMNIVISION SETUP SEQUENCE ---"

# 1. Install Dependencies
echo "[1] Installing requirements..."
pip install -r requirements.txt

# 2. Seed Data
echo "[2] Seeding Data (This may take a while)..."
# We run for all domains.
# Warning: This scrapes web. Ensure internet connection.
python scripts/data_seeder.py --domain all

# 3. Train Models
echo "[3] Training Modules..."
# Train each domain
for domain in cars fashion laliga tech food; do
    echo "Training $domain..."
    python train/train_model.py --domain $domain --clusters 500
done

# 4. Launch
echo "[4] Initializing Server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000
