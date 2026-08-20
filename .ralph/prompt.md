# Ralph Autonomous Execution Loop Prompt

You are operating inside an autonomous **Ralph Loop** iteration for the Aegivanta platform.

## Loop Protocol
1. **Inspect State**:
   - Read `.ralph/tasks.json` to find the highest-priority incomplete task (`"status": "pending"` or `"status": "in_progress"`).
   - Check `.planning/STATE.md` and `.planning/SPEC.md` for context and architectural invariants.
2. **Execute Task**:
   - Focus exclusively on the selected task in this atomic context window.
   - Implement necessary code or configuration changes.
3. **Verify**:
   - Run unit tests: `python -m pytest -q`
   - Run environment verification: `python scripts/verify_environment.py`
4. **Persist State**:
   - Mark the completed task as `"status": "completed"` with timestamp in `.ralph/tasks.json`.
   - Update `.planning/STATE.md`.
5. **Exit Cleanly**:
   - Conclude this iteration so the loop can start fresh for the next task.
