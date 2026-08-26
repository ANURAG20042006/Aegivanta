# PHASE 28 — PAM OPERATIONS RUNBOOK

## 1. Just-in-Time Elevation Workflow

1. **Submission**: User requests elevation with justification and duration (max 8 hours).
2. **Approval**: Security officer or automated peer review validates request.
3. **Session Activation**: Target role is temporarily assigned with automatic TTL revocation.
4. **Emergency Revocation**: Security admins can immediately terminate active sessions via `/api/v1/iam/pam/revoke/{id}`.
