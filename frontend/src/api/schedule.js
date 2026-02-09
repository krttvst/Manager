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

export function listSchedule(token, params = {}) {
  return apiFetch(`/schedule${buildQuery(params)}`, { token });
}

export function requeuePost(token, postId, payload = {}) {
  return apiFetch(`/schedule/posts/${postId}/requeue`, { method: "POST", token, body: payload });
}

