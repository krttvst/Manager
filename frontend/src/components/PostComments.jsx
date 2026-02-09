import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "../state/auth.jsx";
import { createPostComment, listPostComments } from "../api/comments.js";
import { formatDateTime } from "../utils/date.js";

function kindLabel(kind) {
  if (kind === "reject") return "Отклонение";
  if (kind === "system") return "Система";
  return "Комментарий";
}

export default function PostComments({ postId }) {
  const { token } = useAuth();
  const qc = useQueryClient();
  const [text, setText] = useState("");
  const key = useMemo(() => ["post-comments", { postId }], [postId]);

  const query = useQuery({
    queryKey: key,
    queryFn: () => listPostComments(token, postId),
    enabled: Boolean(token && postId)
  });

  const createMutation = useMutation({
    mutationFn: async () => {
      const body = text.trim();
      if (!body) throw new Error("Пустой комментарий");
      return await createPostComment(token, postId, body);
    },
    onSuccess: async () => {
      setText("");
      await qc.invalidateQueries({ queryKey: key });
    }
  });

  const items = query.data ?? [];

  return (
    <div style={{ marginTop: 14 }}>
      <div className="page-header" style={{ alignItems: "baseline" }}>
        <h3 style={{ margin: 0 }}>Комментарии</h3>
        <div className="mini">{items.length}</div>
      </div>
      {query.isLoading && <div className="hint">Загрузка...</div>}
      {query.error && <div className="error">{query.error.message}</div>}
      {items.length === 0 && !query.isLoading && <div className="empty">Пока нет комментариев.</div>}
      {items.map((c) => (
        <div key={c.id} className="card" style={{ marginTop: 10, padding: 14 }}>
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "baseline" }}>
            <span className="badge">{kindLabel(c.kind)}</span>
            <span className="muted">{c.author_email || `user:${c.author_user_id}`}</span>
            <span className="mini">{formatDateTime(c.created_at)}</span>
          </div>
          <div style={{ marginTop: 8, whiteSpace: "pre-wrap" }}>{c.body_text}</div>
        </div>
      ))}

      <div className="card" style={{ marginTop: 12, padding: 14 }}>
        <label style={{ display: "block" }}>
          <div className="muted" style={{ marginBottom: 6 }}>Новый комментарий</div>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={3}
            placeholder="Напишите комментарий..."
          />
        </label>
        {createMutation.error && <div className="error">{createMutation.error.message}</div>}
        <div className="actions" style={{ marginTop: 10 }}>
          <button
            type="button"
            className="primary"
            onClick={() => createMutation.mutate()}
            disabled={createMutation.isPending || !text.trim()}
          >
            {createMutation.isPending ? "Отправка..." : "Отправить"}
          </button>
        </div>
      </div>
    </div>
  );
}

