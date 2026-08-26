# PHASE 40 — DIFFERENTIAL PRIVACY SPECIFICATION

## 1. Mathematical Privacy Definition

A randomized algorithm $\mathcal{M}$ satisfies $(\epsilon, \delta)$-differential privacy if for all neighboring datasets $D, D'$:
$$ \mathbb{P}[\mathcal{M}(D) \in S] \le e^{\epsilon} \mathbb{P}[\mathcal{M}(D') \in S] + \delta $$

Calibrated Laplace mechanism applies noise:
$$ Y = f(D) + \text{Lap}\left( \frac{\Delta f}{\epsilon} \right) $$
where $\Delta f = 1$ for individual sighting count queries.
