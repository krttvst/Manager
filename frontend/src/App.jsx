import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login.jsx";
import Telegram from "./pages/Telegram.jsx";
import Placeholder from "./pages/Placeholder.jsx";
import Channel from "./pages/Channel.jsx";
import AgentSettings from "./pages/AgentSettings.jsx";
import AppShell from "./components/AppShell.jsx";
import { AuthProvider, useAuth } from "./state/auth.jsx";

function ProtectedRoute({ children }) {
  const { token } = useAuth();
  if (!token) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <AppShell />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/telegram" replace />} />
            <Route path="telegram" element={<Telegram />} />
            <Route path="youtube" element={<Placeholder title="YouTube" />} />
            <Route path="vk" element={<Placeholder title="VK" />} />
            <Route path="zen" element={<Placeholder title="Дзен" />} />
            <Route path="channels/:id" element={<Channel />} />
            <Route path="channels/:id/agent-settings" element={<AgentSettings />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
