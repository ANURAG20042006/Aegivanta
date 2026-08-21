# PHASE 40 — HOMOMORPHIC HASHING SPECIFICATION

## 1. Zero-Knowledge Match Protocol

- Indicators and queries are transformed into cryptographically salted SHA-256 digests.
- Indicator matches occur entirely in the hashed domain:
$$ \text{Match}(\text{Hash}(Q), \text{Hash}(I)) = \begin{cases} 1 & \text{if } \text{Hash}(Q) = \text{Hash}(I) \\ 0 & \text{otherwise} \end{cases} $$
