"use client"

import { Card } from "@/components/ui/card"
import { Avatar } from "@/components/ui/avatar"
import { Bot, User } from "lucide-react"
import { Message } from "./chat-interface"

interface ChatMessageProps {
  message: Message
}

const formatMessage = (text: string) => {
  const urlRegex = /(https?:\/\/[^\s]+)/g;
  const parts = text.split(urlRegex);

  return parts.map((part, index) => {
    if (part.startsWith("http")) {
      // Remove trailing punctuation
      const cleanUrl = part.replace(/[),.!?]+$/, "");
      const trailing = part.slice(cleanUrl.length);

      return (
        <span key={index}>
          <a
            href={cleanUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 underline font-semibold break-all"
          >
            {cleanUrl}
          </a>
          {trailing}
        </span>
      );
    }

    return part;
  });
};


export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.type === "HumanMessage"

  return (
    <div className={`flex gap-3 text-wrap animate-in slide-in-from-bottom-2 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <Avatar className="h-8 w-8 border-2 border-primary/20">
          <div className="h-full w-full bg-primary/10 flex items-center justify-center">
            <Bot className="h-5 w-5 text-primary" />
          </div>
        </Avatar>
      )}
      <Card
        className={`max-w-[85%] md:max-w-[75%] py-2 px-4 ${
          isUser ? "bg-primary text-primary-foreground" : "bg-card border-border"
        }`}
      >
        <div className="text-sm wrap-anywhere leading-relaxed whitespace-pre-wrap">{formatMessage(message.content)}</div>
      </Card>
      {isUser && (
        <Avatar className="h-8 w-8 border-2 border-primary/20">
          <div className="h-full w-full bg-secondary flex items-center justify-center">
            <User className="h-5 w-5 text-secondary-foreground" />
          </div>
        </Avatar>
      )}
    </div>
  )
}
