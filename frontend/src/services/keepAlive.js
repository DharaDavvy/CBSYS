/**
 * Pings the backend /health endpoint every INTERVAL ms to prevent
 * Render free-tier cold starts during an active session.
 */
import api from "./api";

const INTERVAL = 9 * 60 * 1000; // 9 minutes (Render sleeps after 15 min inactivity)

let timer = null;

async function ping() {
  try {
    await api.get("/health");
  } catch {
    // Silently ignore — it's just a keep-alive
  }
}

export function startKeepAlive() {
  if (timer) return;
  ping(); // immediate ping on start
  timer = setInterval(ping, INTERVAL);
}

export function stopKeepAlive() {
  if (timer) {
    clearInterval(timer);
    timer = null;
  }
}
