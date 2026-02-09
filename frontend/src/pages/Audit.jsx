import { useMemo, useState } from "react";
import { useAuth } from "../state/auth.jsx";
import { useAuditLogsQuery } from "../hooks/useAuditLogsQuery.js";
import { formatDateTime } from "../utils/date.js";

const DEFAULT_LIMIT = 50;

function safeJson(value) {
  try {
    return JSON.stringify(value);
  } catch {
    return String(value ?? "");
  }
}

export default function Audit() {
  const { token, user } = useAuth();
  const [entityType, setEntityType] = useState("");
  const [entityId, setEntityId] = useState("");
  const [action, setAction] = useState("");
  const [offset, setOffset] = useState(0);

  const params = useMemo(
    () => ({
      limit: DEFAULT_LIMIT,
      offset,
      entity_type: entityType || undefined,
      entity_id: entityId ? Number(entityId) : undefined,
      action: action || undefined
    }),
    [entityType, entityId, action, offset]
  );

  const query = useAuditLogsQuery(token, params);
  const data = query.data;
  const items = data?.items ?? [];
  const total = data?.total ?? 0;

  const isAdmin = user?.role === "admin";

  return (
    <section>
      <div className="page-header">
        <h1>Аудит</h1>
      </div>

      {!isAdmin && <div className="hint">Доступно только администратору.</div>}

      <div className="card" style={{ marginTop: 16 }}>
        <div className="actions-inline">
          <label>
            Тип
            <select value={entityType} onChange={(e) => setEntityType(e.target.value)}>
              <option value="">Все</option>
              <option value="post">post</option>
              <option value="channel">channel</option>
              <option value="suggestion">suggestion</option>
            </select>
          </label>
          <label>
            ID
            <input value={entityId} onChange={(e) => setEntityId(e.target.value)} placeholder="например 123" />
          </label>
          <label>
            Action
            <input value={action} onChange={(e) => setAction(e.target.value)} placeholder="например create" />
          </label>
          <button
            type="button"
            className="ghost"
            onClick={() => {
              setOffset(0);
              query.refetch();
            }}
          >
            Применить
          </button>
        </div>
        <div className="mini" style={{ marginTop: 10 }}>
          Всего: {total}. Показано: {items.length}. Offset: {offset}.
        </div>
      </div>

      {query.isLoading && <div className="hint" style={{ marginTop: 12 }}>Загрузка...</div>}
      {query.error && <div className="error" style={{ marginTop: 12 }}>{query.error.message}</div>}

      <div className="grid-section" style={{ marginTop: 18 }}>
        {items.map((it) => (
          <div key={it.id} className="card">
            <div className="mini">{formatDateTime(it.created_at)}</div>
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "baseline" }}>
              <strong>{it.entity_type}:{it.entity_id}</strong>
              <span className="badge">{it.action}</span>
              <span className="muted">actor: {it.actor_email || it.actor_user_id}</span>
            </div>
            <pre className="codeblock">{safeJson(it.payload_json)}</pre>
          </div>
        ))}
        {items.length === 0 && !query.isLoading && <div className="empty">Нет записей.</div>}
      </div>

      {isAdmin && items.length > 0 && offset + DEFAULT_LIMIT < total && (
        <div style={{ marginTop: 16 }}>
          <button type="button" className="ghost" onClick={() => setOffset((v) => v + DEFAULT_LIMIT)}>
            Еще
          </button>
        </div>
      )}
    </section>
  );
}

