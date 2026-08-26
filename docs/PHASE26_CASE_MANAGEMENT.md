# Aegivanta — Enterprise SOC Case Management (Phase 26.6)

## Case Lifecycle & State Machine

```
   +-----------------------------------------------------------------------+
   |                                                                       |
   v                                                                       |
[ OPEN ] ---> [ TRIAGED ] ---> [ INVESTIGATING ] ---> [ CONTAINMENT ]     |
                                       |                      |            |
                                       v                      v            |
                                [ ESCALATED ]        [ REMEDIATION ]       |
                                       |                      |            |
                                       v                      v            |
                                [ MONITORING ] ------> [ RESOLVED ]        |
                                       |                      |            |
                                       +-----------------> [ CLOSED ] -----+
                                                              |
                                                              +--> [ REOPENED ]
```

## Immutable Audit Governance
Every case creation, status transition, task assignment, comment addition, and evidence link automatically creates a tamper-evident audit record in `soc_case_audits`.
