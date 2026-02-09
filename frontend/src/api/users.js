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

export function listUsers(token, params = {}) {
  return apiFetch(`/users${buildQuery(params)}`, { token });
}

export function createUser(token, payload) {
  return apiFetch("/users/", { method: "POST", token, body: payload });
}

export function updateUserRole(token, userId, role) {
  return apiFetch(`/users/${userId}/role`, { method: "PATCH", token, body: { role } });
}

export function setUserPassword(token, userId, password) {
  return apiFetch(`/users/${userId}/password`, { method: "PATCH", token, body: { password } });
}

export function setUserActive(token, userId, isActive) {
  return apiFetch(`/users/${userId}/active`, { method: "PATCH", token, body: { is_active: isActive } });
}

export function resetUserPassword(token, userId) {
  return apiFetch(`/users/${userId}/reset-password`, { method: "POST", token });
}
