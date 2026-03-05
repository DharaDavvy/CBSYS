import { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import {
  loginWithMatric,
  registerWithMatric,
  resetPasswordWithMatric,
} from "../../services/firebase";

export default function Login() {
  const [view, setView] = useState("login"); // 'login' | 'register' | 'forgot'
  const [matric, setMatric] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Local Validation
  const validateForm = () => {
    setError("");
    setMessage("");
    
    // Example: CSC/2024/001
    const matricRegex = /^[a-zA-Z]{3}\/\d{4}\/\d{3,4}$/;
    
    if (!matric) {
      setError("Matric Number is required");
      return false;
    }
    
    if (!matricRegex.test(matric)) {
      setError("Invalid format. Use format like CSC/2024/001");
      return false;
    }

    if (view !== "forgot") {
      if (!password) {
        setError("Password is required");
        return false;
      }
      if (password.length < 6) {
        setError("Password must be at least 6 characters long");
        return false;
      }
      if (view === "register" && password !== confirmPassword) {
        setError("Passwords do not match");
        return false;
      }
    }

    return true;
  };

  async function handleSubmit(e) {
    e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);

    try {
      if (view === "register") {
        sessionStorage.setItem("needsOnboarding", "1");
        await registerWithMatric(matric, password);
        navigate("/onboarding");
      } else if (view === "login") {
        await loginWithMatric(matric, password);
        navigate("/dashboard");
      } else if (view === "forgot") {
        await resetPasswordWithMatric(matric);
        setMessage("If that matric number exists, a reset link has been configured (Internal simulation)");
        // Note: For real use with synthetic emails, this requires custom backend handling.
        // We just show a success message here mimicking the design.
      }
    } catch (err) {
      if (err.code === "auth/user-not-found" || err.code === "auth/invalid-credential") {
        setError("Invalid matric number or password.");
      } else if (err.code === "auth/email-already-in-use") {
        setError("This matric number is already registered. Try logging in.");
      } else if (err.code === "auth/too-many-requests") {
        setError("Too many attempts. Please try again later.");
      } else {
        setError(err.message || "Something went wrong.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#f7f7f7] flex flex-col items-center justify-center py-10 px-4">
      {/* Brand Header */}
      <div className="flex items-center gap-2 mb-10">
        <div className="w-8 h-8 flex items-center justify-center border-2 border-[#8cc63f] rounded-none">
          <span className="text-[#8cc63f] font-bold text-lg leading-none">CB</span>
        </div>
        <span className="font-bold text-gray-800 text-xl tracking-wide">CBSys</span>
      </div>

      <div className="bg-white rounded-none shadow-sm border border-gray-100 p-8 sm:p-10 w-full max-w-[440px]">
        <h2 className="text-[26px] font-bold text-[#1f2937] text-center mb-6 tracking-tight">
          {view === "login" && "Welcome Back!"}
          {view === "register" && "Create an Account"}
          {view === "forgot" && "Forgot Password"}
        </h2>

        {view === "forgot" && (
          <p className="text-sm text-gray-500 text-center mb-6 px-4">
            No worries, enter your matric number and we will help you reset your password.
          </p>
        )}

        {/* Global Messages */}
        {error && (
          <div className="mb-4 text-sm text-red-600 bg-red-50 border border-red-200 px-4 py-3 rounded-none flex items-start gap-2">
             <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
             <span>{error}</span>
          </div>
        )}
        {message && (
          <div className="mb-4 text-sm text-green-700 bg-green-50 border border-green-200 px-4 py-3 rounded-none flex items-start gap-2">
            <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7"/></svg>
            <span>{message}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Matric Input */}
          <div className="space-y-1.5">
            <label className="block text-[13px] font-semibold text-gray-700">
              Matric Number <span className="text-red-500">*</span>
            </label>
            <div className="relative flex items-center">
              <div className="absolute left-3.5 text-gray-400">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                </svg>
              </div>
              <input
                type="text"
                value={matric}
                onChange={(e) => setMatric(e.target.value.toUpperCase())}
                placeholder="CSC/2024/001"
                className="w-full pl-11 pr-4 py-3 text-sm border border-gray-200 rounded-none focus:border-[#8cc63f] focus:ring-1 focus:ring-[#8cc63f] outline-none transition-all"
              />
            </div>
          </div>

          {/* Password Inputs */}
          {view !== "forgot" && (
            <>
              <div className="space-y-1.5">
                <label className="block text-[13px] font-semibold text-gray-700">
                  Password <span className="text-red-500">*</span>
                </label>
                <div className="relative flex items-center">
                  <div className="absolute left-3.5 text-gray-400">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                  </div>
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-11 pr-11 py-3 text-sm border border-gray-200 rounded-none focus:border-[#8cc63f] focus:ring-1 focus:ring-[#8cc63f] outline-none transition-all"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3.5 text-gray-400 hover:text-gray-600 transition-colors cursor-pointer"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      {showPassword ? (
                         <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      ) : (
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                      )}
                    </svg>
                  </button>
                </div>
                {view === "login" && (
                  <div className="flex justify-end mt-2">
                    <button
                      type="button"
                      onClick={() => { setView("forgot"); setError(""); setMessage(""); }}
                      className="text-[#8cc63f] text-xs font-semibold hover:underline cursor-pointer"
                    >
                      Forgot Password
                    </button>
                  </div>
                )}
              </div>

              {view === "register" && (
                <div className="space-y-1.5 pt-2">
                  <label className="block text-[13px] font-semibold text-gray-700">
                    Confirm Password <span className="text-red-500">*</span>
                  </label>
                  <div className="relative flex items-center">
                    <div className="absolute left-3.5 text-gray-400">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                      </svg>
                    </div>
                    <input
                      type={showPassword ? "text" : "password"}
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="••••••••"
                      className="w-full pl-11 pr-11 py-3 text-sm border border-gray-200 rounded-none focus:border-[#8cc63f] focus:ring-1 focus:ring-[#8cc63f] outline-none transition-all"
                    />
                  </div>
                </div>
              )}
            </>
          )}

          {/* Action Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-[#8cc63f] hover:bg-[#7db437] text-white font-medium py-3 rounded-none transition-colors mt-2 disabled:opacity-70 disabled:cursor-not-allowed cursor-pointer"
          >
            {loading ? "Please wait..." : (
              view === "login" ? "Login" : 
              view === "register" ? "Sign Up" : 
              "Get Link"
            )}
          </button>
        </form>

        {/* Alternate Links */}
        <div className="mt-8">
          {view === "forgot" ? (
            <div className="text-center">
              <button
                type="button"
                onClick={() => { setView("login"); setError(""); setMessage(""); }}
                className="text-[#8cc63f] text-sm font-semibold flex items-center justify-center gap-1.5 mx-auto hover:underline cursor-pointer"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
                Back to Login
              </button>
            </div>
          ) : (
            <div className="text-center text-sm text-gray-500">
              {view === "login" ? (
                <>
                  Don't have an account?{" "}
                  <button
                    onClick={() => { setView("register"); setError(""); setMessage(""); }}
                    className="text-[#8cc63f] font-semibold hover:underline cursor-pointer"
                  >
                    Sign Up
                  </button>
                </>
              ) : (
                <>
                  Already have an account?{" "}
                  <button
                    onClick={() => { setView("login"); setError(""); setMessage(""); }}
                    className="text-[#8cc63f] font-semibold hover:underline cursor-pointer"
                  >
                    Login
                  </button>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
