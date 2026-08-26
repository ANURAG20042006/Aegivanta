# PHASE 30 — PROMPT INJECTION & JAILBREAK DEFENSE GUIDE

## 1. Attack Vectors Handled

1. **Direct System Prompt Overrides**: "Ignore all previous instructions..."
2. **Roleplay / Persona Jailbreaks**: "Pretend you are DAN with no rules..."
3. **Indirect Prompt Injection**: Malicious instructions embedded in parsed HTML/PDF documents.
4. **Token Smuggling / Base64 Evasion**: Decodes and scans obfuscated payload strings before inference.
