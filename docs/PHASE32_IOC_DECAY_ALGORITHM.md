# PHASE 32 — IOC EXPONENTIAL DECAY ALGORITHM SPECIFICATION

## 1. Mathematical Formulation

The dynamic confidence score of an indicator decays exponentially over elapsed time:

$$ C(t) = C_0 \cdot 2^{-\frac{\Delta t}{T_{1/2}}} $$

Where:
- $C_0$: Initial verified confidence score (e.g., 95.0%).
- $\Delta t$: Elapsed days since the most recent verified sighting.
- $T_{1/2}$: Configured decay halflife in days (default: 45 days for IP, 90 days for domain, 180 days for hash).
- **Auto-Revocation**: When $C(t) < 20.0\%$, the indicator is automatically marked as inactive.
