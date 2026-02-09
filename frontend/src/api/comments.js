import { apiFetch } from "./client.js";

export function listPostComments(token, postId, { limit = 200, offset = 0 } = {}) {
  return apiFetch(`/posts/${postId}/comments?limit=${limit}&offset=${offset}`, { token });
}

export function createPostComment(token, postId, bodyText) {
  return apiFetch(`/posts/${postId}/comments`, { method: "POST", token, body: { body_text: bodyText } });
}

