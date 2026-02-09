import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "../state/auth.jsx";
import { useChannelsQuery } from "../hooks/useChannelsQuery.js";
import { listSchedule } from "../api/schedule.js";
import { formatDateTime } from "../utils/date.js";

const PAGE_SIZE = 50;

export default function Schedule() {
  const { token } = useAuth();
  const { channels } = useChannelsQuery(token);
  const [channelId, setChannelId] = useState("");
  const [offset, setOffset] = useState(0);

  const params = useMemo(
    () => ({
      limit: PAGE_SIZE,
      offset,
      channel_id: channelId ? Number(channelId) : undefined
    }),
    [offset, channelId]
  );

  const query = useQuery({
    queryKey: ["schedule", params],
    queryFn: () => listSchedule(token, params),
    enabled: Boolean(token)
  });

  const data = query.data;
  const items = data?.items ?? [];
  const total = data?.total ?? 0;

  return (
    <section>
      <div className="page-header">
        <h1>Очередь</h1>
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <div className="actions-inline">
          <label>
            Канал
            <select value={channelId} onChange={(e) => { setChannelId(e.target.value); setOffset(0); }}>
              <option value="">Все</option>
              {channels.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.title}
                </option>
              ))}
            </select>
          </label>
        </div>
        <div className="mini" style={{ marginTop: 10 }}>
          Всего: {total}. Показано: {items.length}. Offset: {offset}.
        </div>
      </div>

      {query.isLoading && <div className="hint" style={{ marginTop: 12 }}>Загрузка...</div>}
      {query.error && <div className="error" style={{ marginTop: 12 }}>{query.error.message}</div>}

      <div className="grid-section" style={{ marginTop: 18 }}>
        {items.map((it) => (
          <div key={it.id} className="card">
            <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
              <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
                <strong>{it.channel_title || `channel:${it.channel_id}`}</strong>
                <div className="muted">{it.title}</div>
                {it.last_error && <div className="mini">last_error: {it.last_error}</div>}
              </div>
              <div className="mini" style={{ whiteSpace: "nowrap" }}>{formatDateTime(it.scheduled_at)}</div>
            </div>
          </div>
        ))}
        {items.length === 0 && !query.isLoading && <div className="empty">Нет запланированных постов.</div>}
      </div>

      {items.length > 0 && offset + PAGE_SIZE < total && (
        <div style={{ marginTop: 16 }}>
          <button type="button" className="ghost" onClick={() => setOffset((v) => v + PAGE_SIZE)}>
            Еще
          </button>
        </div>
      )}
    </section>
  );
}

