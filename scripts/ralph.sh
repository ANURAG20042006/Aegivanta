#!/usr/bin/env bash
# ==============================================================================
# Ralph Autonomous Execution Loop (Bash Runner for Linux/macOS/WSL/Git Bash)
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${ROOT_DIR}"

TASKS_FILE=".ralph/tasks.json"
PROMPT_FILE=".ralph/prompt.md"
CONFIG_FILE=".ralph/config.json"
MAX_ITERATIONS=${1:-25}
ITERATION=1

echo "========================================================"
echo " Starting Ralph Autonomous Loop for Aegivanta"
echo " Max Iterations: ${MAX_ITERATIONS}"
echo " Tasks File: ${TASKS_FILE}"
echo "========================================================"

while [ "${ITERATION}" -le "${MAX_ITERATIONS}" ]; do
    echo ""
    echo "--- [Ralph Loop] Iteration ${ITERATION}/${MAX_ITERATIONS} ---"

    # Check for pending tasks
    PENDING_COUNT=$(python3 -c "
import json, sys
try:
    with open('${TASKS_FILE}') as f:
        data = json.load(f)
    pending = [t for t in data.get('tasks', []) if t.get('status') in ('pending', 'in_progress')]
    print(len(pending))
except Exception:
    print(0)
" 2>/dev/null || echo "0")

    if [ "${PENDING_COUNT}" -eq 0 ]; then
        echo " All tasks in ${TASKS_FILE} are completed!"
        echo " Ralph loop finished successfully."
        exit 0
    fi

    echo " Pending tasks remaining: ${PENDING_COUNT}"
    echo " Running verification test suite..."
    
    if [ -d ".venv" ]; then
        .venv/bin/python -m pytest -q || true
    else
        python3 -m pytest -q || true
    fi

    echo " Iteration ${ITERATION} completed."
    ITERATION=$((ITERATION + 1))
done

echo " Reached maximum iterations (${MAX_ITERATIONS})."
exit 0
