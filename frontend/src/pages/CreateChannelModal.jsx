import { useEffect, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useAuth } from "../state/auth.jsx";
import { createChannel, lookupChannel } from "../api/channels.js";

export default function CreateChannelModal({ onClose, onCreated }) {
  const { token } = useAuth();
  const [title, setTitle] = useState("");
  const [identifier, setIdentifier] = useState("");
  const [error, setError] = useState("");
  const [avatarUrl, setAvatarUrl] = useState("");
  const [lookupStatus, setLookupStatus] = useState("idle");
  const [titleTouched, setTitleTouched] = useState(false);
  const [lookupError, setLookupError] = useState("");

  const createMutation = useMutation({
    mutationFn: () =>
      createChannel(token, {
        title,
        telegram_channel_identifier: identifier,
        avatar_url: avatarUrl || null
      }),
    onSuccess: (channel) => {
      onCreated(channel);
      onClose();
    },
    onError: (err) => setError(err.message)
  });

  useEffect(() => {
    const trimmed = identifier.trim();
    if (!trimmed) {
      setAvatarUrl("");
      setLookupStatus("idle");
      setLookupError("");
      return;
    }
    setLookupStatus("loading");
    const timer = setTimeout(async () => {
      try {
        const data = await lookupChannel(token, trimmed);
        if (!titleTouched) {
          setTitle(data.title);
        }
        setAvatarUrl(data.avatar_url || "");
        setLookupStatus("ready");
        setLookupError("");
      } catch (err) {
        setLookupStatus("error");
        setLookupError(err.message || "Не удалось найти канал");
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [identifier, token, titleTouched]);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    try {
      await createMutation.mutateAsync();
    } catch {}
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Новый канал</h2>
        <form onSubmit={handleSubmit} className="modal-form">
          <label>
            Название
            <input
              value={title}
              onChange={(e) => {
                setTitle(e.target.value);
                setTitleTouched(true);
              }}
              required
            />
          </label>
          <label>
            Telegram идентификатор
            <input value={identifier} onChange={(e) => setIdentifier(e.target.value)} placeholder="@channel" required />
          </label>
          {lookupStatus === "loading" && <div className="hint">Ищем канал...</div>}
          {lookupStatus === "error" && <div className="error">{lookupError}</div>}
          {avatarUrl && (
            <div className="channel-preview">
              <img className="channel-avatar" src={avatarUrl} alt="" />
              <div>
                <div className="preview-title">{title || "Без названия"}</div>
                <div className="muted">{identifier}</div>
              </div>
            </div>
          )}
          {error && <div className="error">{error}</div>}
          <div className="actions">
            <button type="button" className="ghost-dark" onClick={onClose}>
              Отмена
            </button>
            <button type="submit" className="primary" disabled={createMutation.isPending}>
              {createMutation.isPending ? "Создание..." : "Создать"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
