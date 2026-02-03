import { Link, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../state/auth.jsx";

export default function AppShell() {
  const { setToken } = useAuth();
  const navigate = useNavigate();

  function logout() {
    localStorage.removeItem("token");
    document.cookie = "access_token=; Max-Age=0; path=/";
    setToken(null);
    navigate("/login");
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">Manager TG</div>
        <nav className="nav">
          <Link to="/telegram">Telegram</Link>
          <Link to="/youtube">YouTube</Link>
          <Link to="/vk">VK</Link>
          <Link to="/zen">Дзен</Link>
        </nav>
        <button className="ghost" onClick={logout}>
          Выйти
        </button>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
