#!/usr/bin/env sh
set -eu

mkdir -p release
tar -czf release/repo-health-frontend-dist.tar.gz -C frontend dist
tar -czf release/repo-health-backend-source.tar.gz backend scripts sdd docker-compose.yml .env.example

echo "Release artifacts:"
ls -lh release
