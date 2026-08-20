# SENTINELAI — PHASE 3.8 INVESTIGATION ENGINE

## Investigation Case Management, Evidence Correlation & Pivoting

### 1. Investigation Case Lifecycle State Machine

```
OPEN ───► TRIAGED ───► INVESTIGATING ───► ESCALATED ───► CONTAINED ───► RESOLVED ───► CLOSED
  │          │              ▲                 ▲              ▲             ▲         │
  └──────────┴──────────────┴─────────────────┴──────────────┴─────────────┴─────────┘
                                 (Re-open / Pivot)
```

### 2. Supported Evidence Types

- `ALERT`: Correlated detection alert record.
- `FLOW_TELEMETRY`: Raw network flow record.
- `IOC_MATCH`: Threat intelligence sighting.
- `BEHAVIORAL_ANOMALY`: Statistical deviation record.
- `PIVOT`: Analyst multi-hop exploration result.
- `LOG`: Immutable system and authentication log.
- `RESPONSE_ACTION`: SOAR containment execution.

### 3. Chronological Evidence Timeline

Every investigation automatically reconstructs an immutable, ordered sequence of forensic occurrences:
1. Telemetry ingest and alert detection.
2. Threat intelligence indicator correlation.
3. Behavioral baseline anomaly deviation.
4. Multi-hop lateral graph traversal.
5. Automated incident declaration.
6. SOAR remediation execution.
7. Analyst forensic hypotheses and case resolution.
