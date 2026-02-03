import { useState } from "react";
import { useAuth } from "../state/auth.jsx";
import { createPost } from "../api/posts.js";
import { generateFromUrl } from "../api/ai.js";

export default function AiGenerateModal({ channelId, onClose, onCreated }) {
  const { token } = useAuth();
  const [url, setUrl] = useState("");
  const [tone, setTone] = useState("neutral");
  const [length, setLength] = useState("medium");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const draft = await createPost(token, channelId, { title: "Черновик", body_text: "..." });
      await generateFromUrl(token, draft.id, { url, tone, length, language: "ru" });
      onCreated();
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Сгенерировать из URL</h2>
        <form onSubmit={handleSubmit} className="modal-form">
          <label>
            URL источника
            <input value={url} onChange={(e) => setUrl(e.target.value)} required />
          </label>
          <label>
            Тональность
            <select value={tone} onChange={(e) => setTone(e.target.value)}>
              <option value="neutral">Нейтрально</option>
              <option value="friendly">Дружелюбно</option>
              <option value="expert">Экспертно</option>
            </select>
          </label>
          <label>
            Длина
            <select value={length} onChange={(e) => setLength(e.target.value)}>
              <option value="short">Коротко</option>
              <option value="medium">Средне</option>
              <option value="long">Длинно</option>
            </select>
          </label>
          {error && <div className="error">{error}</div>}
          <div className="actions">
            <button type="button" className="ghost-dark" onClick={onClose} disabled={loading}>
              Отмена
            </button>
            <button type="submit" className="primary" disabled={loading}>
              {loading ? "Генерация..." : "Сгенерировать"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
