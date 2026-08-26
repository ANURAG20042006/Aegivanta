# PHASE 35 — FRONTEND DLP COMMAND CENTER

## 1. UI Tabs

`DLPCommandCenter.tsx` delivers a 6-tab enterprise interface:
1. **DLP Overview**: Posture score, active inspection policies, blocked exfiltrations count, tokenized records, discovered shadow data stores, and top directives.
2. **Inspection Policies**: Policy ledger displaying data categories, sensitivity tiers, regex patterns, keywords, and enforcement actions.
3. **Exfiltration Incidents**: Real-time exfiltration log showing source user, channel, destination, matched policy, and masked payload samples.
4. **Tokenization Vault (FPE)**: Cryptographic surrogate ledger with live detokenization modal.
5. **Shadow Data (DSPM)**: Exposure map highlighting unencrypted cloud storage buckets and database records.
6. **Live Payload Scanner**: Interactive sandbox allowing real-time test evaluation and masking of raw payload snippets.
