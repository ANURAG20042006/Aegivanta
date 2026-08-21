# PHASE 45 — HMAC-SHA256 WEBHOOKS SPECIFICATION

## 1. Webhook Signature Verification

Webhook deliveries provide an authentication header:
$$ \text{Header: } X\text{-Aegivanta-Signature: sha256=} \text{HMAC-SHA256}(K_{\text{secret}}, \text{Payload}_{\text{raw}}) $$

Receiving endpoints must compute the HMAC digest over the raw request body and compare with constant-time equality check.
