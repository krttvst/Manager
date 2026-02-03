import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useAuth } from "../state/auth.jsx";
import { createPost, publishNow, schedulePost, submitApproval, approvePost } from "../api/posts.js";
import { uploadMedia } from "../api/media.js";
import { formatDateTimeLocal } from "../utils/date.js";

export default function CreatePostModal({ channelId, onClose, onCreated }) {
  const { token } = useAuth();
  const [title, setTitle] = useState("");
  const [bodyText, setBodyText] = useState("");
  const [imageFile, setImageFile] = useState(null);
  const [error, setError] = useState("");
  const [scheduledAt, setScheduledAt] = useState("");
  const [tzHint, setTzHint] = useState("");

  const submitMutation = useMutation({
    mutationFn: async () => {
      if (scheduledAt) {
        const selected = new Date(scheduledAt);
        if (Number.isNaN(selected.getTime()) || selected <= new Date()) {
          throw new Error("Дата и время должны быть в будущем");
        }
      }
      let mediaUrl = null;
      if (imageFile) {
        const uploaded = await uploadMedia(token, imageFile);
        mediaUrl = uploaded.url;
      }
      const post = await createPost(token, channelId, {
        title,
        body_text: bodyText,
        media_url: mediaUrl
      });
      if (scheduledAt) {
        const iso = new Date(scheduledAt).toISOString();
        await submitApproval(token, post.id);
        await approvePost(token, post.id);
        await schedulePost(token, post.id, { scheduled_at: iso });
      } else {
        await publishNow(token, post.id);
      }
      return post;
    },
    onSuccess: (post) => {
      onCreated(post);
      onClose();
    },
    onError: (err) => setError(err.message)
  });

  const saveDraftMutation = useMutation({
    mutationFn: async () => {
      let mediaUrl = null;
      if (imageFile) {
        const uploaded = await uploadMedia(token, imageFile);
        mediaUrl = uploaded.url;
      }
      return await createPost(token, channelId, {
        title,
        body_text: bodyText,
        media_url: mediaUrl
      });
    },
    onSuccess: (post) => {
      onCreated(post);
      onClose();
    },
    onError: (err) => setError(err.message)
  });

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    try {
      await submitMutation.mutateAsync();
    } catch {}
  }

  async function handleSaveDraft() {
    setError("");
    try {
      await saveDraftMutation.mutateAsync();
    } catch {}
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Новый пост</h2>
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
          {error && <div className="error">{error}</div>}
          <div className="actions">
            <button type="button" className="ghost-dark" onClick={onClose}>
              Отмена
            </button>
            <button
              type="button"
              className="ghost-dark"
              onClick={handleSaveDraft}
              disabled={submitMutation.isPending || saveDraftMutation.isPending}
            >
              Сохранить
            </button>
            <button type="submit" className="primary" disabled={submitMutation.isPending || saveDraftMutation.isPending}>
              {submitMutation.isPending
                ? "Подождите..."
                : scheduledAt
                ? "Добавить в очередь"
                : "Опубликовать сразу"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
