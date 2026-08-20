# Aegivanta Phase 5 — Enterprise Operations & Runbooks

## 1. Day-2 Operations Runbooks

### MFA Reset Workflow
1. Admin verifies user identity via out-of-band channel.
2. Emergency recovery code is supplied by user to complete single-use login.
3. User re-enrolls via `POST /api/v1/identity/mfa/setup` and activates new authenticator.

### SSO Certificate Rollover
1. Upload new X.509 certificate to Identity Provider configuration via `POST /api/v1/identity/sso/config`.
2. Verify token signature handling before sunsetting old certificate.

### SCIM Provisioning Health Checks
- Verify `scim_provisioning_events` for any `status != 200` error responses.
- Rotate SCIM bearer token annually or immediately upon staff departure.
