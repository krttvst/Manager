import { apiFetch } from "./client.js";

function buildQuery(params = {}) {
  const usp = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v === null || v === undefined || v === "") continue;
    usp.set(k, String(v));
  }
  const s = usp.toString();
  return s ? `?${s}` : "";
}

export function listInboxSuggestions(token, params = {}) {
  return apiFetch(`/inbox/suggestions${buildQuery(params)}`, { token });
}

