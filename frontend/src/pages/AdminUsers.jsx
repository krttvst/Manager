import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "../state/auth.jsx";
import { createUser, listUsers, resetUserPassword, setUserActive, setUserPassword, updateUserRole } from "../api/users.js";
import { formatDateTime } from "../utils/date.js";

const PAGE_SIZE = 50;
const ROLES = ["admin", "editor", "author", "viewer"];

export default function AdminUsers() {
  const { token, user } = useAuth();
  const qc = useQueryClient();
  const isAdmin = user?.role === "admin";

  const [q, setQ] = useState("");
  const [offset, setOffset] = useState(0);

  const params = useMemo(() => ({ limit: PAGE_SIZE, offset, q: q || undefined }), [offset, q]);
  const queryKey = ["admin-users", params];

  const usersQuery = useQuery({
    queryKey,
    queryFn: () => listUsers(token, params),
    enabled: Boolean(token && isAdmin)
  });

  const data = usersQuery.data;
  const items = data?.items ?? [];
  const total = data?.total ?? 0;

  const [newEmail, setNewEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newRole, setNewRole] = useState("author");

  const createMutation = useMutation({
    mutationFn: () => createUser(token, { email: newEmail, password: newPassword, role: newRole }),
    onSuccess: async () => {
      setNewEmail("");
      setNewPassword("");
      setNewRole("author");
      await qc.invalidateQueries({ queryKey: ["admin-users"] });
    }
  });

  const roleMutation = useMutation({
    mutationFn: ({ userId, role }) => updateUserRole(token, userId, role),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["admin-users"] });
    }
  });

  const passwordMutation = useMutation({
    mutationFn: ({ userId, password }) => setUserPassword(token, userId, password),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["admin-users"] });
    }
  });

  const activeMutation = useMutation({
    mutationFn: ({ userId, isActive }) => setUserActive(token, userId, isActive),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["admin-users"] });
    }
  });

  const resetMutation = useMutation({
    mutationFn: async (userId) => {
      const res = await resetUserPassword(token, userId);
      return res.temporary_password;
    }
  });

  const [pwDraft, setPwDraft] = useState({});
  const [resetShown, setResetShown] = useState(null);

  if (!isAdmin) {
    return (
      <section>
        <div className="page-header">
          <h1>Пользователи</h1>
        </div>
        <div className="hint">Доступно только администратору.</div>
      </section>
    );
  }

  return (
    <section>
      <div className="page-header">
        <h1>Пользователи</h1>
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <h3 style={{ margin: 0 }}>Создать пользователя</h3>
        <div className="actions-inline" style={{ marginTop: 12 }}>
          <label style={{ flex: 1 }}>
            Email
            <input value={newEmail} onChange={(e) => setNewEmail(e.target.value)} placeholder="user@example.com" />
          </label>
          <label style={{ flex: 1 }}>
            Пароль
            <input value={newPassword} onChange={(e) => setNewPassword(e.target.value)} type="password" />
          </label>
          <label>
            Роль
            <select value={newRole} onChange={(e) => setNewRole(e.target.value)}>
              {ROLES.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </label>
          <button
            type="button"
            className="primary"
            onClick={() => createMutation.mutate()}
            disabled={createMutation.isPending || !newEmail || !newPassword}
          >
            {createMutation.isPending ? "Создание..." : "Создать"}
          </button>
        </div>
        {createMutation.error && <div className="error" style={{ marginTop: 10 }}>{createMutation.error.message}</div>}
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <div className="actions-inline">
          <label style={{ flex: 1 }}>
            Поиск
            <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="email" />
          </label>
          <button type="button" className="ghost" onClick={() => { setOffset(0); usersQuery.refetch(); }}>
            Применить
          </button>
        </div>
        <div className="mini" style={{ marginTop: 10 }}>
          Всего: {total}. Показано: {items.length}. Offset: {offset}.
        </div>
      </div>

      {usersQuery.isLoading && <div className="hint" style={{ marginTop: 12 }}>Загрузка...</div>}
      {usersQuery.error && <div className="error" style={{ marginTop: 12 }}>{usersQuery.error.message}</div>}

      <div className="card" style={{ marginTop: 16 }}>
        <div className="table">
          <div className="row header">
            <div>ID</div>
            <div>Email</div>
            <div>Role</div>
            <div>Active</div>
            <div>Created</div>
            <div>Пароль</div>
          </div>
          {items.map((u) => (
            <div key={u.id} className="row">
              <div className="mono">{u.id}</div>
              <div>{u.email}</div>
              <div>
                <select
                  value={u.role}
                  onChange={(e) => roleMutation.mutate({ userId: u.id, role: e.target.value })}
                  disabled={roleMutation.isPending}
                >
                  {ROLES.map((r) => (
                    <option key={r} value={r}>
                      {r}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <input
                    type="checkbox"
                    checked={Boolean(u.is_active)}
                    onChange={(e) => activeMutation.mutate({ userId: u.id, isActive: e.target.checked })}
                    disabled={activeMutation.isPending}
                  />
                  <span className="mini">{u.is_active ? "on" : "off"}</span>
                </label>
              </div>
              <div className="mini">{formatDateTime(u.created_at)}</div>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                <input
                  type="password"
                  placeholder="new password"
                  value={pwDraft[u.id] ?? ""}
                  onChange={(e) => setPwDraft((prev) => ({ ...prev, [u.id]: e.target.value }))}
                />
                <button
                  type="button"
                  className="ghost"
                  onClick={() => passwordMutation.mutate({ userId: u.id, password: pwDraft[u.id] ?? "" })}
                  disabled={passwordMutation.isPending || !(pwDraft[u.id] ?? "").trim()}
                >
                  Set
                </button>
                <button
                  type="button"
                  className="ghost"
                  onClick={async () => {
                    const temp = await resetMutation.mutateAsync(u.id);
                    setResetShown({ email: u.email, password: temp });
                  }}
                  disabled={resetMutation.isPending}
                  title="Сгенерировать временный пароль"
                >
                  Reset
                </button>
              </div>
            </div>
          ))}
        </div>

        {items.length === 0 && !usersQuery.isLoading && <div className="empty">Нет пользователей.</div>}
      </div>

      {items.length > 0 && offset + PAGE_SIZE < total && (
        <div style={{ marginTop: 16 }}>
          <button type="button" className="ghost" onClick={() => setOffset((v) => v + PAGE_SIZE)}>
            Еще
          </button>
        </div>
      )}

      {resetShown && (
        <div className="modal-backdrop" onClick={() => setResetShown(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Временный пароль</h2>
            <div className="mini">Показан один раз. Сохраните и передайте пользователю.</div>
            <div className="card" style={{ marginTop: 12 }}>
              <div className="muted">Email</div>
              <div style={{ fontWeight: 600 }}>{resetShown.email}</div>
              <div className="muted" style={{ marginTop: 10 }}>Password</div>
              <pre className="codeblock">{resetShown.password}</pre>
            </div>
            <div className="actions" style={{ marginTop: 12 }}>
              <button type="button" className="primary" onClick={() => setResetShown(null)}>
                Закрыть
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
