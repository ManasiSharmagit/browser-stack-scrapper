#!/usr/bin/env bash
set -euo pipefail

if [ -d ".venv" ]; then
  source ".venv/bin/activate"
fi

pip install -r requirements.txt

python -m src.runners.browserstack_runner

