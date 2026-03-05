import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import { getUser, getProfile, saveProfile } from "../../services/api";

export default function Profile() {
  const { currentUser } = useAuth();
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [editing, setEditing] = useState(false);
  const [interests, setInterests] = useState([]);
  const [targetCareer, setTargetCareer] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    getUser().then(setUser).catch(() => {});
    getProfile()
      .then((p) => {
        setProfile(p);
        setInterests(p.interests || []);
        setTargetCareer(p.targetCareer || "");
      })
      .catch(() => {});
  }, []);

  async function handleSave() {
    setSaving(true);
    try {
      const updated = await saveProfile({ interests, skills: profile?.skills || [], targetCareer });
      setProfile(updated);
      setEditing(false);
    } catch {
      // Silently fail
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h2 className="text-xl font-bold text-gray-900 mb-6">Profile</h2>

      {/* User info */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">
          Student Information
        </h3>
        <dl className="grid grid-cols-2 gap-4">
          {[
            ["Name", user?.name || "—"],
            ["Matric Number", user?.matricNumber || currentUser?.email?.replace("@faculty.local", "").replace(/-/g, "/").toUpperCase()],
            ["Department", user?.department || "—"],
            ["Level", user?.level ? `Level ${user.level}` : "—"],
          ].map(([label, value]) => (
            <div key={label}>
              <dt className="text-xs text-gray-500">{label}</dt>
              <dd className="text-sm font-medium text-gray-900 mt-0.5">{value}</dd>
            </div>
          ))}
        </dl>
      </div>

      {/* Profile / interests */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
            Interests & Goals
          </h3>
          {!editing && (
            <button
              onClick={() => setEditing(true)}
              className="text-sm text-blue-600 hover:underline cursor-pointer"
            >
              Edit
            </button>
          )}
        </div>

        {editing ? (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Interests (comma-separated)
              </label>
              <input
                type="text"
                value={interests.join(", ")}
                onChange={(e) =>
                  setInterests(e.target.value.split(",").map((s) => s.trim()).filter(Boolean))
                }
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Target Career
              </label>
              <input
                type="text"
                value={targetCareer}
                onChange={(e) => setTargetCareer(e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              />
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setEditing(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50 transition cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={saving}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50 transition cursor-pointer"
              >
                {saving ? "Saving..." : "Save"}
              </button>
            </div>
          </div>
        ) : (
          <div>
            <div className="flex flex-wrap gap-2 mb-4">
              {(profile?.interests || []).length > 0 ? (
                profile.interests.map((interest, i) => (
                  <span
                    key={i}
                    className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm"
                  >
                    {interest}
                  </span>
                ))
              ) : (
                <span className="text-sm text-gray-400">No interests set</span>
              )}
            </div>
            <div>
              <dt className="text-xs text-gray-500">Target Career</dt>
              <dd className="text-sm font-medium text-gray-900 mt-0.5">
                {profile?.targetCareer || "—"}
              </dd>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
