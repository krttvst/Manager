import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../state/auth.jsx";
import { apiFetch } from "../state/api.js";
import CreateChannelModal from "./CreateChannelModal.jsx";

export default function Dashboard() {
  const { token, user } = useAuth();
  const [channels, setChannels] = useState([]);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch("/channels", { token });
        setChannels(data);
      } catch (err) {
        setError(err.message);
      }
    }
    load();
  }, [token]);

  return (
    <section>
      <div className="page-header">
        <h1>Каналы</h1>
        {user?.role === "admin" && (
          <button className="primary" onClick={() => setShowModal(true)}>
            Добавить канал
          </button>
        )}
      </div>
      {error && <div className="error">{error}</div>}
      <div className="grid">
        {channels.map((ch) => (
          <Link key={ch.id} to={`/channels/${ch.id}`} className="card">
            <h3>{ch.title}</h3>
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
          onCreated={(channel) => setChannels((prev) => [channel, ...prev])}
        />
      )}
    </section>
  );
}
