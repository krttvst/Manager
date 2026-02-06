const TOKEN_KEY = "token";

export function getStoredToken() {
  if (typeof localStorage === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setStoredToken(token) {
  if (typeof localStorage === "undefined") return;
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearStoredToken() {
  if (typeof localStorage === "undefined") return;
  localStorage.removeItem(TOKEN_KEY);
}

