import { useState } from "react";
import { previewUrl } from "../api/media.js";

export default function PostPreviewModal({ post, onClose, onEdit, onDelete, isDeleting = false }) {
  const preview = previewUrl(post.media_url);
  const [menuOpen, setMenuOpen] = useState(false);
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div />
          <div className="menu">
            <button
              type="button"
              className="icon-button"
              onClick={() => setMenuOpen((prev) => !prev)}
              aria-label="Открыть меню"
            >
              ⋯
            </button>
            {menuOpen && (
              <div className="menu-panel" onClick={(e) => e.stopPropagation()}>
                <button type="button" className="menu-item" onClick={onEdit}>
                  Редактировать
                </button>
                <button type="button" className="menu-item" onClick={onDelete} disabled={isDeleting}>
                  {isDeleting ? "Удаление..." : "Удалить"}
                </button>
                <button type="button" className="menu-item" onClick={onClose}>
                  Закрыть
                </button>
              </div>
            )}
          </div>
        </div>
        <div className="telegram-preview telegram-preview-modern">
          {preview && (
            <img className="preview-image" src={preview} alt="" />
          )}
          <div className="preview-text preview-bubble">
            <div className="preview-title">{post.title}</div>
            <div className="preview-body">{post.body_text}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
