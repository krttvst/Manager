import { apiFetch } from "./client.js";

export function getDashboardOverview(token) {
  return apiFetch("/dashboard/overview", { token });
}

