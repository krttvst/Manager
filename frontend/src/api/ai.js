import { apiFetch } from "./client.js";

export function generateFromUrl(token, postId, payload) {
  return apiFetch(`/posts/${postId}/ai-generate`, { method: "POST", token, body: payload });
}
