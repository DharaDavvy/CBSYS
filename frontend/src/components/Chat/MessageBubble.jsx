export default function MessageBubble({ message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[80%] rounded-none px-4 py-3 ${
          isUser
            ? "bg-[#8cc63f] text-white rounded-none"
            : "bg-gray-100 text-gray-900 rounded-none"
        }`}
      >
        <p className="text-sm whitespace-pre-wrap leading-relaxed">
          {message.content}
        </p>

        {/* Source citations */}
        {!isUser && message.sources?.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {message.sources.map((src, i) => (
              <span
                key={i}
                className="inline-block text-xs bg-[#f4fce8] text-[#8cc63f] px-2 py-0.5 rounded-none"
              >
                {src}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
