#!/usr/bin/env sh
set -eu

export SESSION_SECRET="${SESSION_SECRET:-gitlink-ci-session-secret}"
export PIP_INDEX_URL="${PIP_INDEX_URL:-https://pypi.tuna.tsinghua.edu.cn/simple}"
export PIP_DEFAULT_TIMEOUT="${PIP_DEFAULT_TIMEOUT:-120}"
export PIP_RETRIES="${PIP_RETRIES:-3}"

python -m pip install --disable-pip-version-check --no-cache-dir -i "$PIP_INDEX_URL" \
  -r backend/requirements.txt pytest flake8

flake8 backend scripts --config backend/.flake8 --extend-ignore E501
pytest backend/tests -q
python scripts/e2e_test.py
