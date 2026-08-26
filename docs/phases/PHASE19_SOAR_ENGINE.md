# AEGIVANTA — PHASE 19 SOAR 2.0 ENGINE SPECIFICATION

## 1. Controlled Response Workflows
The SOAR 2.0 Engine supports 9 core remediation workflows:
1. `BLOCK_IP`: Pushes firewall drop rules for confirmed malicious C2 / scanning addresses.
2. `BLOCK_DOMAIN`: Injects DNS sinkhole / domain blocks across perimeter gateways.
3. `REVOKE_SESSION`: Terminates active user tokens across corporate identity providers.
4. `REVOKE_API_KEY`: Revokes compromised API keys and machine credentials.
5. `ISOLATE_SENSOR`: Restricts local network communication for sensor endpoints.
6. `CONTAIN_ENDPOINT`: Engages host-level firewall isolation via EDR agent.
7. `SUSPEND_ACCOUNT`: Disables directory account status in IAM.
8. `ROTATE_CREDENTIALS`: Triggers automated secret re-issuance.
9. `ESCALATE_ALERT`: Elevates priority and assigns dedicated SOC case responder.

## 2. Reversible Rollback Operations
All destructive network and identity actions log exact pre-modification state snapshots in `ResponseRollback` to ensure atomic 1-click reversal.
