# PHASE 40 — PRIVACY BUDGET ALLOCATION SPECIFICATION

## 1. Budget Composition

- Composition bounds total privacy loss across multiple queries:
$$ \epsilon_{\text{total}} = \sum_{k=1}^K \epsilon_k $$
- Automatic rate-limiters halt telemetry syndication once daily $\epsilon$-budget exceeds configured threshold ($\epsilon \le 2.0$).
