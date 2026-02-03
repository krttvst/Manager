import { apiFetch } from "./client.js";

export function listPosts(token, channelId, { statusFilter, statusFilters, limit = 50, offset = 0 } = {}) {
  const params = new URLSearchParams();
  if (statusFilter) params.set("status_filter", statusFilter);
  if (Array.isArray(statusFilters)) {
    statusFilters.forEach((value) => params.append("status_filters", value));
  }
  if (limit) params.set("limit", String(limit));
  if (offset) params.set("offset", String(offset));
  const query = params.toString();
  const path = query ? `/channels/${channelId}/posts?${query}` : `/channels/${channelId}/posts`;
  return apiFetch(path, { token });
}

export function createPost(token, channelId, payload) {
  return apiFetch(`/channels/${channelId}/posts`, { method: "POST", token, body: payload });
}

export function updatePost(token, postId, payload) {
  return apiFetch(`/posts/${postId}`, { method: "PUT", token, body: payload });
}

export function getPost(token, postId) {
  return apiFetch(`/posts/${postId}`, { token });
}

export function submitApproval(token, postId) {
  return apiFetch(`/posts/${postId}/submit-approval`, { method: "POST", token });
}

export function approvePost(token, postId) {
  return apiFetch(`/posts/${postId}/approve`, { method: "POST", token });
}

export function rejectPost(token, postId, payload) {
  return apiFetch(`/posts/${postId}/reject`, { method: "POST", token, body: payload });
}

export function schedulePost(token, postId, payload) {
  return apiFetch(`/posts/${postId}/schedule`, { method: "POST", token, body: payload });
}

export function publishNow(token, postId) {
  return apiFetch(`/posts/${postId}/publish-now`, { method: "POST", token });
}

export function deletePost(token, postId) {
  return apiFetch(`/posts/${postId}`, { method: "DELETE", token });
}
