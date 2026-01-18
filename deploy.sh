#!/bin/bash
# deploy.sh

echo "Deploy Sequence Initiated..."

# 1. Format Code
echo "Running code formatter..."
black .

# 2. Update dependencies
echo "Updating requirements.txt..."
# Simple freeze (pruning unneeded ones usually better, but this ensures tracking)
# pip freeze > requirements.txt
# For now, we manually updated requirements.txt, so we skip overwriting it to avoid noise.

# 3. Git Operations
timestamp=$(date "+%Y-%m-%d %H:%M:%S")
commit_msg="feat: system upgrade [$timestamp]"

echo "Staging files..."
git add .

echo "Committing: $commit_msg"
git commit -m "$commit_msg"

echo "Pushing to remote..."
git push origin master

echo "Deployment Sequence Complete."
read -p "Press enter to exit"
