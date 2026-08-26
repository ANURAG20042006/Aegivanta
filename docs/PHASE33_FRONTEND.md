# PHASE 33 — FRONTEND DECEPTION COMMAND CENTER

## 1. UI Tabs

`DeceptionCenter.tsx` delivers a 6-tab enterprise interface:
1. **Deception Overview**: Deception Readiness score, active honeypots, canary tokens, recent true-positive engagements, and priority deployment recommendations.
2. **Honeypot Decoy Fleet**: Decoy cards with IP, VLAN, interaction level, emulation profile, total hits, and modal for deploying new decoys.
3. **Canary Token Generator**: Token ledger with trigger counts, placement description, and modal for generating AWS IAM, DOCX, and DNS canaries with one-click trip simulation.
4. **Adversary Interaction Ledger**: Real-time keystroke and command table with source IP, ASN, target decoy, captured payload, and SOAR containment actions.
5. **Endpoint Lure Distribution**: Grid of managed endpoints showing injected LSASS credentials, canary files, and browser cookies.
6. **MITRE Engage Matrix**: Overview of the 6 engagement goals (Expose, Lure, Redirect, Elicit, Degrade, Disrupt).
