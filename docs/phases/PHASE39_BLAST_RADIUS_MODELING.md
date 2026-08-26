# PHASE 39 — BLAST RADIUS MODELING SPECIFICATION

## 1. Node Blast Projection

Computes estimated reachable workloads $N_{\text{blast}}$ under simulated lateral pivot conditions:
$$ N_{\text{blast}} = \left| \bigcup_{v \in V_{\text{compromised}}} \text{ReachableNodes}(v, \text{ZTNA\_Topology}) \right| $$
