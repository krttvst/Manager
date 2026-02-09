import { useMemo, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "../state/auth.jsx";
import { useChannelsQuery } from "../hooks/useChannelsQuery.js";
import { listInboxSuggestions } from "../api/inbox.js";
import { acceptSuggestion, rejectSuggestion } from "../api/suggestions.js";
import { useQuery } from "@tanstack/react-query";
import { formatDateTime } from "../utils/date.js";

const PAGE_SIZE = 50;

export default function Inbox() {
  const { token, user } = useAuth();
  const qc = useQueryClient();
  const { channels } = useChannelsQuery(token);
  const [channelId, setChannelId] = useState("");
  const [q, setQ] = useState("");
  const [offset, setOffset] = useState(0);

  const params = useMemo(
    () => ({
      limit: PAGE_SIZE,
      offset,
      channel_id: channelId ? Number(channelId) : undefined,
      q: q || undefined
    }),
    [offset, channelId, q]
  );

  const queryKey = ["inbox-suggestions", params];
  const inboxQuery = useQuery({
    queryKey,
    queryFn: () => listInboxSuggestions(token, params),
    enabled: Boolean(token)
  });

  const data = inboxQuery.data;
  const items = data?.items ?? [];
  const total = data?.total ?? 0;

  const canModerate = user?.role === "admin" || user?.role === "editor";

  const acceptMutation = useMutation({
    mutationFn: async (item) => acceptSuggestion(token, item.channel_id, item.id),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["inbox-suggestions"] });
      await qc.invalidateQueries({ queryKey: ["suggestions"] });
      await qc.invalidateQueries({ queryKey: ["channels"] });
    }
  });

  const rejectMutation = useMutation({
    mutationFn: async (item) => rejectSuggestion(token, item.channel_id, item.id),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["inbox-suggestions"] });
      await qc.invalidateQueries({ queryKey: ["suggestions"] });
    }
  });

  return (
    <section>
      <div className="page-header">
        <h1>Inbox</h1>
      </div>
      {!canModerate && <div className="hint">Доступно только редактору или администратору.</div>}

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
          <label style={{ flex: 1 }}>
            Поиск
            <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="title/body/source_url" />
          </label>
          <button type="button" className="ghost" onClick={() => { setOffset(0); inboxQuery.refetch(); }}>
            Применить
          </button>
        </div>
        <div className="mini" style={{ marginTop: 10 }}>
          Всего: {total}. Показано: {items.length}. Offset: {offset}.
        </div>
      </div>

      {inboxQuery.isLoading && <div className="hint" style={{ marginTop: 12 }}>Загрузка...</div>}
      {inboxQuery.error && <div className="error" style={{ marginTop: 12 }}>{inboxQuery.error.message}</div>}

      <div className="grid-section" style={{ marginTop: 18 }}>
        {items.map((it) => (
          <div key={`${it.channel_id}-${it.id}`} className="card">
            <div className="mini">{formatDateTime(it.created_at)}</div>
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "baseline" }}>
              <strong>{it.channel_title || `channel:${it.channel_id}`}</strong>
              <span className="muted">suggestion:{it.id}</span>
            </div>
            <div style={{ marginTop: 8 }}>
              <div style={{ fontWeight: 600 }}>{it.title}</div>
              <div className="muted" style={{ marginTop: 4, whiteSpace: "pre-wrap" }}>{it.body_text}</div>
              {it.source_url && (
                <div className="mini" style={{ marginTop: 6 }}>Источник: {it.source_url}</div>
              )}
            </div>

            {canModerate && (
              <div className="actions" style={{ marginTop: 12 }}>
                <button
                  type="button"
                  className="ghost-dark"
                  onClick={() => rejectMutation.mutate(it)}
                  disabled={rejectMutation.isPending || acceptMutation.isPending}
                >
                  Отклонить
                </button>
                <button
                  type="button"
                  className="primary"
                  onClick={() => acceptMutation.mutate(it)}
                  disabled={rejectMutation.isPending || acceptMutation.isPending}
                >
                  Принять в посты
                </button>
              </div>
            )}
          </div>
        ))}
        {items.length === 0 && !inboxQuery.isLoading && <div className="empty">Нет предложений.</div>}
      </div>

      {canModerate && items.length > 0 && offset + PAGE_SIZE < total && (
        <div style={{ marginTop: 16 }}>
          <button type="button" className="ghost" onClick={() => setOffset((v) => v + PAGE_SIZE)}>
            Еще
          </button>
        </div>
      )}
    </section>
  );
}

