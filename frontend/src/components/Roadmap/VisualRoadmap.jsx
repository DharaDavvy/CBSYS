import { useState, useCallback } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
} from "reactflow";
import "reactflow/dist/style.css";
import { generateRoadmap, generateCareerRoadmap, getProfile, getUser } from "../../services/api";

// ── Knowledge graph layout (topological BFS) ────────────────────────
function computeGraphLayout(pillars, dependencies) {
  const inDegree = Object.fromEntries(pillars.map(p => [p.id, 0]));
  const adj = Object.fromEntries(pillars.map(p => [p.id, []]));

  dependencies.forEach(d => {
    if (d.from_pillar in adj) adj[d.from_pillar].push(d.to_pillar);
    if (d.to_pillar in inDegree) inDegree[d.to_pillar]++;
  });

  // BFS to assign depth level (x-axis column)
  const levels = {};
  const queue = pillars.filter(p => inDegree[p.id] === 0).map(p => p.id);
  queue.forEach(id => { levels[id] = 0; });

  const visited = new Set(queue);
  let head = 0;
  while (head < queue.length) {
    const curr = queue[head++];
    (adj[curr] || []).forEach(next => {
      levels[next] = Math.max(levels[next] ?? 0, (levels[curr] ?? 0) + 1);
      if (!visited.has(next)) { visited.add(next); queue.push(next); }
    });
  }

  // Stack multiple pillars at the same depth vertically
  const levelYIdx = {};
  const positions = {};
  pillars.forEach(p => {
    const level = levels[p.id] ?? 0;
    const yi = levelYIdx[level] ?? 0;
    positions[p.id] = { x: level * 400, y: yi * 240 };
    levelYIdx[level] = yi + 1;
  });
  return positions;
}

// ── Colour palette for pillars ──────────────────────────────────────
const PILLAR_COLOURS = [
  { bg: "#f4fce8", border: "#8cc63f", text: "#3d6b00" },
  { bg: "#eff6ff", border: "#3b82f6", text: "#1e3a8a" },
  { bg: "#fef3c7", border: "#f59e0b", text: "#78350f" },
  { bg: "#fdf2f8", border: "#a855f7", text: "#581c87" },
  { bg: "#ecfdf5", border: "#10b981", text: "#065f46" },
  { bg: "#fff1f2", border: "#f43f5e", text: "#881337" },
  { bg: "#f0f9ff", border: "#0ea5e9", text: "#0c4a6e" },
];

const TAB_ACADEMIC = "academic";
const TAB_CAREER   = "career";

