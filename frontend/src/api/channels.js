import { apiFetch } from "./client.js";

export function listChannels(token) {
  return apiFetch("/channels", { token });
}

export function createChannel(token, payload) {
  return apiFetch("/channels", { method: "POST", token, body: payload });
}

export function getChannel(token, channelId) {
  return apiFetch(`/channels/${channelId}`, { token });
}

export function deleteChannel(token, channelId) {
  return apiFetch(`/channels/${channelId}`, { method: "DELETE", token });
}

export function lookupChannel(token, identifier) {
  const params = new URLSearchParams({ identifier });
  return apiFetch(`/channels/lookup?${params.toString()}`, { token });
}
