export default function ChatBubble({ role, content }: { role: string; content: string }) {
  return (
    <div className={`mb-2 p-2 rounded max-w-xs ${role === "user" ? "bg-blue-100 self-end" : "bg-gray-200 self-start"}`}>
      <p className="text-sm">{content}</p>
    </div>
  );
}
