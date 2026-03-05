import { initializeApp } from "firebase/app";
import {
  getAuth,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  sendPasswordResetEmail,
  signOut,
} from "firebase/auth";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);

/**
 * Convert a matric number to the synthetic email used by Firebase Auth.
 * e.g. "CSC/2024/001" → "csc-2024-001@faculty.local"
 */
export function matricToEmail(matric) {
  return matric.trim().toLowerCase().replace(/\//g, "-") + "@faculty.local";
}

/**
 * Sign in with matric number + password.
 * Returns the Firebase UserCredential.
 */
export async function loginWithMatric(matric, password) {
  const email = matricToEmail(matric);
  return signInWithEmailAndPassword(auth, email, password);
}

/**
 * Register a new user with matric number + password.
 * Returns the Firebase UserCredential.
 */
export async function registerWithMatric(matric, password) {
  const email = matricToEmail(matric);
  return createUserWithEmailAndPassword(auth, email, password);
}

/**
 * Send a password reset email using the matric number.
 * Note: Since this uses a synthetic email, actual emails won't be delivered 
 * unless a custom email handler is set up mapping to real student emails.
 */
export async function resetPasswordWithMatric(matric) {
  const email = matricToEmail(matric);
  return sendPasswordResetEmail(auth, email);
}

/**
 * Sign the current user out.
 */
export async function logout() {
  return signOut(auth);
}

/**
 * Get the current user's ID token for API calls.
 */
export async function getIdToken() {
  const user = auth.currentUser;
  if (!user) throw new Error("Not authenticated");
  return user.getIdToken(true);
}
