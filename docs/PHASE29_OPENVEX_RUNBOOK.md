# PHASE 29 — OPENVEX OPERATIONAL RUNBOOK

## 1. VEX Publishing Workflow

1. **Detection**: Dependency scanner identifies a CVE in a third-party package.
2. **Analysis**: Static analysis verifies if the vulnerable method or file is reached during execution.
3. **Publication**: If unreachable, author an OpenVEX statement with status `NOT_AFFECTED` and detailed justification.
4. **Gate Bypass**: CI/CD gatekeeper ingests VEX and suppresses the blocking condition automatically.
