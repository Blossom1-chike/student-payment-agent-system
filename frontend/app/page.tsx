"use client";

import { useState } from "react";
import ChatBubble from "./components/ChatBubble";
import UploadID from "./components/UploadID";
import { sendChat } from "./utils/api";

type MessageType = "AIMessage" | "HumanMessage";

export default function ChatPage() {
  const [messages, setMessages] = useState<{ type: MessageType; content: string }[]>([]);
  const [state, setState] = useState<any>({});
  const [threadId, setThreadId] = useState(""); // Store ID here
  const [input, setInput] = useState<string>("");
  const [uploading, setUploading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [file, setFile] = useState<File>(null as unknown as File);

  const handleSend = async () => {
    // 1. Validate: Must have either text OR file
    if (!input.trim() && !file) return;

    // 2. Prepare Optimistic UI Message
    let userMessageContent = input;
    if (file) userMessageContent = file.name + (input ? `: ${input}` : "");

    const newMessages = [...messages, { type: "HumanMessage" as MessageType, content: userMessageContent }];
    setMessages(newMessages);

    // 3. Set Loading States
    setIsTyping(true);
    setInput(""); // Clear text input immediately
    if (file) setUploading(true);

    try {
      // 4. Send Request (Pass text AND file if exists)
      // If file exists, we use "Uploaded ID..." or the actual input?
      // Usually, you pass the 'input' as the caption for the file.
      const textToSend = file ? (input || "Uploaded ID image.") : input;

      const data = await sendChat(textToSend, state, threadId, file);

      if (data.thread_id) setThreadId(data.thread_id);
      setMessages([...newMessages, { type: "AIMessage" as MessageType, content: data.response }]);
      setState(data.state);

    } catch (e) {
      console.error(e);
    } finally {
      setIsTyping(false);
      setUploading(false);
      setFile(null as unknown as File); // Reset file
    }
  };

  const handleUpload = async () => {
    setUploading(true);

    const newMessages = [...messages, { type: "HumanMessage" as MessageType, content: `Uploaded ID image, ${input}` }];
    setMessages(newMessages);

    const data = await sendChat("Uploaded ID image.", state, threadId, file);
    setMessages([...newMessages, { type: "AIMessage" as MessageType, content: data.response }]);
    setState(data.state);

    setUploading(false);
  };

  return (
    <div className="flex flex-col items-center p-4 h-screen">
      <h1 className="font-bold text-2xl pb-3">AskNorthumbria Agent</h1>
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

        <UploadID onUpload={(file) => {
          console.log("File selected:", file);
          setFile(file);
        }} />

        {uploading && <p className="text-sm text-gray-500">Uploading...</p>}
      </div>
    </div>
  );
}
