export default function MessageBubble({ message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-blue-600 text-white rounded-br-md"
            : "bg-gray-100 text-gray-900 rounded-bl-md"
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
                className="inline-block text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full"
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
