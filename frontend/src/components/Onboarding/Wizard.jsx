import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { saveUser, saveProfile } from "../../services/api";

const DEPARTMENTS = [
  "Computer Science",
  "Information Technology",
  "Software Engineering",
  "Cyber Security",
];

const INTEREST_OPTIONS = [
  "Web Development",
  "Mobile Development",
  "Data Science",
  "Artificial Intelligence",
  "Cyber Security",
  "Cloud Computing",
  "Game Development",
  "Database Administration",
  "Networking",
  "DevOps",
];

export default function Wizard() {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  // Step 1 data
  const [name, setName] = useState("");
  const [matricNumber, setMatricNumber] = useState("");
  const [department, setDepartment] = useState(DEPARTMENTS[0]);
  const [level, setLevel] = useState(100);

  // Step 2 data
  const [interests, setInterests] = useState([]);
  const [targetCareer, setTargetCareer] = useState("");

  function toggleInterest(item) {
    setInterests((prev) =>
      prev.includes(item) ? prev.filter((i) => i !== item) : [...prev, item]
    );
  }

  async function handleFinish() {
    setLoading(true);
    setError("");
    try {
      await saveUser({ name, matricNumber, department, level });
      await saveProfile({ interests, skills: [], targetCareer });
      sessionStorage.removeItem("needsOnboarding");
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save profile.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <div className="w-full max-w-lg bg-white rounded-none shadow-lg p-8">
        {/* Progress indicator */}
        <div className="flex items-center justify-center gap-2 mb-8">
          {[1, 2].map((s) => (
            <div
              key={s}
              className={`h-2 w-16 rounded-none transition ${
                s <= step ? "bg-[#8cc63f]" : "bg-gray-200"
              }`}
            />
          ))}
        </div>

        {step === 1 && (
          <>
            <h2 className="text-xl font-bold text-gray-900 mb-1">
              Welcome! Let's set up your profile
            </h2>
            <p className="text-gray-500 mb-6 text-sm">Step 1 of 2 — Basic Information</p>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Full Name
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="John Doe"
                  required
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-none focus:ring-2 focus:ring-[#8cc63f] focus:border-[#8cc63f] outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Matric Number
                </label>
                <input
                  type="text"
                  value={matricNumber}
                  onChange={(e) => setMatricNumber(e.target.value)}
                  placeholder="CSC/2024/001"
                  required
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-none focus:ring-2 focus:ring-[#8cc63f] focus:border-[#8cc63f] outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Department
                </label>
                <select
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-none focus:ring-2 focus:ring-[#8cc63f] focus:border-[#8cc63f] outline-none"
                >
                  {DEPARTMENTS.map((d) => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Current Level
                </label>
                <select
                  value={level}
                  onChange={(e) => setLevel(Number(e.target.value))}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-none focus:ring-2 focus:ring-[#8cc63f] focus:border-[#8cc63f] outline-none"
                >
                  {[100, 200, 300, 400, 500].map((l) => (
                    <option key={l} value={l}>Level {l}</option>
                  ))}
                </select>
              </div>
            </div>

            <button
              onClick={() => setStep(2)}
              disabled={!name || !matricNumber}
              className="w-full mt-6 py-2.5 bg-[#8cc63f] text-white font-medium rounded-none hover:bg-[#7db437] disabled:opacity-50 transition cursor-pointer"
            >
              Next
            </button>
          </>
        )}

        {step === 2 && (
          <>
            <h2 className="text-xl font-bold text-gray-900 mb-1">
              Your Interests & Goals
            </h2>
            <p className="text-gray-500 mb-6 text-sm">Step 2 of 2 — Select your interests</p>

            <div className="flex flex-wrap gap-2 mb-6">
              {INTEREST_OPTIONS.map((item) => (
                <button
                  key={item}
                  onClick={() => toggleInterest(item)}
                  className={`px-3 py-1.5 rounded-none text-sm font-medium border transition cursor-pointer ${
                    interests.includes(item)
                      ? "bg-[#8cc63f] text-white border-[#8cc63f]"
                      : "bg-white text-gray-700 border-gray-300 hover:border-blue-400"
                  }`}
                >
                  {item}
                </button>
              ))}
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Target Career (optional)
              </label>
              <input
                type="text"
                value={targetCareer}
                onChange={(e) => setTargetCareer(e.target.value)}
                placeholder="e.g. Data Scientist, Full-Stack Developer"
                className="w-full px-4 py-2.5 border border-gray-300 rounded-none focus:ring-2 focus:ring-[#8cc63f] focus:border-[#8cc63f] outline-none"
              />
            </div>

            {error && (
              <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-none mb-4">
                {error}
              </p>
            )}

            <div className="flex gap-3">
              <button
                onClick={() => setStep(1)}
                className="flex-1 py-2.5 border border-gray-300 text-gray-700 font-medium rounded-none hover:bg-gray-50 transition cursor-pointer"
              >
                Back
              </button>
              <button
                onClick={handleFinish}
                disabled={loading}
                className="flex-1 py-2.5 bg-[#8cc63f] text-white font-medium rounded-none hover:bg-[#7db437] disabled:opacity-50 transition cursor-pointer"
              >
                {loading ? "Saving..." : "Finish Setup"}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
