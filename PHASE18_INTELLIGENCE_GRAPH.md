# AEGIVANTA — PHASE 18 INTELLIGENCE GRAPH SPECIFICATION

## 1. Multi-Entity Relationships
The Threat Intelligence Graph models evidence-backed directed edges across:
- `IP` $\leftrightarrow$ `Domain`
- `Domain` $\leftrightarrow$ `Certificate`
- `Hash` $\leftrightarrow$ `Malware Family`
- `IOC` $\leftrightarrow$ `Campaign`
- `Campaign` $\leftrightarrow$ `Threat Actor`
- `Threat Actor` $\leftrightarrow$ `MITRE Technique`
- `Alert` $\leftrightarrow$ `IOC`
- `Incident` $\leftrightarrow$ `Campaign`

## 2. Graph Traversal & Pivot Performance
Graph queries utilize indexed relationship edges (`ix_threat_edge_source_target`) to guarantee sub-10ms topological rendering for investigation graphs up to 500 nodes.
