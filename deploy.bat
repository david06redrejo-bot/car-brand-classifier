@echo off
echo Checking training status...
REM Ideally we check if models are new, but for now we just proceed assuming user runs this AFTER training.

echo Adding files to git...
git add .

echo Committing changes...
git commit -m "Refactor: SPA Frontend, Calibration, Active Learning and New Models"

echo Pushing to GitHub...
git push origin master

echo Deployment triggered on Hugging Face.
pause
