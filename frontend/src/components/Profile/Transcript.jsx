import { useState, useEffect } from "react";
import { getTranscript, saveTranscript } from "../../services/api";

const GRADE_OPTIONS = ["A", "B", "C", "D", "E", "F"];

const emptyForm = { code: "", title: "", units: "", grade: "A", semester: "" };

export default function Transcript() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [formError, setFormError] = useState("");
  const [saveError, setSaveError] = useState("");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    getTranscript()
      .then((data) => setCourses(data.courses || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  function handleFormChange(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
    setFormError("");
  }

  function handleAdd() {
    if (!form.code.trim()) return setFormError("Course code is required.");
    if (!form.title.trim()) return setFormError("Course title is required.");
    if (!form.units || isNaN(Number(form.units)) || Number(form.units) < 1) {
      return setFormError("Valid number of units is required.");
    }

    const duplicate = courses.some(
      (c) => c.code.trim().toUpperCase() === form.code.trim().toUpperCase()
    );
    if (duplicate) return setFormError(`Course ${form.code.toUpperCase()} is already in your transcript.`);

    setCourses((prev) => [
      ...prev,
      { ...form, code: form.code.trim().toUpperCase(), units: Number(form.units) },
    ]);
    setForm(emptyForm);
    setShowForm(false);
    setFormError("");
  }

  function handleRemove(idx) {
    setCourses((prev) => prev.filter((_, i) => i !== idx));
    setSaved(false);
  }

  async function handleSave() {
    setSaving(true);
    setSaveError("");
    setSaved(false);
    try {
      await saveTranscript(courses);
      setSaved(true);
    } catch {
      setSaveError("Failed to save. Please try again.");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="p-6 flex justify-center items-center h-48">
        <div className="text-sm text-gray-400">Loading transcript…</div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Academic Transcript</h2>
          <p className="text-sm text-gray-500 mt-0.5">
            Record your completed courses. This helps the advisor generate a personalised roadmap.
          </p>
        </div>
        <div className="flex gap-3">
          {!showForm && (
            <button
              onClick={() => { setShowForm(true); setFormError(""); }}
              className="flex items-center gap-2 px-4 py-2 border border-[#8cc63f] text-[#8cc63f] text-sm font-medium rounded-none hover:bg-[#f4fce8] transition cursor-pointer"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Add Course
            </button>
          )}
          <button
            onClick={handleSave}
            disabled={saving || courses.length === 0}
            className="px-4 py-2 bg-[#8cc63f] text-white text-sm font-medium rounded-none hover:bg-[#7db437] disabled:opacity-50 transition cursor-pointer"
          >
            {saving ? "Saving…" : "Save Transcript"}
          </button>
        </div>
      </div>

      {/* Save messages */}
      {saved && (
        <div className="mb-4 text-sm text-green-700 bg-green-50 border border-green-200 px-4 py-3 rounded-none flex items-center gap-2">
          <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          Transcript saved successfully.
        </div>
      )}
      {saveError && (
        <div className="mb-4 text-sm text-red-600 bg-red-50 border border-red-200 px-4 py-3 rounded-none">
          {saveError}
        </div>
      )}

      {/* Add Course Form */}
      {showForm && (
        <div className="bg-white border border-[#8cc63f] rounded-none p-5 mb-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">New Course</h3>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                Course Code <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={form.code}
                onChange={(e) => handleFormChange("code", e.target.value.toUpperCase())}
                placeholder="e.g. CSC301"
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-none focus:ring-1 focus:ring-[#8cc63f] focus:border-[#8cc63f] outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                Course Title <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={form.title}
                onChange={(e) => handleFormChange("title", e.target.value)}
                placeholder="e.g. Data Structures"
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-none focus:ring-1 focus:ring-[#8cc63f] focus:border-[#8cc63f] outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                Units <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                min="1"
                max="6"
                value={form.units}
                onChange={(e) => handleFormChange("units", e.target.value)}
                placeholder="e.g. 3"
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-none focus:ring-1 focus:ring-[#8cc63f] focus:border-[#8cc63f] outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Grade</label>
              <select
                value={form.grade}
                onChange={(e) => handleFormChange("grade", e.target.value)}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-none focus:ring-1 focus:ring-[#8cc63f] focus:border-[#8cc63f] outline-none bg-white"
              >
                {GRADE_OPTIONS.map((g) => (
                  <option key={g} value={g}>{g}</option>
                ))}
              </select>
            </div>
            <div className="col-span-2">
              <label className="block text-xs font-medium text-gray-600 mb-1">Semester</label>
              <input
                type="text"
                value={form.semester}
                onChange={(e) => handleFormChange("semester", e.target.value)}
                placeholder="e.g. 300L First Semester"
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-none focus:ring-1 focus:ring-[#8cc63f] focus:border-[#8cc63f] outline-none"
              />
            </div>
          </div>

          {formError && (
            <p className="text-xs text-red-600 mb-3">{formError}</p>
          )}

          <div className="flex gap-3">
            <button
              onClick={() => { setShowForm(false); setForm(emptyForm); setFormError(""); }}
              className="px-4 py-2 border border-gray-300 text-sm text-gray-700 rounded-none hover:bg-gray-50 transition cursor-pointer"
            >
              Cancel
            </button>
            <button
              onClick={handleAdd}
              className="px-4 py-2 bg-[#8cc63f] text-white text-sm rounded-none hover:bg-[#7db437] transition cursor-pointer"
            >
              Add
            </button>
          </div>
        </div>
      )}

      {/* Courses Table */}
      {courses.length === 0 ? (
        <div className="bg-white border border-gray-200 rounded-none p-12 text-center">
          <svg className="w-10 h-10 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-sm text-gray-400">No courses yet. Add your completed courses above.</p>
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-none overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200 text-left">
                <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Code</th>
                <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Title</th>
                <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide text-center">Units</th>
                <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide text-center">Grade</th>
                <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Semester</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {courses.map((course, idx) => (
                <tr key={idx} className="hover:bg-gray-50 transition">
                  <td className="px-4 py-3 font-mono font-medium text-gray-900">{course.code}</td>
                  <td className="px-4 py-3 text-gray-700">{course.title}</td>
                  <td className="px-4 py-3 text-center text-gray-700">{course.units}</td>
                  <td className="px-4 py-3 text-center">
                    <span
                      className={`inline-block px-2 py-0.5 text-xs font-semibold rounded-none ${
                        course.grade === "A"
                          ? "bg-green-100 text-green-700"
                          : course.grade === "B"
                          ? "bg-blue-100 text-blue-700"
                          : course.grade === "C"
                          ? "bg-yellow-100 text-yellow-700"
                          : "bg-red-100 text-red-700"
                      }`}
                    >
                      {course.grade}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-500 text-xs">{course.semester || "—"}</td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => handleRemove(idx)}
                      className="text-gray-400 hover:text-red-500 transition cursor-pointer"
                      title="Remove course"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr className="bg-gray-50 border-t border-gray-200">
                <td className="px-4 py-3 text-xs text-gray-500 font-medium" colSpan={2}>
                  {courses.length} course{courses.length !== 1 ? "s" : ""}
                </td>
                <td className="px-4 py-3 text-center text-xs font-semibold text-gray-700">
                  {courses.reduce((s, c) => s + (Number(c.units) || 0), 0)} units
                </td>
                <td colSpan={3}></td>
              </tr>
            </tfoot>
          </table>
        </div>
      )}
    </div>
  );
}
