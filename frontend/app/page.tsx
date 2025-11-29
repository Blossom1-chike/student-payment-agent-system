"use client";

import { useState } from "react";
import ChatBubble from "./components/ChatBubble";
import UploadID from "./components/UploadID";
import { sendChat } from "./utils/api";

type MessageType = "AIMessage" | "HumanMessage";

export default function ChatPage() {
  const [messages, setMessages] = useState<{ type: MessageType; content: string }[]>([]);
  const [state, setState] = useState<any>({});
  const [input, setInput] = useState<string>("");
  const [uploading, setUploading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { type: "HumanMessage" as MessageType, content: input }];
    setMessages(newMessages);
    setInput("");
    setIsTyping(true);  // start typing animation

    const data = await sendChat(input, state);
    console.log("Received data:", data);
    setMessages([...newMessages, { type: "AIMessage" as MessageType, content: data.response }]);
    setState(data.state);
    setIsTyping(false); // stop typing animation
  };

  const handleUpload = async (file: File) => {
    setUploading(true);

    const newMessages = [...messages, { type: "HumanMessage" as MessageType, content: "Uploaded ID image." }];
    setMessages(newMessages);

    const data = await sendChat("Uploaded ID image.", state, file);
    setMessages([...newMessages, { type: "AIMessage" as MessageType, content: data.response }]);
    setState(data.state);

    setUploading(false);
  };

  return (
    <div className="flex flex-col items-center p-4 h-screen">
      <div className="flex-1 w-full max-w-xl border rounded p-4 overflow-y-auto flex flex-col">
        {messages.map((m, i) => (
          <ChatBubble key={i} role={m.type} content={m.content} />
        ))}
        {isTyping && (
          <div className="flex items-center gap-2 mt-2 self-start">
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-300"></div>
            <span className="text-gray-500 text-sm">Agent is typing...</span>
          </div>
        )}

      </div>

      <div className="mt-4 flex flex-col w-full max-w-xl gap-2">
        <div className="flex gap-2">
          <input
            type="text"
            className="flex-1 border p-2 rounded"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message..."
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
          />
          <button onClick={handleSend} className="bg-blue-600 text-white px-4 py-2 rounded">
            Send
          </button>
        </div>

        <UploadID onUpload={handleUpload} />

        {uploading && <p className="text-sm text-gray-500">Uploading...</p>}
      </div>
    </div>
  );
}
