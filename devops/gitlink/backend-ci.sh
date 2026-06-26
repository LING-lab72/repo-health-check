#!/usr/bin/env sh
set -eu

export SESSION_SECRET="${SESSION_SECRET:-gitlink-ci-session-secret}"
export PIP_DEFAULT_TIMEOUT="${PIP_DEFAULT_TIMEOUT:-120}"
export PIP_RETRIES="${PIP_RETRIES:-3}"

install_deps() {
  index_url="$1"
  trusted_host="${2:-}"

  if [ -n "$trusted_host" ]; then
    python -m pip install --disable-pip-version-check --no-cache-dir \
      -i "$index_url" --trusted-host "$trusted_host" \
      -r backend/requirements.txt pytest flake8
  else
    python -m pip install --disable-pip-version-check --no-cache-dir \
      -i "$index_url" \
      -r backend/requirements.txt pytest flake8
  fi
}

echo "Installing Python dependencies..."
install_deps "${PIP_INDEX_URL:-https://mirrors.aliyun.com/pypi/simple/}" "mirrors.aliyun.com" \
  || install_deps "https://pypi.org/simple" ""

flake8 backend scripts --config backend/.flake8 --extend-ignore E501
pytest backend/tests -q
python scripts/e2e_test.py
