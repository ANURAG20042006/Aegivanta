# PHASE 35 — LUHN ALGORITHM (MOD-10) SPECIFICATION

## 1. Algorithmic Formulation

The Luhn algorithm validates credit card Primary Account Numbers (PANs):
1. Reverse digits.
2. Multiply every second digit by 2. If product $> 9$, subtract 9.
3. Sum all modified and unmodified digits.
4. If $Sum \pmod{10} = 0$, the number is structurally valid.
