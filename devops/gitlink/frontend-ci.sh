#!/usr/bin/env sh
set -eu

cd frontend
npm ci
npm run lint
npm test -- --run
npm run build
