import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import Login from "./components/Auth/Login";
import Wizard from "./components/Onboarding/Wizard";
import Dashboard from "./components/Layout/Dashboard";
import ChatWindow from "./components/Chat/ChatWindow";
import VisualRoadmap from "./components/Roadmap/VisualRoadmap";
import Profile from "./components/Profile/Profile";

function ProtectedRoute({ children }) {
  const { currentUser } = useAuth();
  if (!currentUser) return <Navigate to="/login" replace />;
  return children;
}

function PublicRoute({ children }) {
  const { currentUser } = useAuth();
  if (currentUser) return <Navigate to="/dashboard" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      {/* Public */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        }
      />

      {/* Onboarding (requires auth) */}
      <Route
        path="/onboarding"
        element={
          <ProtectedRoute>
            <Wizard />
          </ProtectedRoute>
        }
      />

      {/* Dashboard (requires auth) */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      >
        <Route index element={<ChatWindow />} />
        <Route path="roadmap" element={<VisualRoadmap />} />
        <Route path="profile" element={<Profile />} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
