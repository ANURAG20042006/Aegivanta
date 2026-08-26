# Aegivanta Phase 5 — SCIM 2.0 Identity Lifecycle Management

## 1. RFC 7644 Implementation

Aegivanta exposes standard SCIM endpoints authenticated via Bearer tokens:
- `POST /api/v1/scim/v2/Users`: Automated user creation and tenant membership provisioning.
- `DELETE /api/v1/scim/v2/Users/{id}`: Automated account deactivation / deprovisioning.

## 2. Security & Idempotency
- SCIM bearer tokens are hashed with SHA-256 before database insertion.
- All SCIM lifecycle events are permanently recorded in `scim_provisioning_events`.
