#!/bin/sh
# Install the repository-local security delta review hook.
set -e
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit
echo "Installed .githooks/pre-commit (core.hooksPath=.githooks)."
