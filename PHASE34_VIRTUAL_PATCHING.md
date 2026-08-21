# PHASE 34 — WAF & IPS VIRTUAL PATCHING SPECIFICATION

## 1. Supported Compensating Rule Formats

1. **AWS WAF Rule Statements**: JSON-formatted byte match and regex statements blocking exploitation paths at the Application Load Balancer / CloudFront edge.
2. **ModSecurity / Coraza CRS Rules**: Web Application Firewall rules deployed on Nginx, Envoy, or Apache ingress gateways.
3. **Suricata / Snort Signatures**: Network intrusion prevention system rules dropping exploit traffic at the perimeter firewall.
