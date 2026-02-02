import { useState } from "react";
import { useAuth } from "../state/auth.jsx";

export default function CreateChannelModal({ onClose, onCreated }) {
  const { token } = useAuth();
  const [title, setTitle] = useState("");
  const [identifier, setIdentifier] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    try {
      const res = await fetch("/channels", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ title, telegram_channel_identifier: identifier })
      });
      if (!res.ok) throw new Error("Не удалось создать канал");
      const channel = await res.json();
      onCreated(channel);
      onClose();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Новый канал</h2>
        <form onSubmit={handleSubmit} className="modal-form">
          <label>
            Название
            <input value={title} onChange={(e) => setTitle(e.target.value)} required />
          </label>
          <label>
            Telegram идентификатор
            <input value={identifier} onChange={(e) => setIdentifier(e.target.value)} placeholder="@channel" required />
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
