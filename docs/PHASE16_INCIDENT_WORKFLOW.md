# Aegivanta — Phase 16: SOC Incident Workflow & Immutable Timeline

## 1. SOC Incident State Machine
The incident lifecycle enforces audited state transitions across 9 standardized states:
1. `NEW`
2. `TRIAGED`
3. `INVESTIGATING`
4. `CONTAINMENT_PENDING`
5. `CONTAINED`
6. `REMEDIATING`
7. `RESOLVED`
8. `FALSE_POSITIVE`
9. `CLOSED`

## 2. Immutable Timeline Ledger
- Every state change, analyst note, assignment, and SOAR action generates an immutable `IncidentTimelineEvent`.
- Timelines provide chronological visibility from flow `first_seen` to closure.

## 3. Endpoints
- `GET /api/v1/incidents/{id}/timeline`
- `POST /api/v1/incidents/{id}/transition`
- `POST /api/v1/incidents/{id}/assign`
