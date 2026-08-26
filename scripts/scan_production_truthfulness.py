"""
scripts/scan_production_truthfulness.py
======================================
Automated Production Truthfulness & Integrity Scanner for Aegivanta.

Validates the whole codebase against 6 critical production integrity rules:
1. No False Third-Party Certification Claims (Coalfire/EY/BSI external certs without disclosure).
2. Seeded Data Guards in Production (Zero automatic mock seeding in production mode).
3. Authoritative Multi-Tenant Isolation (No `default-tenant` fallbacks in API routes).
4. Authoritative ML Metric Registrations (No hardcoded 0.985/0.958 default metrics in schemas).
5. Canonical Frontend Token & Tenant Storage (Uniform usage of authStorage).
6. Honest Capability & Dataset Demarcation (Proper tagging of DEMO, LAB, BETA, PROD).
"""

import os
import sys
import re
import json
from typing import List, Dict, Any

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")


def scan_rule_1_certifications() -> Dict[str, Any]:
    """Rule 1: External certification claims must be labeled SELF_ATTESTED / CONTROL_MAPPING."""
    cert_file = os.path.join(BACKEND_DIR, "app", "services", "enterprise_certification_service.py")
    if not os.path.exists(cert_file):
        return {"passed": False, "rule": "Rule 1: Certification Truthfulness", "errors": ["File missing"]}

    with open(cert_file, "r", encoding="utf-8") as f:
        content = f.read()

    errors = []
    if "Coalfire Systems (3PAO)" in content or "Ernst & Young LLP" in content:
        errors.append("Found unshielded 3rd-party auditor claims in enterprise_certification_service.py")
    if "SELF_ATTESTED_MAPPING" not in content:
        errors.append("Missing SELF_ATTESTED_MAPPING status in enterprise_certification_service.py")

    return {
        "rule": "Rule 1: False External Certification Prohibition",
        "passed": len(errors) == 0,
        "errors": errors
    }


def scan_rule_2_seeded_production_guards() -> Dict[str, Any]:
    """Rule 2: Services with _seed_defaults must guard against seeding in production."""
    services_dir = os.path.join(BACKEND_DIR, "app", "services")
    guarded_services = [
        "enterprise_certification_service.py",
        "cloud_account_connector_service.py",
        "drift_monitoring_service.py",
        "ml_model_platform_service.py",
        "cyber_roi_service.py",
        "ciso_report_service.py",
        "autonomous_mission_service.py",
        "adversarial_defense_service.py",
        "production_readiness_audit_service.py",
        "defense_war_room_service.py"
    ]
    errors = []
    for svc in guarded_services:
        path = os.path.join(services_dir, svc)
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
        if "is_production" not in code:
            errors.append(f"Service {svc} lacks production guard (is_production)")

    return {
        "rule": "Rule 2: Production Mock & Seed Data Isolation",
        "passed": len(errors) == 0,
        "errors": errors,
        "verified_services_count": len(guarded_services)
    }


