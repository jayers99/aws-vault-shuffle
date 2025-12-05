#!/usr/bin/env bash
# Script to run tests with coverage

set -euo pipefail

echo "Running tests with coverage..."
pytest tests/ \
    --cov=aws_vault_shuffle \
    --cov-report=term-missing \
    --cov-report=html \
    -v

echo ""
echo "Coverage report generated in htmlcov/index.html"
