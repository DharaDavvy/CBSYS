import { useState, useEffect } from "react";

const STAGES = [
  { after: 0,  text: "Thinking…" },
  { after: 5,  text: "Searching curriculum data…" },
  { after: 12, text: "Analysing sources…" },
  { after: 20, text: "Generating response…" },
  { after: 35, text: "Almost there…" },
];

export default function ThinkingBubble() {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const t = setInterval(() => setElapsed((s) => s + 1), 1000);
    return () => clearInterval(t);
  }, []);

  // Pick the latest stage whose threshold has been passed
  const stage = [...STAGES].reverse().find((s) => elapsed >= s.after);

  return (
    <div className="flex justify-start mb-4">
      <div className="bg-gray-100 rounded-none px-4 py-3 flex items-center gap-3">
        {/* Animated dots */}
        <div className="flex gap-1.5">
          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
        </div>
        {/* Status text */}
        <span className="text-xs text-gray-500">{stage.text}</span>
        {/* Elapsed time — shown after 5s so it doesn't flicker on fast responses */}
        {elapsed >= 5 && (
          <span className="text-xs text-gray-400 tabular-nums">{elapsed}s</span>
        )}
      </div>
    </div>
  );
}
