/** Base URL for API requests. Uses Vite env var in production, defaults to backend. */
export const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/** Generate SHA-256 hash prefix matching backend (storage.py). */
export async function sha256Prefix(input: string, length = 12): Promise<string> {
  const data = new TextEncoder().encode(input);
  const hash = await crypto.subtle.digest('SHA-256', data);
  return Array.from(new Uint8Array(hash))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('')
    .slice(0, length);
}

// ── API Key management (localStorage) ──────────────────────────

const API_KEY_STORAGE_KEY = 'repo_health_deepseek_key';

export function getApiKey(): string {
  try {
    return localStorage.getItem(API_KEY_STORAGE_KEY) || '';
  } catch {
    return '';
  }
}

export function setApiKey(key: string): void {
  try {
    localStorage.setItem(API_KEY_STORAGE_KEY, key.trim());
  } catch {
    // localStorage unavailable
  }
}

export function clearApiKey(): void {
  try {
    localStorage.removeItem(API_KEY_STORAGE_KEY);
  } catch {
    // localStorage unavailable
  }
}
