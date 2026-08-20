# AEGIVANTA — SOC ADMINISTRATOR MANUAL

**Platform**: Aegivanta — Autonomous Cyber Defense & Security Operations Platform  
**Target Audience**: Security Directors, SOC Managers, Platform Administrators  
**Document Version**: 3.0.0  

---

## 1. User & Access Administration

### User Role Hierarchy
- **Admin**: Full administrative authority over users, system preferences, SOAR policy rules, and ML model retraining.
- **Analyst**: Access to threat hunting, investigation cases, live alert triage, and containment execution.
- **Viewer**: Read-only access to operational dashboards and metric reports.

### Provisioning New SOC Operators
1. Navigate to **Team members** (`/users`).
2. Click **Add a team member**.
3. Provide Full Name, Username, Email, and assign appropriate RBAC role.
4. Set account state to **Active**.

---

## 2. Machine Learning Governance & Model Retraining

### Triggering Model Benchmark Retraining
1. Navigate to **Model insights** (`/analytics`).
2. Click **Refresh ML Models**.
3. The background training worker will train benchmark candidate models (Random Forest, XGBoost, LightGBM, CatBoost) against recent labeled flow datasets.
4. Only candidates outperforming current champion accuracy and FPR will be automatically promoted.

---

## 3. Disaster Recovery & Backup Procedures
- **Database Snapshot**: Automatic hourly snapshots stored in `/var/backups/aegivanta`.
- **Artifact Manifest Verification**: Run `python scripts/final_integrity_audit.py` to ensure zero tampering across model binaries.
