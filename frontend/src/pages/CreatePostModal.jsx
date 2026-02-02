import { useState } from "react";
import { useAuth } from "../state/auth.jsx";
import { apiFetch } from "../state/api.js";

export default function CreatePostModal({ channelId, onClose, onCreated }) {
  const { token } = useAuth();
  const [title, setTitle] = useState("");
  const [bodyText, setBodyText] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    try {
      const post = await apiFetch(`/channels/${channelId}/posts`, {
        method: "POST",
        token,
        body: { title, body_text: bodyText }
      });
      onCreated(post);
      onClose();
    } catch (err) {
      setError(err.message);
    }
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
          {error && <div className="error">{error}</div>}
          <div className="actions">
            <button type="button" className="ghost-dark" onClick={onClose}>
              Отмена
            </button>
            <button type="submit" className="primary">Создать</button>
          </div>
        </form>
      </div>
    </div>
  );
}
