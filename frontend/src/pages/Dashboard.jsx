import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../state/auth.jsx";
import CreateChannelModal from "./CreateChannelModal.jsx";
import { useChannelsQuery } from "../hooks/useChannelsQuery.js";
import { useDashboardOverviewQuery } from "../hooks/useDashboardOverviewQuery.js";
import { formatDateTime } from "../utils/date.js";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { requeuePost } from "../api/schedule.js";

export default function Dashboard() {
  const { token } = useAuth();
  const { user } = useAuth();
  const [showModal, setShowModal] = useState(false);
  const { channels, isLoading, error, addChannel } = useChannelsQuery(token);
  const { overview } = useDashboardOverviewQuery(token);
  const errorMessage = error?.message || "";
  const channelMeta = new Map((overview?.channels ?? []).map((row) => [row.channel_id, row]));
  const totalCounts = overview?.total_status_counts ?? {};
  const upcoming = overview?.upcoming ?? [];
  const recentErrors = overview?.recent_errors ?? [];
  const canRequeue = user?.role === "admin" || user?.role === "editor";
  const qc = useQueryClient();

  const requeueMutation = useMutation({
    mutationFn: (postId) => requeuePost(token, postId, { delay_seconds: 0 }),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["dashboard"] });
    }
  });

  return (
    <section>
      <div className="page-header">
        <h1>Каналы</h1>
        <button className="primary" onClick={() => setShowModal(true)}>
          Добавить канал
        </button>
      </div>
      <div className="badge-row" style={{ marginTop: 16 }}>
        <span className="badge status-draft">Draft: {totalCounts.draft ?? 0}</span>
        <span className="badge status-pending">Pending: {totalCounts.pending ?? 0}</span>
        <span className="badge status-approved">Approved: {totalCounts.approved ?? 0}</span>
        <span className="badge status-scheduled">Scheduled: {totalCounts.scheduled ?? 0}</span>
        <span className="badge status-published">Published: {totalCounts.published ?? 0}</span>
        <span className="badge status-failed">Failed: {totalCounts.failed ?? 0}</span>
      </div>
      {isLoading && <div className="hint">Загрузка...</div>}
      {errorMessage && <div className="error">{errorMessage}</div>}
      <div className="grid">
        {channels.map((ch) => (
          <Link key={ch.id} to={`/channels/${ch.id}`} className="card">
            {(() => {
              const meta = channelMeta.get(ch.id);
              const nextAt = meta?.next_scheduled_at ?? null;
              const overdue = meta?.overdue_scheduled_count ?? 0;
              const lastPub = meta?.last_published_at ?? null;
              const lastPost = meta?.last_post_at ?? null;
              const counts = meta?.status_counts ?? {};
              return (
                <>
                  <div className="card-header">
                    {ch.avatar_url && <img className="channel-avatar" src={ch.avatar_url} alt="" loading="lazy" />}
                    <h3>{ch.title}</h3>
                  </div>
                  <p className="muted">{ch.telegram_channel_identifier}</p>
                  <div className="mini">
                    Следующая публикация: {formatDateTime(nextAt)} {overdue > 0 ? `(просрочено: ${overdue})` : ""}
                  </div>
                  <div className="mini">Последний опубликованный: {formatDateTime(lastPub)}</div>
                  <div className="mini">Последний пост: {formatDateTime(lastPost)}</div>
                  <div className="badge-row" style={{ marginTop: 8, marginBottom: 0 }}>
                    <span className="badge status-draft">D {counts.draft ?? 0}</span>
                    <span className="badge status-pending">P {counts.pending ?? 0}</span>
                    <span className="badge status-approved">A {counts.approved ?? 0}</span>
                    <span className="badge status-scheduled">S {counts.scheduled ?? 0}</span>
                  </div>
                </>
              );
            })()}
          </Link>
        ))}
        {channels.length === 0 && <div className="empty">Пока нет подключённых каналов.</div>}
      </div>

      <div className="grid-section" style={{ marginTop: 26 }}>
        <div className="card">
          <h3 style={{ margin: 0 }}>Ближайшие публикации</h3>
          {upcoming.length === 0 && <div className="mini" style={{ marginTop: 8 }}>—</div>}
          {upcoming.map((u) => (
            <div key={u.post_id} className="channel-preview" style={{ marginTop: 10, justifyContent: "space-between" }}>
              <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
                <strong>{u.channel_title || `channel:${u.channel_id}`}</strong>
                <div className="muted">{u.title}</div>
              </div>
              <div className="mini">{formatDateTime(u.scheduled_at)}</div>
            </div>
          ))}
        </div>

        <div className="card">
          <h3 style={{ margin: 0 }}>Последние ошибки</h3>
          {recentErrors.length === 0 && <div className="mini" style={{ marginTop: 8 }}>—</div>}
          {recentErrors.map((e) => (
            <div key={e.post_id} className="channel-preview" style={{ marginTop: 10, justifyContent: "space-between" }}>
              <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
                <strong>{e.channel_title || `channel:${e.channel_id}`}</strong>
                <div className="muted">{e.title}</div>
                <div className="mini">{e.last_error}</div>
              </div>
              <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 8 }}>
                <div className="mini">{formatDateTime(e.updated_at)}</div>
                {canRequeue && (
                  <button
                    type="button"
                    className="ghost"
                    onClick={(ev) => {
                      ev.preventDefault();
                      requeueMutation.mutate(e.post_id);
                    }}
                    disabled={requeueMutation.isPending}
                  >
                    {requeueMutation.isPending ? "..." : "Requeue"}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
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
