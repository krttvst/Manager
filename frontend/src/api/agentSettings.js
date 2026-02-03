import { apiFetch } from "./client.js";

export function getAgentSettings(token, channelId) {
  return apiFetch(`/channels/${channelId}/agent-settings`, { token });
}

export function updateAgentSettings(token, channelId, payload) {
  return apiFetch(`/channels/${channelId}/agent-settings`, { method: "PUT", token, body: payload });
}

