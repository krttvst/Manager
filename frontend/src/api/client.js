const DEFAULT_ERROR = "Ошибка запроса";
const AUTH_LOGOUT_EVENT = "auth:logout";
const API_PREFIX = "/v1";

function getStoredToken() {
  if (typeof localStorage === "undefined") return null;
  return localStorage.getItem("token");
}

function normalizePath(path) {
  if (path.startsWith(API_PREFIX)) return path;
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${API_PREFIX}${normalized}`;
}

function buildError(res, data) {
  const requestId = res.headers.get("x-request-id") || data?.request_id || null;
  const message = data?.detail || DEFAULT_ERROR;
  const err = new Error(requestId ? `${message} (request_id: ${requestId})` : message);
  err.status = res.status;
  err.requestId = requestId;
  return err;
}

function logApiError(err) {
  console.error("API error", {
    message: err.message,
    status: err.status,
    requestId: err.requestId
  });
}

export async function apiFetch(path, { token, method = "GET", body } = {}) {
  const authToken = token || getStoredToken();
  const url = normalizePath(path);
  let res;
  try {
    res = await fetch(url, {
      method,
      headers: {
        ...(body ? { "Content-Type": "application/json" } : {}),
        ...(authToken ? { Authorization: `Bearer ${authToken}` } : {})
      },
      body: body ? JSON.stringify(body) : undefined
    });
  } catch (err) {
    const netErr = new Error("Сетевая ошибка");
    logApiError(netErr);
    throw netErr;
  }
  if (res.status === 401) {
    const data = await safeJson(res);
    const err = buildError(res, data);
    logApiError(err);
    if (typeof localStorage !== "undefined") {
      localStorage.removeItem("token");
    }
    if (typeof window !== "undefined") {
      window.dispatchEvent(new Event(AUTH_LOGOUT_EVENT));
    }
    throw err;
  }
  if (!res.ok) {
    const data = await safeJson(res);
    const err = buildError(res, data);
    logApiError(err);
    throw err;
  }
  if (res.status === 204) return null;
  return res.json();
}

async function safeJson(res) {
  try {
    return await res.json();
  } catch {
    return null;
  }
}

export async function apiFetchMultipart(path, { token, form, method = "POST" } = {}) {
  const authToken = token || getStoredToken();
  const url = normalizePath(path);
  let res;
  try {
    res = await fetch(url, {
      method,
      headers: {
        ...(authToken ? { Authorization: `Bearer ${authToken}` } : {})
      },
      body: form
    });
  } catch {
    const netErr = new Error("Сетевая ошибка");
    logApiError(netErr);
    throw netErr;
  }
  if (res.status === 401) {
    const data = await safeJson(res);
    const err = buildError(res, data);
    logApiError(err);
    if (typeof localStorage !== "undefined") {
      localStorage.removeItem("token");
    }
    if (typeof window !== "undefined") {
      window.dispatchEvent(new Event(AUTH_LOGOUT_EVENT));
    }
    throw err;
  }
  if (!res.ok) {
    const data = await safeJson(res);
    const err = buildError(res, data);
    logApiError(err);
    throw err;
  }
  return res.json();
}
