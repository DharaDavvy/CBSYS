import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginWithMatric, registerWithMatric } from "../../services/firebase";

export default function Login() {
  const [matric, setMatric] = useState("");
  const [password, setPassword] = useState("");
  const [isRegister, setIsRegister] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (isRegister) {
        sessionStorage.setItem("needsOnboarding", "1");
        await registerWithMatric(matric, password);
        navigate("/onboarding");
      } else {
        await loginWithMatric(matric, password);
        navigate("/dashboard");
      }
    } catch (err) {
      if (err.code === "auth/user-not-found" || err.code === "auth/invalid-credential") {
        setError("Invalid matric number or password.");
      } else if (err.code === "auth/email-already-in-use") {
        setError("This matric number is already registered. Try logging in.");
      } else if (err.code === "auth/weak-password") {
        setError("Password must be at least 6 characters.");
      } else {
        setError(err.message || "Something went wrong.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-lg p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-blue-600 rounded-xl mb-4">
            <span className="text-2xl text-white font-bold">CB</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">CBSys</h1>
          <p className="text-gray-500 mt-1">Career-Based Information System</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Matric Number */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Matric Number
            </label>
            <input
              type="text"
              placeholder="CSC/2024/001"
              value={matric}
              onChange={(e) => setMatric(e.target.value)}
              required
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            />
          </div>

          {/* Password */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            />
          </div>

          {error && (
            <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 transition cursor-pointer"
          >
            {loading ? "Please wait..." : isRegister ? "Create Account" : "Log In"}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={() => {
              setIsRegister(!isRegister);
              setError("");
            }}
            className="text-sm text-blue-600 hover:underline cursor-pointer"
          >
            {isRegister
              ? "Already have an account? Log in"
              : "New student? Create an account"}
          </button>
        </div>
      </div>
    </div>
  );
}
