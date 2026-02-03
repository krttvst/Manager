import { previewUrl } from "../api/media.js";

export default function PostPreviewModal({ post, onClose, onEdit }) {
  const preview = previewUrl(post.media_url);
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Предпросмотр</h2>
        <div className="telegram-preview">
          {preview && (
            <img className="preview-image" src={preview} alt="" />
          )}
          <div className="preview-text">
            <div className="preview-title">{post.title}</div>
            <div className="preview-body">{post.body_text}</div>
          </div>
        </div>
        <div className="actions">
          <button type="button" className="ghost-dark" onClick={onClose}>
            Закрыть
          </button>
          <button type="button" className="primary" onClick={onEdit}>
            Изменить
          </button>
        </div>
      </div>
    </div>
  );
}
