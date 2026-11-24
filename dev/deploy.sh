#!/bin/bash
set -e

if [[ "$(git branch --show-current)" != "dev" ]]; then
    echo "Error: Must be on dev branch to deploy."
    exit 1
fi

echo "Generating .env.example..."
just env-example

echo "Linting and formatting code..."
uv run ruff check . --fix
uv run ruff format .
echo "Code cleaned!"

git add .
git commit -m "${1:-Update}"

read -r -p "Ready to push to dev? (y/n): " confirm
if [[ "$confirm" != "y" ]]; then
    echo "Push cancelled."
    exit 0
fi

git push

echo "Successfully pushed to dev branch!"
read -r -p "Ready to deploy to prod? (y/n): " confirm

if [[ "$confirm" != "y" ]]; then
    echo "Deployment cancelled."
    exit 0
fi

git switch main
git pull
git merge dev -m "${1:-Update}"
git push

git switch dev

echo "Production deployment triggered!"