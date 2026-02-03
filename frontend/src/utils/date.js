export function normalizeApiDate(value) {
  if (!value) return value;
  if (typeof value !== "string") return value;
  if (value.endsWith("Z") || value.includes("+")) return value;
  const normalized = value.includes("T") ? value : value.replace(" ", "T");
  return `${normalized}Z`;
}

export function formatDateTime(value) {
  if (!value) return "—";
  const date = new Date(normalizeApiDate(value));
  if (Number.isNaN(date.getTime())) return "—";
  const pad = (n) => String(n).padStart(2, "0");
  return `${pad(date.getDate())}.${pad(date.getMonth() + 1)}.${date.getFullYear()} ${pad(
    date.getHours()
  )}:${pad(date.getMinutes())}`;
}

export function formatDateTimeLocal(date) {
  const pad = (n) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(
    date.getHours()
  )}:${pad(date.getMinutes())}`;
}

