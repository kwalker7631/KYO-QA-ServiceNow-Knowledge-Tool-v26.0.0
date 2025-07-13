#!/bin/bash
set -e

# Ensure repository is clean
if [[ -n $(git status --porcelain) ]]; then
    echo "Repository has uncommitted changes. Commit or stash them before running." >&2
    exit 1
fi

# Create timestamped branch
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BRANCH="codex-fixes-$TIMESTAMP"

echo "Creating branch $BRANCH"

git checkout -b "$BRANCH"

PATCH_FILE=${1:-patch.diff}

if [[ ! -f "$PATCH_FILE" ]]; then
    echo "Patch file $PATCH_FILE not found." >&2
    git checkout main
    git branch -D "$BRANCH"
    exit 1
fi

# Apply patch
if ! git apply "$PATCH_FILE"; then
    echo "Failed to apply patch." >&2
    git checkout main
    git branch -D "$BRANCH"
    exit 1
fi

# Run basic lint on new/changed Python files
PY_FILES=$(git diff --name-only --diff-filter=AM | grep -E '\.py$' || true)
if [[ -n "$PY_FILES" ]]; then
    if ! python -m py_compile $PY_FILES; then
        echo "Linting failed." >&2
        git reset --hard origin/main
        git checkout main
        git branch -D "$BRANCH"
        exit 1
    fi
fi

# Run smoke tests
if ! python -m pytest --maxfail=1 --disable-warnings -q; then
    echo "Tests failed. Reverting." >&2
    git reset --hard origin/main
    git checkout main
    git branch -D "$BRANCH"
    exit 1
fi

# Commit and push

git add -A
COMMIT_MSG="Apply automated patches"

git commit -m "$COMMIT_MSG"

git push -u origin "$BRANCH"

echo "Patch applied and branch pushed: $BRANCH"
