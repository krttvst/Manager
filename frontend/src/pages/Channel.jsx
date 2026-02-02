import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { useAuth } from "../state/auth.jsx";
import { apiFetch } from "../state/api.js";
import CreatePostModal from "./CreatePostModal.jsx";
import AiGenerateModal from "./AiGenerateModal.jsx";

const STATUSES = ["draft", "pending", "approved", "scheduled", "published", "rejected", "failed"];

export default function Channel() {
  const { id } = useParams();
  const { token, user } = useAuth();
  const [channel, setChannel] = useState(null);
  const [posts, setPosts] = useState([]);
  const [activeTab, setActiveTab] = useState("queue");
  const [statusFilter, setStatusFilter] = useState("");
  const [error, setError] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [showAi, setShowAi] = useState(false);
  const [stats, setStats] = useState(null);

  const canCreatePost = user?.role !== "viewer";
  const canApprove = user?.role === "editor" || user?.role === "admin";

  async function loadChannel() {
    try {
      const data = await apiFetch(`/channels/${id}`, { token });
      setChannel(data);
    } catch (err) {
      setError(err.message);
    }
  }

  async function loadPosts() {
    try {
      const url = statusFilter
        ? `/channels/${id}/posts?status_filter=${statusFilter}`
        : `/channels/${id}/posts`;
      const data = await apiFetch(url, { token });
      setPosts(data);
    } catch (err) {
      setError(err.message);
    }
  }

  async function loadStats() {
    try {
      const data = await apiFetch(`/channels/${id}/stats`, { token });
      setStats(data);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    loadChannel();
  }, [id, token]);

  useEffect(() => {
    if (activeTab === "queue") loadPosts();
    if (activeTab === "stats") loadStats();
  }, [id, token, activeTab, statusFilter]);

  const badges = useMemo(
    () =>
      STATUSES.map((st) => (
        <button
          key={st}
          className={statusFilter === st ? "badge active" : "badge"}
          onClick={() => setStatusFilter(statusFilter === st ? "" : st)}
        >
          {st}
        </button>
      )),
    [statusFilter]
  );

  async function submitApproval(postId) {
    await apiFetch(`/posts/${postId}/submit-approval`, { method: "POST", token });
    loadPosts();
  }

  async function approve(postId) {
    await apiFetch(`/posts/${postId}/approve`, { method: "POST", token });
    loadPosts();
  }

  async function reject(postId) {
    const comment = prompt("Комментарий редактора");
    if (!comment) return;
    await apiFetch(`/posts/${postId}/reject`, { method: "POST", token, body: { comment } });
    loadPosts();
  }

  async function schedule(postId) {
    const when = prompt("Дата и время (YYYY-MM-DD HH:MM)");
    if (!when) return;
    const iso = new Date(when.replace(" ", "T")).toISOString();
    await apiFetch(`/posts/${postId}/schedule`, { method: "POST", token, body: { scheduled_at: iso } });
    loadPosts();
  }

  async function publishNow(postId) {
    await apiFetch(`/posts/${postId}/publish-now`, { method: "POST", token });
    loadPosts();
  }

  return (
    <section>
      <div className="page-header">
        <div>
          <h1>{channel?.title || "Канал"}</h1>
          <p className="muted">{channel?.telegram_channel_identifier}</p>
        </div>
        <div className="actions-inline">
          {canCreatePost && (
            <>
              <button className="ghost-dark" onClick={() => setShowAi(true)}>
                AI из URL
              </button>
              <button className="primary" onClick={() => setShowCreate(true)}>
                Создать пост
              </button>
            </>
          )}
        </div>
      </div>

      <div className="tabs">
        <button className={activeTab === "queue" ? "tab active" : "tab"} onClick={() => setActiveTab("queue")}>
          Очередь
        </button>
        <button className={activeTab === "stats" ? "tab active" : "tab"} onClick={() => setActiveTab("stats")}>
          Статистика
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {activeTab === "queue" && (
        <div>
          <div className="badge-row">{badges}</div>
          <div className="list">
            {posts.map((post) => (
              <div key={post.id} className="list-item">
                <div>
                  <h3>{post.title}</h3>
                  <p className="muted">{post.body_text.slice(0, 120)}...</p>
                  {post.editor_comment && <p className="note">Комментарий: {post.editor_comment}</p>}
                  {post.last_error && <p className="note error">Ошибка: {post.last_error}</p>}
                </div>
                <div className="post-meta">
                  <div className={`status ${post.status}`}>{post.status}</div>
                  <div className="actions-inline">
                    {(post.status === "draft" || post.status === "rejected") && canCreatePost && (
                      <button className="tiny" onClick={() => submitApproval(post.id)}>
                        На согласование
                      </button>
                    )}
                    {post.status === "pending" && canApprove && (
                      <>
                        <button className="tiny" onClick={() => approve(post.id)}>
                          Approve
                        </button>
                        <button className="tiny" onClick={() => reject(post.id)}>
                          Reject
                        </button>
                      </>
                    )}
                    {post.status === "approved" && canApprove && (
                      <>
                        <button className="tiny" onClick={() => schedule(post.id)}>
                          Schedule
                        </button>
                        <button className="tiny" onClick={() => publishNow(post.id)}>
                          Publish now
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}
            {posts.length === 0 && <div className="empty">Постов пока нет.</div>}
          </div>
        </div>
      )}

      {activeTab === "stats" && (
        <div className="stats">
          <div className="stat-card">
            <div className="label">Views доступно</div>
            <div className="value">{stats?.views_available ? "Да" : "Нет"}</div>
          </div>
          <div className="stat-card">
            <div className="label">Средние просмотры</div>
            <div className="value">{stats?.avg_views_last_n ?? "—"}</div>
          </div>
          <div className="stat-card">
            <div className="label">Подписчики</div>
            <div className="value">{stats?.subscribers ?? "—"}</div>
          </div>
        </div>
      )}

      {showCreate && (
        <CreatePostModal
          channelId={id}
          onClose={() => setShowCreate(false)}
          onCreated={(post) => setPosts((prev) => [post, ...prev])}
        />
      )}
      {showAi && (
        <AiGenerateModal
          channelId={id}
          onClose={() => setShowAi(false)}
          onCreated={loadPosts}
        />
      )}
    </section>
  );
}
