export default function ChatBubble({ role, content }: { role: string; content: string }) {
  return (
    <div className={`mb-2 p-2 rounded max-w-xs ${role === "HumanMessage" ? "bg-blue-400 self-end" : "bg-green-600 self-start"}`}>
      <p className="text-sm">{content}</p>
    </div>
  );
}
