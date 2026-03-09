import axios from "axios";
import { onAuthStateChanged } from "firebase/auth";
import { auth } from "./firebase";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
});

/**
 * Return the current Firebase user, waiting for auth state if needed.
 * If auth.currentUser is already set (fast path), return immediately.
 * Otherwise subscribe to onAuthStateChanged and wait for the first event.
 */
function getAuthUser() {
  if (auth.currentUser) return Promise.resolve(auth.currentUser);
  return new Promise((resolve) => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      unsubscribe();
      resolve(user);          // null = genuinely signed-out
    });
  });
}

// Attach a fresh Firebase ID token to every request
api.interceptors.request.use(async (config) => {
  try {
    const user = await getAuthUser();
    if (user) {
      const token = await user.getIdToken(true); // force-refresh if expired
      config.headers.Authorization = `Bearer ${token}`;
    }
  } catch (err) {
    console.warn("[API] Could not get ID token:", err.message);
  }
  return config;
});

// ── Chat ────────────────────────────────────────────────────────────

export async function sendMessage(message) {
  const { data } = await api.post("/chat", { message });
  return data; // { response, sources }
}

// ── Roadmap ─────────────────────────────────────────────────────────

export async function generateRoadmap({ level, interests, completedCourses }) {
  const { data } = await api.post("/generate-roadmap", {
    level,
    interests,
    completed_courses: completedCourses || [],
  });
  return data; // { roadmap, sources }
}

// ── User ────────────────────────────────────────────────────────────

export async function saveUser(userData) {
  const { data } = await api.post("/users/me", userData);
  return data;
}

export async function getUser() {
  const { data } = await api.get("/users/me");
  return data;
}

// ── Profile ─────────────────────────────────────────────────────────

export async function saveProfile(profileData) {
  const { data } = await api.put("/users/me/profile", profileData);
  return data;
}

export async function getProfile() {
  const { data } = await api.get("/users/me/profile");
  return data;
}

// ── Transcript ──────────────────────────────────────────────────────

export async function saveTranscript(courses) {
  const { data } = await api.put("/users/me/transcript", { courses });
  return data;
}

export async function getTranscript() {
  const { data } = await api.get("/users/me/transcript");
  return data;
}

// ── Chat History ────────────────────────────────────────────────────

export async function getChatHistory() {
  const { data } = await api.get("/users/me/chat-history");
  return data; // { messages }
}

export async function clearChatHistory() {
  await api.delete("/users/me/chat-history");
}



export default api;