export default function VisualRoadmap() {
  const [activeTab, setActiveTab] = useState(TAB_ACADEMIC);

  // ── Academic Roadmap state ──────────────────────────────────────
  const [acNodes, setAcNodes, onAcNodesChange] = useNodesState([]);
  const [acEdges, setAcEdges, onAcEdgesChange] = useEdgesState([]);
  const [acSources, setAcSources] = useState([]);
  const [acLoading, setAcLoading] = useState(false);
  const [acError, setAcError] = useState("");
  const [acGenerated, setAcGenerated] = useState(false);

  // ── Career Knowledge Graph state ────────────────────────────────
  const [careerSector, setCareerSector] = useState("");
  const [cgNodes, setCgNodes, onCgNodesChange] = useNodesState([]);
  const [cgEdges, setCgEdges, onCgEdgesChange] = useEdgesState([]);
  const [cgSources, setCgSources] = useState([]);
  const [cgLoading, setCgLoading] = useState(false);
  const [cgError, setCgError] = useState("");
  const [cgGenerated, setCgGenerated] = useState(false);

  // ── Generate Academic Roadmap ───────────────────────────────────
  const generateAcademic = useCallback(async () => {
    setAcLoading(true);
    setAcError("");
    try {
      let level = 100;
      let interests = [];
      try {
        const [profile, user] = await Promise.all([getProfile(), getUser()]);
        interests = profile.interests || [];
        level = user.level || 100;
      } catch { /* use defaults */ }

      const data = await generateRoadmap({ level, interests, completedCourses: [] });
      setAcSources(data.sources || []);

      const newNodes = [];
      const newEdges = [];

      (data.roadmap || []).forEach((sem, semIdx) => {
        const semId = `sem-${semIdx}`;
        newNodes.push({
          id: semId,
          type: "default",
          position: { x: semIdx * 320, y: 0 },
          data: {
            label: (
              <div className="font-bold text-[#8cc63f] text-sm">{sem.semester}</div>
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

        (sem.courses || []).forEach((course, ci) => {
          const cid = `sem-${semIdx}-course-${ci}`;
          newNodes.push({
            id: cid,
            type: "default",
            position: { x: semIdx * 320, y: 70 + ci * 60 },
            data: { label: <div className="text-xs text-gray-700">{course}</div> },
            style: {
              background: "#FFFFFF",
              border: "1px solid #D1D5DB",
              borderRadius: 0,
              padding: 8,
              minWidth: 250,
            },
          });
          newEdges.push({
            id: `edge-${semId}-${cid}`,
            source: semId,
            target: cid,
            style: { stroke: "#c6e69f" },
          });
        });

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

      setAcNodes(newNodes);
      setAcEdges(newEdges);
      setAcGenerated(true);
    } catch (err) {
      setAcError(err.response?.data?.detail || "Failed to generate academic roadmap.");
    } finally {
      setAcLoading(false);
    }
  }, [setAcNodes, setAcEdges]);

  // ── Generate Career Knowledge Graph ────────────────────────────
  const generateCareer = useCallback(async () => {
    if (!careerSector.trim()) {
      setCgError("Please enter a career sector.");
      return;
    }
    setCgLoading(true);
    setCgError("");
    try {
      const data = await generateCareerRoadmap({ career_sector: careerSector.trim() });
      setCgSources(data.sources || []);

      const pillars = data.pillars || [];
      const dependencies = data.dependencies || [];
      const positions = computeGraphLayout(pillars, dependencies);

      const newNodes = pillars.map((pillar, idx) => {
        const colour = PILLAR_COLOURS[idx % PILLAR_COLOURS.length];
        const pos = positions[pillar.id] || { x: idx * 400, y: 0 };
        const shown = (pillar.courses || []).slice(0, 4);
        const extra = (pillar.courses || []).length - shown.length;
        return {
          id: pillar.id,
          type: "default",
          position: pos,
          data: {
            label: (
              <div style={{ maxWidth: 280 }}>
                <div style={{ color: colour.text, fontWeight: 700, fontSize: 13, marginBottom: 6 }}>
                  {pillar.label}
                </div>
                {pillar.description && (
                  <div style={{ color: "#6b7280", fontSize: 10, marginBottom: 6, fontStyle: "italic" }}>
                    {pillar.description}
                  </div>
                )}
                {shown.map((c, i) => (
                  <div key={i} style={{ fontSize: 10, color: "#374151", marginBottom: 2 }}>• {c}</div>
                ))}
                {extra > 0 && (
                  <div style={{ fontSize: 10, color: colour.text, marginTop: 3 }}>
                    +{extra} more course{extra > 1 ? "s" : ""}
                  </div>
                )}
              </div>
            ),
          },
          style: {
            background: colour.bg,
            border: `2px solid ${colour.border}`,
            borderRadius: 6,
            padding: 12,
            minWidth: 290,
          },
        };
      });

      const newEdges = dependencies.map((dep, i) => ({
        id: `dep-${i}`,
        source: dep.from_pillar,
        target: dep.to_pillar,
        animated: true,
        style: { stroke: "#8cc63f", strokeWidth: 2 },
        markerEnd: { type: MarkerType.ArrowClosed, color: "#8cc63f" },
        label: "prerequisite",
        labelStyle: { fontSize: 9, fill: "#6b7280" },
        labelBgStyle: { fill: "transparent" },
      }));

      setCgNodes(newNodes);
      setCgEdges(newEdges);
      setCgGenerated(true);
    } catch (err) {
      setCgError(err.response?.data?.detail || "Failed to generate knowledge graph.");
    } finally {
      setCgLoading(false);
    }
  }, [careerSector, setCgNodes, setCgEdges]);

  const isAcademic = activeTab === TAB_ACADEMIC;
  const activeSources = isAcademic ? acSources : cgSources;

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="border-b border-gray-200 px-6 py-4">
        {/* Tab bar */}
        <div className="flex gap-6 mb-3">
          {[
            { key: TAB_ACADEMIC, label: "Academic Roadmap" },
            { key: TAB_CAREER,   label: "Career Knowledge Graph" },
          ].map(({ key, label }) => (
            <button
              key={key}
              onClick={() => setActiveTab(key)}
              className={`text-sm font-medium pb-1 border-b-2 transition ${
                activeTab === key
                  ? "border-[#8cc63f] text-[#8cc63f]"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        {/* Controls */}
        {isAcademic ? (
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-500">
              A personalised semester-by-semester plan based on your profile
            </p>
            <button
              onClick={generateAcademic}
              disabled={acLoading}
              className="px-5 py-2 bg-[#8cc63f] text-white text-sm font-medium rounded-none hover:bg-[#7db437] disabled:opacity-50 transition cursor-pointer"
            >
              {acLoading ? "Generating…" : acGenerated ? "Regenerate" : "Generate Roadmap"}
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <input
              type="text"
              value={careerSector}
              onChange={e => setCareerSector(e.target.value)}
              onKeyDown={e => e.key === "Enter" && generateCareer()}
              placeholder="e.g. Web Development, Data Science, Cybersecurity…"
              className="flex-1 border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:border-[#8cc63f]"
            />
            <button
              onClick={generateCareer}
              disabled={cgLoading}
              className="px-5 py-2 bg-[#8cc63f] text-white text-sm font-medium rounded-none hover:bg-[#7db437] disabled:opacity-50 transition cursor-pointer whitespace-nowrap"
            >
              {cgLoading ? "Analysing…" : cgGenerated ? "Regenerate" : "Sequence Knowledge"}
            </button>
          </div>
        )}
      </div>

      {/* Flow canvas */}
      <div className="flex-1 relative">
        {/* Empty state */}
        {((isAcademic && !acGenerated && !acLoading) ||
          (!isAcademic && !cgGenerated && !cgLoading)) && (
          <div className="flex flex-col items-center justify-center h-full text-gray-400 text-center">
            <svg className="w-16 h-16 mb-4 text-[#c6e69f]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2m0 10V7m6 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2v10z" />
            </svg>
            <p className="font-medium text-gray-600">
              {isAcademic ? "No roadmap yet" : "No knowledge graph yet"}
            </p>
            <p className="text-sm mt-1">
              {isAcademic
                ? "Click \"Generate Roadmap\" to create your personalised plan"
                : "Enter a career sector and click \"Sequence Knowledge\""}
            </p>
          </div>
        )}

        {/* Errors */}
        {((isAcademic && acError) || (!isAcademic && cgError)) && (
          <div className="absolute top-4 left-1/2 -translate-x-1/2 text-sm text-red-600 bg-red-50 px-4 py-2 rounded-none shadow z-10">
            {isAcademic ? acError : cgError}
          </div>
        )}

        {/* Academic semester flow */}
        {isAcademic && acGenerated && (
          <ReactFlow
            nodes={acNodes}
            edges={acEdges}
            onNodesChange={onAcNodesChange}
            onEdgesChange={onAcEdgesChange}
            fitView
            className="bg-gray-50"
          >
            <Background gap={16} size={1} />
            <Controls />
          </ReactFlow>
        )}

        {/* Career knowledge graph */}
        {!isAcademic && cgGenerated && (
          <ReactFlow
            nodes={cgNodes}
            edges={cgEdges}
            onNodesChange={onCgNodesChange}
            onEdgesChange={onCgEdgesChange}
            fitView
            className="bg-gray-50"
          >
            <Background gap={16} size={1} />
            <Controls />
            <MiniMap maskColor="rgba(0,0,0,0.05)" />
          </ReactFlow>
        )}
      </div>

      {/* Sources footer */}
      {activeSources.length > 0 && (
        <div className="border-t border-gray-200 px-6 py-3 flex flex-wrap gap-2">
          <span className="text-xs text-gray-500 mr-1">Sources:</span>
          {activeSources.map((src, i) => (
            <span key={i} className="text-xs bg-[#f4fce8] text-[#8cc63f] px-2 py-0.5 rounded-none">
              {src}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}