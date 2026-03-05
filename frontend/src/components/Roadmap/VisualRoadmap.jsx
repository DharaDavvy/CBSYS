import { useState, useCallback } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  useNodesState,
  useEdgesState,
} from "reactflow";
import "reactflow/dist/style.css";
import { generateRoadmap, getProfile } from "../../services/api";

export default function VisualRoadmap() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [generated, setGenerated] = useState(false);

  const generate = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      // Fetch the user's profile for interests/level
      let level = 100;
      let interests = [];
      try {
        const profile = await getProfile();
        interests = profile.interests || [];
      } catch {
        // Profile not found — use defaults
      }

      const data = await generateRoadmap({
        level,
        interests,
        completedCourses: [],
      });

      setSources(data.sources || []);

      // Convert roadmap data into React Flow nodes/edges
      const newNodes = [];
      const newEdges = [];

      (data.roadmap || []).forEach((sem, semIdx) => {
        // Semester header node
        const semId = `sem-${semIdx}`;
        newNodes.push({
          id: semId,
          type: "default",
          position: { x: semIdx * 320, y: 0 },
          data: {
            label: (
              <div className="font-bold text-[#8cc63f] text-sm">
                {sem.semester}
              </div>
            ),
          },
          style: {
            background: "#f4fce8",
            border: "2px solid #8cc63f",
            borderRadius: 0,
            padding: 10,
            minWidth: 250,
          },
        });

        // Course nodes under this semester
        (sem.courses || []).forEach((course, courseIdx) => {
          const courseId = `sem-${semIdx}-course-${courseIdx}`;
          newNodes.push({
            id: courseId,
            type: "default",
            position: { x: semIdx * 320, y: 70 + courseIdx * 60 },
            data: {
              label: (
                <div className="text-xs text-gray-700">{course}</div>
              ),
            },
            style: {
              background: "#FFFFFF",
              border: "1px solid #D1D5DB",
              borderRadius: 0,
              padding: 8,
              minWidth: 250,
            },
          });

          // Edge from semester header to each course
          newEdges.push({
            id: `edge-${semId}-${courseId}`,
            source: semId,
            target: courseId,
            style: { stroke: "#c6e69f" },
          });
        });

        // Edge between consecutive semesters
        if (semIdx > 0) {
          newEdges.push({
            id: `edge-sem-${semIdx - 1}-sem-${semIdx}`,
            source: `sem-${semIdx - 1}`,
            target: semId,
            style: { stroke: "#8cc63f", strokeWidth: 2 },
            animated: true,
          });
        }
      });

      setNodes(newNodes);
      setEdges(newEdges);
      setGenerated(true);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to generate roadmap.");
    } finally {
      setLoading(false);
    }
  }, [setNodes, setEdges]);

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Academic Roadmap</h2>
          <p className="text-sm text-gray-500">
            A personalised semester-by-semester plan based on your profile
          </p>
        </div>
        <button
          onClick={generate}
          disabled={loading}
          className="px-5 py-2 bg-[#8cc63f] text-white text-sm font-medium rounded-none hover:bg-[#7db437] disabled:opacity-50 transition cursor-pointer"
        >
          {loading ? "Generating..." : generated ? "Regenerate" : "Generate Roadmap"}
        </button>
      </div>

      {/* Flow canvas */}
      <div className="flex-1 relative">
        {!generated && !loading && (
          <div className="flex flex-col items-center justify-center h-full text-gray-400 text-center">
            <svg className="w-16 h-16 mb-4 text-[#c6e69f]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2m0 10V7m6 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2v10z" />
            </svg>
            <p className="font-medium text-gray-600">No roadmap yet</p>
            <p className="text-sm mt-1">Click "Generate Roadmap" to create your personalised plan</p>
          </div>
        )}

        {error && (
          <div className="absolute top-4 left-1/2 -translate-x-1/2 text-sm text-red-600 bg-red-50 px-4 py-2 rounded-none shadow z-10">
            {error}
          </div>
        )}

        {generated && (
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView
            className="bg-gray-50"
          >
            <Background gap={16} size={1} />
            <Controls />
          </ReactFlow>
        )}
      </div>

      {/* Sources */}
      {sources.length > 0 && (
        <div className="border-t border-gray-200 px-6 py-3 flex flex-wrap gap-2">
          <span className="text-xs text-gray-500 mr-1">Sources:</span>
          {sources.map((src, i) => (
            <span key={i} className="text-xs bg-[#f4fce8] text-[#8cc63f] px-2 py-0.5 rounded-none">
              {src}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
