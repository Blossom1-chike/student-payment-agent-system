"use client"

import { Card } from "@/components/ui/card"
import { Avatar } from "@/components/ui/avatar"
import { Bot, User } from "lucide-react"
import { Message } from "./chat-interface"

interface ChatMessageProps {
  message: Message
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.type === "HumanMessage"

  return (
    <div className={`flex gap-3 animate-in slide-in-from-bottom-2 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <Avatar className="h-8 w-8 border-2 border-primary/20">
          <div className="h-full w-full bg-primary/10 flex items-center justify-center">
            <Bot className="h-5 w-5 text-primary" />
          </div>
        </Avatar>
      )}
      <Card
        className={`max-w-[85%] md:max-w-[75%] p-4 ${
          isUser ? "bg-primary text-primary-foreground" : "bg-card border-border"
        }`}
      >
        <div className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</div>
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
