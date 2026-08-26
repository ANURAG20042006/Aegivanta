# AEGIVANTA — PHASE 21 CLOUD INFRASTRUCTURE ENTITLEMENT MANAGEMENT (CIEM)

## 1. Entitlement Risk Vectors
- **Wildcard Admin Permissions**: Flags policies granting unrestricted `*` actions across S3, IAM, and EC2.
- **Stale Accounts**: Detects dormant credentials and access keys unused for over 90 days.
- **Privilege Escalation Paths**: Identifies IAM permission combinations allowing lateral privilege elevation (`iam:PassRole` + `lambda:CreateFunction`, `sts:AssumeRole` on cross-account production roles).
