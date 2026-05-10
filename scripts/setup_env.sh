#!/usr/bin/env bash
set -euo pipefail

python -m venv .venv
source .venv/bin/activate

PIP_INDEX_URL_DEFAULT="https://pypi.org/simple"
PIP_INDEX_URL_VALUE="${PIP_INDEX_URL:-$PIP_INDEX_URL_DEFAULT}"

echo "Using pip index: ${PIP_INDEX_URL_VALUE}"
python -m pip install --upgrade pip
PIP_INDEX_URL="${PIP_INDEX_URL_VALUE}" pip install -r requirements.txt

echo "Environment ready. Activate with: source .venv/bin/activate"
