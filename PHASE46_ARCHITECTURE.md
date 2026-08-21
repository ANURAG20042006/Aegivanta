# Phase 46 Architecture — Security Automation Studio

## System Design

Phase 46 implements a full **SOAR 2.0 Visual Automation Studio** built on a 3-layer architecture:

```
┌──────────────────────────────────────────────────────────┐
│              Frontend: SecurityAutomationStudioCenter     │
│    Tabs: Overview / DAG Canvas / Playbooks / Executions  │
│              Template Library / Simulation Studio         │
└──────────────────────┬───────────────────────────────────┘
                       │ REST API
┌──────────────────────▼───────────────────────────────────┐
│         FastAPI Router: /api/v1/automation-studio/*       │
│  GET /summary  POST /playbooks  POST /simulate  GET /...  │
└──────────────────────┬───────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────┐
│              Service Layer (3 Services)                    │
│  PlaybookBuilderService   PlaybookEngineService           │
│  AutomationStudioPostureService                           │
└──────────────────────┬───────────────────────────────────┘
                       │ SQLAlchemy Async ORM
┌──────────────────────▼───────────────────────────────────┐
│      SQLite / PostgreSQL (AsyncSession)                   │
│   automation_playbooks  |  playbook_execution_runs        │
│   playbook_templates                                      │
└──────────────────────────────────────────────────────────┘
```

## DAG Node Types

| Node Type | Purpose |
|---|---|
| `TRIGGER` | Entry point (Alert, Schedule, Webhook) |
| `CONDITION` | Boolean gate (`SEVERITY == CRITICAL`) |
| `HUMAN_GATE` | SOC L2 timed approval step |
| `ACTION` | eBPF isolation, Okta revoke, ticket creation |
| `NOTIFICATION` | PagerDuty, Slack SOC War Room, Jira |

## Data Flow

```
1. Security Alert fires (SIEM ingest or cron)
2. PlaybookEngine selects matching trigger type
3. DAG nodes executed in topological order
4. Step results persisted to PlaybookExecutionRun
5. HUMAN_GATE pauses for SOC approval (5 min timeout)
6. Final notification dispatched to PAGERDUTY + SLACK
```

## Horizontal Scale

- Playbook DAGs are stateless — any worker can resume from `PlaybookExecutionRun.current_step`
- Dry-run simulation engine is fully isolated; no production API calls made
- Templates seeded once per tenant at activation time
