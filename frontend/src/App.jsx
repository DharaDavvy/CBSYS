import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import { auth } from "./services/firebase";
import Login from "./components/Auth/Login";
import Wizard from "./components/Onboarding/Wizard";
import Dashboard from "./components/Layout/Dashboard";
import ChatWindow from "./components/Chat/ChatWindow";
import VisualRoadmap from "./components/Roadmap/VisualRoadmap";
import Profile from "./components/Profile/Profile";
import Transcript from "./components/Profile/Transcript";

function ProtectedRoute({ children }) {
  const { currentUser } = useAuth();
  // auth.currentUser is synchronously set the moment Firebase creates/restores
  // a session — even before onAuthStateChanged fires to update React context.
  // This prevents the race condition where a newly-registered user gets
  // bounced to /login because context hasn't updated yet.
  if (!currentUser && !auth.currentUser) return <Navigate to="/login" replace />;
  return children;
}

function PublicRoute({ children }) {
  const { currentUser } = useAuth();
  if (currentUser) {
    // If the user just registered, send them to onboarding
    if (sessionStorage.getItem("needsOnboarding")) {
      return <Navigate to="/onboarding" replace />;
    }
    return <Navigate to="/dashboard" replace />;
  }
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

      {/* Onboarding (requires auth, but accessible right after registration) */}
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
        <Route path="transcript" element={<Transcript />} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
