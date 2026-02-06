import { emitAuthLogout } from "../state/authEvents.js";
import { clearStoredToken, getStoredToken } from "../state/tokenStorage.js";

const DEFAULT_ERROR = "Ошибка запроса";
const API_PREFIX = "/v1";

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

async function apiRequest(path, { token, method = "GET", body, isMultipart = false } = {}) {
  const authToken = token || getStoredToken();
  const url = normalizePath(path);
  let res;
  try {
    res = await fetch(url, {
      method,
      headers: {
        ...(body && !isMultipart ? { "Content-Type": "application/json" } : {}),
        ...(authToken ? { Authorization: `Bearer ${authToken}` } : {})
      },
      body: body ? (isMultipart ? body : JSON.stringify(body)) : undefined
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
    clearStoredToken();
    emitAuthLogout();
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

export async function apiFetch(path, { token, method = "GET", body } = {}) {
  return apiRequest(path, { token, method, body, isMultipart: false });
}

async function safeJson(res) {
  try {
    return await res.json();
  } catch {
    return null;
  }
}

export async function apiFetchMultipart(path, { token, form, method = "POST" } = {}) {
  return apiRequest(path, { token, method, body: form, isMultipart: true });
}
