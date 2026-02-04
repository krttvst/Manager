import { apiFetch } from "./client.js";

export function listSuggestions(token, channelId, { limit = 50, offset = 0 } = {}) {
  const params = new URLSearchParams();
  if (limit) params.set("limit", String(limit));
  if (offset) params.set("offset", String(offset));
  const query = params.toString();
  const path = query ? `/channels/${channelId}/suggestions?${query}` : `/channels/${channelId}/suggestions`;
  return apiFetch(path, { token });
}

export function acceptSuggestion(token, channelId, suggestionId) {
  return apiFetch(`/channels/${channelId}/suggestions/${suggestionId}/accept`, { method: "POST", token });
}

export function rejectSuggestion(token, channelId, suggestionId) {
  return apiFetch(`/channels/${channelId}/suggestions/${suggestionId}`, { method: "DELETE", token });
}
