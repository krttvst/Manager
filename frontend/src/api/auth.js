import { apiFetch } from "./client.js";

export function login(email, password) {
  return apiFetch("/auth/login", { method: "POST", body: { email, password } });
}

export function getMe(token) {
  return apiFetch("/users/me", { token });
}
