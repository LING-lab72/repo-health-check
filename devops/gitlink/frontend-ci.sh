#!/usr/bin/env sh
set -eu

cd frontend
npm config set registry "${NPM_CONFIG_REGISTRY:-https://registry.npmmirror.com}"
npm ci --no-audit --progress=false --fetch-timeout=120000
npm run lint
npm test -- --run
npm run build
