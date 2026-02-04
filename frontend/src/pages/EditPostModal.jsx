import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { updatePost, publishNow, schedulePost, submitApproval, approvePost } from "../api/posts.js";
import { uploadMedia } from "../api/media.js";
import { useAuth } from "../state/auth.jsx";
import { formatDateTimeLocal, normalizeApiDate } from "../utils/date.js";

export default function EditPostModal({ post, canApprove, onClose, onUpdated }) {
  const { token } = useAuth();
  const [title, setTitle] = useState(post.title);
  const [bodyText, setBodyText] = useState(post.body_text);
  const [imageFile, setImageFile] = useState(null);
  const [error, setError] = useState("");
  const initialScheduled = post.scheduled_at
    ? formatDateTimeLocal(new Date(normalizeApiDate(post.scheduled_at)))
    : "";
  const [scheduledAt, setScheduledAt] = useState(initialScheduled);
  const [tzHint, setTzHint] = useState("");
  const isPublished = post.status === "published";

  const updateMutation = useMutation({
    mutationFn: async () => {
      const mediaUrl = await resolveMediaUrl();
      return await updatePost(token, post.id, {
        title,
        body_text: bodyText,
        media_url: mediaUrl
      });
    },
    onError: (err) => setError(err.message)
  });

  const publishNowMutation = useMutation({
    mutationFn: async () => {
      const updated = await updateMutation.mutateAsync();
      await submitApproval(token, updated.id);
      await approvePost(token, updated.id);
      return await publishNow(token, updated.id);
    },
    onError: (err) => setError(err.message)
  });

  const scheduleMutation = useMutation({
    mutationFn: async (iso) => {
      const updated = await updateMutation.mutateAsync();
      await submitApproval(token, updated.id);
      await approvePost(token, updated.id);
      return await schedulePost(token, updated.id, { scheduled_at: iso });
    },
    onError: (err) => setError(err.message)
  });

  function validateSchedule() {
    if (!scheduledAt) {
      setError("Выберите дату и время публикации");
      return false;
    }
    const selected = new Date(scheduledAt);
    if (Number.isNaN(selected.getTime()) || selected <= new Date()) {
      setError("Дата и время должны быть в будущем");
      return false;
    }
    return true;
  }

  async function resolveMediaUrl() {
    let mediaUrl = post.media_url || null;
    if (imageFile) {
      const uploaded = await uploadMedia(token, imageFile);
      mediaUrl = uploaded.url;
    }
    return mediaUrl;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    try {
      const updated = await updateMutation.mutateAsync();
      if (canApprove && scheduledAt && !isPublished) {
        const selected = new Date(scheduledAt);
        if (Number.isNaN(selected.getTime()) || selected <= new Date()) {
          setError("Дата и время должны быть в будущем");
          return;
        }
        const iso = selected.toISOString();
        const scheduled = await scheduleMutation.mutateAsync(iso);
        onUpdated(scheduled);
        onClose();
        return;
      }
      onUpdated(updated);
      onClose();
    } catch {}
  }

  async function handlePublishNow() {
    setError("");
    if (isPublished) {
      setError("Пост уже опубликован.");
      return;
    }
    try {
      const published = await publishNowMutation.mutateAsync();
      onUpdated(published);
      onClose();
    } catch {}
  }

  async function handleSchedule() {
    setError("");
    if (isPublished) {
      setError("Нельзя запланировать уже опубликованный пост.");
      return;
    }
    if (!validateSchedule()) return;
    try {
      const iso = new Date(scheduledAt).toISOString();
      const scheduled = await scheduleMutation.mutateAsync(iso);
      onUpdated(scheduled);
      onClose();
    } catch {}
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Редактировать пост</h2>
        <form onSubmit={handleSubmit} className="modal-form">
          <label>
            Заголовок
            <input value={title} onChange={(e) => setTitle(e.target.value)} required />
          </label>
          <label>
            Текст
            <textarea value={bodyText} onChange={(e) => setBodyText(e.target.value)} rows={6} required />
          </label>
          <label>
            Картинка
            <input type="file" accept="image/*" onChange={(e) => setImageFile(e.target.files?.[0] || null)} />
          </label>
          {!isPublished && canApprove && (
            <>
              <label>
                Дата и время публикации
                <input
                  type="datetime-local"
                  value={scheduledAt}
                  onChange={(e) => {
                    setScheduledAt(e.target.value);
                    if (!tzHint) {
                      const offset = -new Date().getTimezoneOffset() / 60;
                      setTzHint(`Время по вашему часовому поясу (UTC${offset >= 0 ? "+" : ""}${offset}).`);
                    }
                  }}
                  min={formatDateTimeLocal(new Date())}
                />
              </label>
              {tzHint && <div className="hint">{tzHint}</div>}
            </>
          )}
          {error && <div className="error">{error}</div>}
          <div className="actions">
            <button type="button" className="ghost-dark" onClick={onClose}>
              Отмена
            </button>
            <button
              type="submit"
              className="ghost-dark"
              disabled={updateMutation.isPending || scheduleMutation.isPending || publishNowMutation.isPending}
            >
              {updateMutation.isPending ? "Сохранение..." : "Сохранить"}
            </button>
            {!isPublished && canApprove && (
              <>
                <button
                  type="button"
                  className="ghost-dark"
                  onClick={handlePublishNow}
                  disabled={publishNowMutation.isPending || updateMutation.isPending}
                >
                  {publishNowMutation.isPending ? "Публикация..." : "Опубликовать сразу"}
                </button>
                <button
                  type="button"
                  className="primary"
                  onClick={handleSchedule}
                  disabled={!scheduledAt || scheduleMutation.isPending || updateMutation.isPending}
                >
                  {scheduleMutation.isPending ? "Сохраняем..." : "Добавить в очередь"}
                </button>
              </>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
