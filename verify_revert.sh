#!/usr/bin/env bash
set -e
if [ -n "$(git status --porcelain)" ]; then
  echo "Working tree not clean. Aborting revert test." >&2
  exit 1
fi
current_branch=$(git rev-parse --abbrev-ref HEAD)
git checkout HEAD~1
pytest --maxfail=1 --disable-warnings -q
git checkout $current_branch
echo "Reversion test passed."
