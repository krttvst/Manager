import { previewUrl } from "../../api/media.js";
import { formatDateTime } from "../../utils/date.js";

export default function PostsGridList({
  posts,
  onOpen,
  statusLabels,
}) {
  return (
    <div className="post-grid">
      {posts.map((post) => (
        <div
          key={post.id}
          className={`post-card ${["draft", "pending", "approved", "scheduled"].includes(post.status) ? "clickable" : ""}`}
          onClick={() => onOpen(post)}
        >
          <div className={`post-card-status ${post.status}`}>
            {statusLabels[post.status] || post.status}
          </div>
          {post.media_url && <img className="post-card-image" src={previewUrl(post.media_url)} alt="" loading="lazy" />}
          <div className="post-card-title">{post.title}</div>
          {post.body_excerpt && <div className="post-card-excerpt">{post.body_excerpt}</div>}
          <div className="post-card-divider" />
          {post.status === "published" ? (
            <div className="post-card-time">
              Дата публикации: {formatDateTime(post.published_at || post.scheduled_at)}
            </div>
          ) : (
            <div className="post-card-time">
              Дата последнего изменения: {formatDateTime(post.updated_at)}
            </div>
          )}
          {post.status === "published" && (
            <div className="post-card-time">
              Просмотры: {post.last_known_views ?? "—"}
            </div>
          )}
        </div>
      ))}
      {posts.length === 0 && <div className="empty">Постов пока нет.</div>}
    </div>
  );
}
