export const AUTH_LOGOUT_EVENT = "auth:logout";

export function emitAuthLogout() {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new Event(AUTH_LOGOUT_EVENT));
}

