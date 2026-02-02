export async function apiFetch(path, { token, method = "GET", body } = {}) {
  const res = await fetch(path, {
    method,
    headers: {
      ...(body ? { "Content-Type": "application/json" } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    },
    body: body ? JSON.stringify(body) : undefined
  });
  if (!res.ok) {
    let message = "Ошибка запроса";
    try {
      const data = await res.json();
      if (data?.detail) message = data.detail;
    } catch {
      // ignore
    }
    throw new Error(message);
  }
  if (res.status === 204) return null;
  return res.json();
}
