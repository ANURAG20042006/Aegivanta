# Phase 46 Turnkey Templates — Security Automation Studio

## Overview

Phase 46 ships with 3 Aegivanta-verified **Turnkey Enterprise SOAR Templates** that teams can immediately clone, customize, and activate.

---

## Template 1: AWS GuardDuty Crypto-Mining Quarantine

**Category**: `CLOUD_SECURITY`
**Steps**: 4

**Use Case**: Detects EC2 instances communicating with known crypto-mining pools (identified by AWS GuardDuty findings) and automatically quarantines them.

**Flow**:
1. `TRIGGER` — On GuardDuty finding `CryptoCurrency:EC2/BitcoinTool.B!DNS`
2. `ACTION` — Revoke EC2 IAM instance profile
3. `ACTION` — Attach restrictive Security Group (deny all outbound)
4. `NOTIFICATION` — Slack + Jira ticket with GuardDuty evidence

---

## Template 2: Dark Web Leaked Credential Reset

**Category**: `IDENTITY_PROTECTION`
**Steps**: 3

**Use Case**: Matches employee email addresses found in dark web breach feeds and forces just-in-time (JIT) password reset with WebAuthn MFA step-up.

**Flow**:
1. `TRIGGER` — Dark web feed match on `@company.com` domain
2. `HUMAN_GATE` — HR + Security approval for PII handling
3. `ACTION` — Force password reset + WebAuthn re-enrollment via Okta

---

## Template 3: ZTNA Lateral Movement Kill Switch

**Category**: `ZERO_TRUST`
**Steps**: 5

**Use Case**: Detects abnormal lateral SMB/RDP scanning behavior and injects eBPF microsegmentation rules to block lateral movement.

**Flow**:
1. `TRIGGER` — Anomaly: host scanning > 10 SMB targets in 60s
2. `CONDITION` — `IS_PRODUCTION_SEGMENT == true`
3. `HUMAN_GATE` — SOC L2 approval (5 min timeout)
4. `ACTION` — eBPF microsegment block on SMB port 445 from source host
5. `NOTIFICATION` — PagerDuty + Slack with lateral movement graph

---

## Cloning a Template

Via API:
```bash
POST /api/v1/automation-studio/playbooks
{
  "name": "ZTNA Lateral Movement Kill Switch",
  "description": "Customized for Prod-DC-01 segment.",
  "trigger_type": "ON_ALERT"
}
```

Via UI: Click **"Clone & Use"** on any template card in the Template Library tab.
