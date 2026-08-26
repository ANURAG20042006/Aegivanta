# Aegivanta Phase 5 — Enterprise Single Sign-On (SSO)

## 1. Protocols & Supported Identity Providers

- **OpenID Connect (OIDC)**: Discovery document parsing, authorization code flow, PKCE support.
- **SAML 2.0**: X.509 certificate validation, Entity ID verification, and SAML assertion consumers.
- **Tested Providers**: Okta, Microsoft Entra ID (Azure AD), OneLogin, Google Workspace, PingFederate.

## 2. Anti-CSRF & Replay Defense
Every SSO authorization URL embeds a cryptographic `state` and single-use `nonce`. Callbacks mismatched with the expected state are rejected with HTTP 401.
