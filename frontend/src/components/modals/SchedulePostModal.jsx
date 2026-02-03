import { useEffect, useState } from "react";
import { formatDateTimeLocal } from "../../utils/date.js";

export default function SchedulePostModal({ isOpen, onCancel, onConfirm, isLoading = false }) {
  const [scheduledAt, setScheduledAt] = useState("");
  const [error, setError] = useState("");
  const [tzHint, setTzHint] = useState("");

  useEffect(() => {
    if (isOpen) {
      setScheduledAt("");
      setError("");
      setTzHint("");
    }
  }, [isOpen]);

  function handleConfirm() {
    if (!scheduledAt) {
      setError("Выберите дату и время публикации.");
      return;
    }
    const selected = new Date(scheduledAt);
    if (Number.isNaN(selected.getTime()) || selected <= new Date()) {
      setError("Дата и время должны быть в будущем.");
      return;
    }
    onConfirm(selected.toISOString());
  }

  if (!isOpen) return null;

  return (
    <div className="modal-backdrop" onClick={onCancel}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Запланировать публикацию</h2>
        <label>
          Дата и время публикации
          <input
            type="datetime-local"
            value={scheduledAt}
            onChange={(e) => {
              setScheduledAt(e.target.value);
              if (!tzHint) {
                const offset = -new Date().getTimezoneOffset() / 60;
                setTzHint(`Время по вашему часовому поясу (UTC${offset >= 0 ? "+" : ""}${offset}).`);
              }
              if (error) setError("");
            }}
            min={formatDateTimeLocal(new Date())}
          />
        </label>
        {tzHint && <div className="hint">{tzHint}</div>}
        {error && <div className="error">{error}</div>}
        <div className="actions">
          <button type="button" className="ghost-dark" onClick={onCancel} disabled={isLoading}>
            Отмена
          </button>
          <button type="button" className="primary" onClick={handleConfirm} disabled={isLoading}>
            {isLoading ? "Сохраняем..." : "Добавить в очередь"}
          </button>
        </div>
      </div>
    </div>
  );
}