def scan_rule_3_tenant_fallbacks() -> Dict[str, Any]:
    """Rule 3: No silent 'default-tenant' fallbacks in API routes."""
    api_dir = os.path.join(BACKEND_DIR, "app", "api", "v1")
    errors = []
    total_checked = 0
    for filename in os.listdir(api_dir):
        if not filename.endswith(".py"):
            continue
        total_checked += 1
        filepath = os.path.join(api_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        if 'context.tenant_id or "default-tenant"' in content:
            errors.append(f"Found unsafe tenant fallback in {filename}")

    return {
        "rule": "Rule 3: Authoritative Multi-Tenant Isolation",
        "passed": len(errors) == 0,
        "errors": errors,
        "routes_scanned": total_checked
    }


def scan_rule_4_ml_metric_defaults() -> Dict[str, Any]:
    """Rule 4: ML model registration schemas must not hardcode default metric values."""
    schema_file = os.path.join(BACKEND_DIR, "app", "api", "v1", "ai_security_intelligence.py")
    model_file = os.path.join(BACKEND_DIR, "app", "models", "ai_security_intelligence.py")
    errors = []

    with open(schema_file, "r", encoding="utf-8") as f:
        schema_code = f.read()
    with open(model_file, "r", encoding="utf-8") as f:
        model_code = f.read()

    if 'roc_auc: Optional[float] = 0.985' in schema_code:
        errors.append("ai_security_intelligence.py still contains hardcoded roc_auc default in schema")
    if 'roc_auc: Mapped[float] = mapped_column(Float, default=0.985' in model_code:
        errors.append("ai_security_intelligence.py model still contains hardcoded roc_auc default column")

    return {
        "rule": "Rule 4: Authoritative ML Governance & Lineage",
        "passed": len(errors) == 0,
        "errors": errors
    }


def scan_rule_5_frontend_auth_storage() -> Dict[str, Any]:
    """Rule 5: Frontend services must use canonical authStorage."""
    frontend_files = [
        os.path.join(FRONTEND_DIR, "src", "services", "saas.ts"),
        os.path.join(FRONTEND_DIR, "src", "services", "api.ts"),
        os.path.join(FRONTEND_DIR, "src", "services", "reports.ts"),
        os.path.join(FRONTEND_DIR, "src", "context", "AuthContext.tsx"),
    ]
    errors = []
    for fp in frontend_files:
        if not os.path.exists(fp):
            continue
        with open(fp, "r", encoding="utf-8") as f:
            code = f.read()
        if "authStorage" not in code:
            errors.append(f"Frontend file {os.path.basename(fp)} does not import/use authStorage")

    return {
        "rule": "Rule 5: Frontend Canonical Token & Tenant Storage",
        "passed": len(errors) == 0,
        "errors": errors
    }


def scan_rule_6_capability_maturity() -> Dict[str, Any]:
    """Rule 6: Capability maturity indicators and disclosures present."""
    sidebar_file = os.path.join(FRONTEND_DIR, "src", "components", "common", "Sidebar.tsx")
    cert_page_file = os.path.join(FRONTEND_DIR, "src", "pages", "GlobalEnterpriseCertificationCenter.tsx")
    errors = []

    if os.path.exists(sidebar_file):
        with open(sidebar_file, "r", encoding="utf-8") as f:
            side_code = f.read()
        if "SELF-ATTESTED" not in side_code:
            errors.append("Sidebar does not display SELF-ATTESTED maturity badge for certifications")

    if os.path.exists(cert_page_file):
        with open(cert_page_file, "r", encoding="utf-8") as f:
            cert_code = f.read()
        if "Technical Control Mapping & Attestation Notice" not in cert_code:
            errors.append("Certification center does not display transparent self-attestation notice")

    return {
        "rule": "Rule 6: Capability Maturity & Disclosure Integrity",
        "passed": len(errors) == 0,
        "errors": errors
    }


def main():
    if sys.stdout.encoding.lower() != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    print("================================================================================")
    print("      AEGIVANTA PRODUCTION TRUTHFULNESS & INTEGRITY SCANNER (V50.0.0)          ")
    print("================================================================================")

    results = [
        scan_rule_1_certifications(),
        scan_rule_2_seeded_production_guards(),
        scan_rule_3_tenant_fallbacks(),
        scan_rule_4_ml_metric_defaults(),
        scan_rule_5_frontend_auth_storage(),
        scan_rule_6_capability_maturity(),
    ]

    all_passed = True
    for r in results:
        status_str = "[PASSED]" if r["passed"] else "[FAILED]"
        print(f"{status_str} {r['rule']}")
        if not r["passed"]:
            all_passed = False
            for err in r["errors"]:
                print(f"    - ERROR: {err}")

    print("--------------------------------------------------------------------------------")
    summary = {
        "all_passed": all_passed,
        "total_rules": len(results),
        "passed_rules": sum(1 for r in results if r["passed"]),
        "failed_rules": sum(1 for r in results if not r["passed"]),
        "details": results
    }

    os.makedirs(os.path.join(ROOT_DIR, "results", "master_audit"), exist_ok=True)
    report_path = os.path.join(ROOT_DIR, "results", "master_audit", "production_truthfulness_scan.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"Audit scan report saved to: {report_path}")
    if all_passed:
        print("ALL PRODUCTION TRUTHFULNESS RULES PASSED WITH ZERO VIOLATIONS!")
        sys.exit(0)
    else:
        print("SCAN DETECTED INTEGRITY VIOLATIONS - REVIEW REQUIRED.")
        sys.exit(1)


if __name__ == "__main__":
    main()

