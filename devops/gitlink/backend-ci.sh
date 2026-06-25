#!/usr/bin/env sh
set -eu

python -m pip install --upgrade pip
pip install -r backend/requirements.txt pytest flake8

flake8 backend scripts --config backend/.flake8 --extend-ignore E501
pytest backend/tests -q
python scripts/e2e_test.py
