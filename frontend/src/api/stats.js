import { apiFetch } from "./client.js";

export function getChannelStats(token, channelId) {
  return apiFetch(`/channels/${channelId}/stats`, { token });
}
