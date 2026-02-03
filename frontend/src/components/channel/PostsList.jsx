import { previewUrl } from "../../api/media.js";
import { formatDateTime } from "../../utils/date.js";

export default function PostsList({
  posts,
  onOpen,
  onSubmitApproval,
  onApprove,
  onReject,
  onSchedule,
  onPublishNow,
  onDelete,
  canCreatePost,
  canApprove,
  statusLabels,
  isSubmitting,
  isApproving,
  isRejecting,
  isScheduling,
  isPublishing,
  isDeleting
}) {
  return (
    <div className="list">
      {posts.map((post) => (
        <div
          key={post.id}
          className={`list-item ${["draft", "pending", "approved", "scheduled"].includes(post.status) ? "clickable" : ""}`}
          onClick={() => onOpen(post)}
        >
          <div className="post-main">
            {post.media_url && <img className="thumb" src={previewUrl(post.media_url)} alt="" loading="lazy" />}
            <h3>{post.title}</h3>
            <p className="muted">{post.body_excerpt}</p>
            {post.editor_comment && <p className="note">Комментарий: {post.editor_comment}</p>}
            {post.last_error && <p className="note error">Ошибка: {post.last_error}</p>}
          </div>
          <div className="post-meta">
            <div className={`status ${post.status}`}>{statusLabels[post.status] || post.status}</div>
            <div className="note">Публикация: {formatDateTime(post.published_at || post.scheduled_at)}</div>
            {post.status !== "published" && (
              <div className="note">Последнее редактирование: {formatDateTime(post.updated_at)}</div>
            )}
            <div className="actions-inline">
              {(post.status === "draft" || post.status === "rejected") && canCreatePost && (
                <button
                  className="tiny"
                  disabled={isSubmitting}
                  onClick={(e) => {
                    e.stopPropagation();
                    onSubmitApproval(post.id);
                  }}
                >
                  На согласование
                </button>
              )}
              {post.status === "pending" && canApprove && (
                <>
                <button
                  className="tiny"
                  disabled={isApproving}
                  onClick={(e) => {
                    e.stopPropagation();
                    onApprove(post.id);
                  }}
                >
                  Одобрить
                </button>
                <button
                  className="tiny"
                  disabled={isRejecting}
                  onClick={(e) => {
                    e.stopPropagation();
                    onReject(post.id);
                  }}
                >
                  Отклонить
                </button>
              </>
            )}
            {post.status === "approved" && canApprove && (
              <>
                  <button
                    className="tiny"
                    disabled={isScheduling}
                  onClick={(e) => {
                    e.stopPropagation();
                    onSchedule(post.id);
                  }}
                >
                  Запланировать
                </button>
                <button
                  className="tiny"
                  disabled={isPublishing}
                  onClick={(e) => {
                    e.stopPropagation();
                    onPublishNow(post.id);
                  }}
                >
                  Опубликовать сразу
                </button>
              </>
            )}
              <button
                className="tiny"
                disabled={isDeleting}
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(post.id);
                }}
              >
                Удалить
              </button>
            </div>
          </div>
        </div>
      ))}
      {posts.length === 0 && <div className="empty">Постов пока нет.</div>}
    </div>
  );
}
