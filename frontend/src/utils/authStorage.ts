/**
 * frontend/src/utils/authStorage.ts
 * =================================
 * Canonical token and tenant storage management for Aegivanta Frontend.
 * Unifies access across standard REST API, SaaS services, WebSockets, and Reports.
 */

const TOKEN_KEY_PRIMARY = 'aegivanta_token';
const TOKEN_KEY_LEGACY = 'sentinel_token';
const TOKEN_KEY_GENERIC = 'token';
const TENANT_KEY = 'active_tenant_id';

export const authStorage = {
  /**
   * Retrieves active access token with fallback across supported keys.
   */
  getAccessToken(): string | null {
    return (
      localStorage.getItem(TOKEN_KEY_PRIMARY) ||
      localStorage.getItem(TOKEN_KEY_LEGACY) ||
      localStorage.getItem(TOKEN_KEY_GENERIC) ||
      null
    );
  },

  /**
   * Persists access token across standard keys for backward compatibility.
   */
  setAccessToken(token: string): void {
    localStorage.setItem(TOKEN_KEY_PRIMARY, token);
    localStorage.setItem(TOKEN_KEY_LEGACY, token);
    localStorage.setItem(TOKEN_KEY_GENERIC, token);
  },

  /**
   * Clears all stored authentication tokens.
   */
  clearAccessToken(): void {
    localStorage.removeItem(TOKEN_KEY_PRIMARY);
    localStorage.removeItem(TOKEN_KEY_LEGACY);
    localStorage.removeItem(TOKEN_KEY_GENERIC);
  },

  /**
   * Retrieves active tenant ID.
   */
  getActiveTenantId(): string | null {
    return localStorage.getItem(TENANT_KEY) || null;
  },

  /**
   * Sets active tenant ID.
   */
  setActiveTenantId(tenantId: string): void {
    localStorage.setItem(TENANT_KEY, tenantId);
  },

  /**
   * Clears active tenant ID.
   */
  clearActiveTenantId(): void {
    localStorage.removeItem(TENANT_KEY);
  }
};
