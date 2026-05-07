#!/usr/bin/env bash
set -euo pipefail

SPACE_NAME="${SPACE_NAME:-nousresearch/ClinSight}"
HF_SPACE_DIR="${HF_SPACE_DIR:-/workspace/hf_space}"

echo "=== ClinSight HF Space Deploy Script ==="
echo "Target space: ${SPACE_NAME}"
echo "Local dir:    ${HF_SPACE_DIR}"
echo ""

if ! command -v git &>/dev/null; then
    echo "Error: git is not installed."
    exit 1
fi

if ! command -v huggingface-cli &>/dev/null; then
    echo "huggingface-cli not found. Install with:"
    echo "  pip install huggingface_hub"
    exit 1
fi

if ! huggingface-cli whoami &>/dev/null; then
    echo "You are not logged in to Hugging Face. Run:"
    echo "  huggingface-cli login"
    exit 1
fi

cd "${HF_SPACE_DIR}"

if [ ! -d .git ]; then
    echo "Initializing git repo..."
    git init
fi

if ! git remote get-url origin &>/dev/null 2>&1; then
    echo "Adding HF Space remote..."
    git remote add origin "https://huggingface.co/spaces/${SPACE_NAME}"
fi

echo "Staging files..."
git add app.py requirements.txt README.md deploy.sh 2>/dev/null || true
git add -A

echo "Committing..."
git commit -m "deploy: ClinSight app with demo cases, JSON viewer, AMD perf charts" || true

echo "Pushing to Hugging Face Space..."
git push -u origin main:main --force

echo ""
echo "Done. Visit: https://huggingface.co/spaces/${SPACE_NAME}"
