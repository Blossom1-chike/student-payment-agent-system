"use client"

import type React from "react"
import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Paperclip, Send, X } from "lucide-react"
import { NorthumbriaLogo } from "@/components/northumbria-logo"
import { WelcomeScreen } from "@/components/welcome-screen"
import { ChatMessage } from "@/components/chat-message"
import { sendChat } from "@/hooks/send-chat"
import Image from 'next/image'

type MessageType = "AIMessage" | "HumanMessage";

export interface Message {
  type: MessageType
  content: string
}


export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [attachedFile, setAttachedFile] = useState<File | null>(null)
  const [inputValue, setInputValue] = useState("")
  const fileInputRef = useRef<HTMLInputElement>(null)
  const scrollRef = useRef<HTMLDivElement>(null)
  const [uploading, setUploading] = useState(false);
  const [threadId, setThreadId] = useState(""); // Store ID here
  const [state, setState] = useState<any>({});

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setAttachedFile(file)
    }
  }

  const removeAttachment = () => {
    setAttachedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!inputValue.trim()) return // Must have input or file

    let userMessageContent = inputValue; // Default to input text
    if (attachedFile) userMessageContent = attachedFile.name + (inputValue ? `: ${inputValue}` : "");  // If file attached, show filename and optional caption

    const newMessages = [...messages, { type: "HumanMessage" as MessageType, content: userMessageContent }]; //declare the new messages to be sent to the API
    setMessages(newMessages); //optimistically update the UI with the new message

    // set loading States
    setIsLoading(true)
    setInputValue("");

    if (attachedFile) setUploading(true); //if there's a file, set uploading to true

    try {
      const textToSend = attachedFile ? (inputValue || "Uploaded ID image.") : inputValue; //if there's a file, send the input as caption or default text

      const data = await sendChat(textToSend, state, threadId, attachedFile); //send the chat to the API

      if (data.thread_id) setThreadId(data.thread_id); //store the thread ID if we get one back

      setMessages([...newMessages, { type: "AIMessage" as MessageType, content: data.response }]); //update messages with the AI response
      setState(data.state); //update the state with the returned state
    } catch (error) {
      console.error("Error sending message:", error)
      const errorMessage: Message = {
        type: "AIMessage",
        content: "Sorry, I encountered an error. Please try again.",
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setUploading(false);
      setIsLoading(false)
      setAttachedFile(null)
      if (fileInputRef.current) {
        fileInputRef.current.value = ""
      }
    }
  }

  const showWelcome = messages.length === 0 // Show welcome screen if no messages yet

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <header className="border-b bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Image src={`/logo.svg`} alt={"Northumbria Logo"} width="40" height="40" />
            <div>
              <h1 className="text-lg font-semibold text-foreground">AskNorthumbria</h1>
              <p className="text-sm text-muted-foreground">Your 24/7 Student Assistant</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-xs text-muted-foreground hidden sm:inline">Online</span>
          </div>
        </div>
      </header>

      {/* Chat Area */}
      <div className="flex-1 overflow-hidden">
        <ScrollArea ref={scrollRef} className="h-full">
          <div className="max-w-4xl mx-auto px-4 py-6">
            {showWelcome ? (
              <WelcomeScreen />
            ) : (
              <div className="space-y-6">
                {messages.map((message, id) => (
                  <ChatMessage key={id} message={message} />
                ))}
                {isLoading && (
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <div className="flex gap-1">
                      <div className="h-2 w-2 rounded-full bg-primary animate-bounce [animation-delay:-0.3s]" />
                      <div className="h-2 w-2 rounded-full bg-primary animate-bounce [animation-delay:-0.15s]" />
                      <div className="h-2 w-2 rounded-full bg-primary animate-bounce" />
                    </div>
                    <span className="text-sm">AskNorthumbria is thinking...</span>
                  </div>
                )}
              </div>
            )}
          </div>
        </ScrollArea>
      </div>

      {/* Input Area */}
      <div className="border-t bg-card/50 backdrop-blur-sm">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <form onSubmit={onSubmit} className="space-y-3">
            {attachedFile && (
              <Card className="p-3 flex items-center justify-between bg-accent/50 animate-in slide-in-from-bottom-2">
                <div className="flex items-center gap-2">
                  <Paperclip className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm text-foreground truncate max-w-[200px]">{attachedFile.name}</span>
                  <span className="text-xs text-muted-foreground">({(attachedFile.size / 1024).toFixed(1)} KB)</span>
                </div>
                <Button type="button" variant="ghost" size="icon" onClick={removeAttachment} className="h-6 w-6">
                  <X className="h-4 w-4" />
                </Button>
              </Card>
            )}
            <div className="flex items-end gap-2">
              <div className="flex-1 relative">
                <Input
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="Ask about payments, appointments, courses, or anything else..."
                  className="pr-10 min-h-[44px] text-base resize-none bg-background"
                  disabled={isLoading}
                />
                <input
                  ref={fileInputRef}
                  type="file"
                  onChange={handleFileSelect}
                  className="hidden"
                  accept=".pdf,.doc,.docx,.txt,.png,.jpg,.jpeg"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={() => fileInputRef.current?.click()}
                  className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8 text-muted-foreground hover:text-foreground"
                  disabled={isLoading}
                >
                  <Paperclip className="h-4 w-4" />
                </Button>
              </div>
              <Button
                type="submit"
                size="icon"
                className="h-11 w-11 rounded-full bg-primary hover:bg-primary/90 transition-all hover:scale-105"
                disabled={!inputValue.trim() || isLoading}
              >
                <Send className="h-5 w-5" />
              </Button>
            </div>
          </form>
          <p className="text-xs text-center text-muted-foreground mt-3">
            AskNorthumbria can help with payments, appointments, courses, and general enquiries
          </p>
        </div>
      </div>
    </div>
  )
}
