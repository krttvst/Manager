import { previewUrl } from "../../api/media.js";
import { formatDateTime } from "../../utils/date.js";

export default function PostsGridSection({
  title,
  posts,
  emptyText,
  onOpen,
  getMeta,
  getTime,
  showLoadMore,
  onLoadMore,
  isLoadingMore
}) {
  return (
    <div className="grid-section">
      <h2>{title}</h2>
      <div className="post-grid">
        {posts.map((post) => (
          <div key={post.id} className="post-card" onClick={() => onOpen(post)}>
            {post.media_url && <img className="post-card-image" src={previewUrl(post.media_url)} alt="" loading="lazy" />}
            <div className="post-card-body">
              <div className="post-card-title">{post.title}</div>
              <div className="post-card-meta">{getMeta(post)}</div>
              <div className="post-card-time">Публикация: {formatDateTime(getTime(post))}</div>
            </div>
          </div>
        ))}
        {posts.length === 0 && <div className="empty">{emptyText}</div>}
      </div>
      {showLoadMore && (
        <div className="actions">
          <button className="ghost-dark" onClick={onLoadMore} disabled={isLoadingMore}>
            {isLoadingMore ? "Загрузка..." : "Показать еще"}
          </button>
        </div>
      )}
    </div>
  );
}

