import { useEffect, useState } from "react";

export default function RejectPostModal({ isOpen, onCancel, onConfirm, isLoading = false }) {
  const [comment, setComment] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (isOpen) {
      setComment("");
      setError("");
    }
  }, [isOpen]);

  function handleConfirm() {
    if (!comment.trim()) {
      setError("Введите комментарий редактора.");
      return;
    }
    onConfirm(comment.trim());
  }

  if (!isOpen) return null;

  return (
    <div className="modal-backdrop" onClick={onCancel}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Отклонить пост</h2>
        <label>
          Комментарий редактора
          <textarea
            value={comment}
            onChange={(e) => {
              setComment(e.target.value);
              if (error) setError("");
            }}
            rows={4}
            required
          />
        </label>
        {error && <div className="error">{error}</div>}
        <div className="actions">
          <button type="button" className="ghost-dark" onClick={onCancel} disabled={isLoading}>
            Отмена
          </button>
          <button type="button" className="primary" onClick={handleConfirm} disabled={isLoading}>
            {isLoading ? "Отправка..." : "Отклонить"}
          </button>
        </div>
      </div>
    </div>
  );
}

