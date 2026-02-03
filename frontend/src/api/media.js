import { apiFetchMultipart } from "./client.js";

export async function uploadMedia(token, file) {
  const form = new FormData();
  form.append("file", file);
  return apiFetchMultipart("/media/upload", { token, form });
}

export function previewUrl(mediaUrl) {
  if (!mediaUrl) return null;
  if (mediaUrl.includes("/media/previews/")) return mediaUrl;
  if (mediaUrl.startsWith("/media/")) {
    const name = mediaUrl.slice("/media/".length);
    return `/media/previews/${name}`;
  }
  return mediaUrl;
}
