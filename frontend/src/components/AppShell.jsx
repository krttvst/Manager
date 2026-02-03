import { useState } from "react";
import { Link, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../state/auth.jsx";

export default function AppShell() {
  const { setToken } = useAuth();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);

  function logout() {
    localStorage.removeItem("token");
    document.cookie = "access_token=; Max-Age=0; path=/";
    setToken(null);
    navigate("/login");
  }

  return (
    <div className="shell">
      <aside className={`sidebar ${collapsed ? "collapsed" : ""}`}>
        <div className="brand-row">
          {!collapsed && <div className="brand">Manager</div>}
          <button
            type="button"
            className={`icon-button ghost ${collapsed ? "sidebar-toggle-collapsed" : ""}`}
            onClick={() => setCollapsed((prev) => !prev)}
            aria-label={collapsed ? "Развернуть меню" : "Свернуть меню"}
          >
            {collapsed ? "»" : "«"}
          </button>
        </div>
        {!collapsed && (
          <>
            <nav className="nav">
              <Link to="/telegram">
                <span className="nav-label">Telegram</span>
              </Link>
              <Link to="/youtube">
                <span className="nav-label">YouTube</span>
              </Link>
              <Link to="/vk">
                <span className="nav-label">VK</span>
              </Link>
              <Link to="/zen">
                <span className="nav-label">Дзен</span>
              </Link>
            </nav>
            <button className="ghost" onClick={logout}>
              <span className="nav-label">Выйти</span>
            </button>
          </>
        )}
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
