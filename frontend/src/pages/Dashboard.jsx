import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../state/auth.jsx";
import CreateChannelModal from "./CreateChannelModal.jsx";
import { useChannelsQuery } from "../hooks/useChannelsQuery.js";

export default function Dashboard() {
  const { token } = useAuth();
  const [showModal, setShowModal] = useState(false);
  const { channels, isLoading, error, addChannel } = useChannelsQuery(token);
  const errorMessage = error?.message || "";

  return (
    <section>
      <div className="page-header">
        <h1>Каналы</h1>
        <button className="primary" onClick={() => setShowModal(true)}>
          Добавить канал
        </button>
      </div>
      {isLoading && <div className="hint">Загрузка...</div>}
      {errorMessage && <div className="error">{errorMessage}</div>}
      <div className="grid">
        {channels.map((ch) => (
          <Link key={ch.id} to={`/channels/${ch.id}`} className="card">
            <div className="card-header">
              {ch.avatar_url && <img className="channel-avatar" src={ch.avatar_url} alt="" loading="lazy" />}
              <h3>{ch.title}</h3>
            </div>
            <p className="muted">{ch.telegram_channel_identifier}</p>
            <div className="mini">Следующая публикация: —</div>
            <div className="mini">Последний пост: —</div>
          </Link>
        ))}
        {channels.length === 0 && <div className="empty">Пока нет подключённых каналов.</div>}
      </div>

      {showModal && (
        <CreateChannelModal
          onClose={() => setShowModal(false)}
          onCreated={(channel) => {
            addChannel(channel);
          }}
        />
      )}
    </section>
  );
}
