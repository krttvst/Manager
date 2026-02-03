export default function ConfirmModal({
  isOpen,
  title,
  message,
  confirmLabel = "Подтвердить",
  cancelLabel = "Отмена",
  onConfirm,
  onCancel,
  isLoading = false
}) {
  if (!isOpen) return null;

  return (
    <div className="modal-backdrop" onClick={onCancel}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>{title}</h2>
        {message && <p className="muted">{message}</p>}
        <div className="actions">
          <button type="button" className="ghost-dark" onClick={onCancel} disabled={isLoading}>
            {cancelLabel}
          </button>
          <button type="button" className="primary" onClick={onConfirm} disabled={isLoading}>
            {isLoading ? "Подождите..." : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

