# PHASE 36 — FRONTEND MICROSEGMENTATION COMMAND CENTER

## 1. UI Tabs

`MicrosegmentationCenter.tsx` delivers a 6-tab enterprise interface:
1. **ZTNA Overview**: Posture score, gateway nodes, microsegmentation policies, active client sessions, blocked lateral traversals count, and priority isolation directives.
2. **L4/L7 Policies**: Policy ledger displaying source/dest segments, protocol/ports, enforcement actions, min trust scores, and evaluated flow counts.
3. **SDP Gateway Fleet**: Connectors table showing regions, gateway public IPs, overlay CIDRs, active client counts, and tunneled data volume.
4. **Active ZTNA Sessions**: Real-time client session table with user email, device ID, overlay IP, trust score badge, and session revocation button.
5. **Lateral Movement Alerts**: Alert cards detailing unauthorized inter-segment traversal attempts and automated boundary drop actions.
6. **Segment Flow Mesh Graph**: Interactive topology node cards and inter-segment traffic trajectory streams.
