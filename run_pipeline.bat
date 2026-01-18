@echo off
echo ===========================================
echo OmniVision MLOps Pipeline
echo ===========================================

echo [1/5] Running Data Refinery...
python scripts/refinery.py --dataset_path "data/raw/train/Car_Brand_Logos/Train"

echo [2/5] Running Hyperparameter Auto-Tuner...
python scripts/tune_hyperparams.py

echo [3/5] Benchmarking Performance...
python scripts/benchmark.py

echo [4/5] Generating Visual Explainability...
python -c "from core.visualizer import generate_visual_word_montage; generate_visual_word_montage(['data/raw/train/Car_Brand_Logos/Train'])"

echo [5/5] Generating Training Report...
python scripts/generate_report.py

echo ===========================================
echo Pipeline Completed!
echo Check metrics/ and static/ folders for results.
echo ===========================================
pause
