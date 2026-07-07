"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Send, Loader2, Bot, User, AlertCircle, LogOut } from "lucide-react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  toolUsed?: string;
  timestamp: Date;
  error?: boolean;
}

const SUGGESTIONS = [
  "Who should I call today?",
  "How is RAINCO doing?",
  "Show outstanding bills in Welimada",
  "Tell me about Janalanka Textile",
  "Any bounced cheques?",
  "Show all Platinum customer bills",
];

// Renders **bold** markdown inline, preserving other text as-is
function renderInline(text: string): React.ReactNode[] {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    return part;
  });
}

// Renders a full message string with line breaks and inline bold
function MessageContent({ content }: { content: string }) {
  const lines = content.split("\n");
  return (
    <div className="text-sm leading-relaxed space-y-1">
      {lines.map((line, i) => (
        <p key={i} className={line === "" ? "h-2" : ""}>
          {renderInline(line)}
        </p>
      ))}
    </div>
  );
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const router = useRouter();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: text.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_AI_API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text.trim() }),
      });

      if (!res.ok) throw new Error("Failed to get response");

      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: data.response,
          toolUsed: data.tool_used,
          timestamp: new Date(),
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: "Sorry, I could not connect to the AI service. Please try again.",
          timestamp: new Date(),
          error: true,
        },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  const handleLogout = async () => {
    await fetch("/api/auth", { method: "DELETE" });
    router.push("/login");
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center gap-3 px-6 py-4 border-b border-gray-800 bg-gray-900">
        <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-blue-600">
          <Bot size={20} className="text-white" />
        </div>
        <div>
          <h1 className="text-white font-semibold text-sm">ERP Copilot</h1>
          <p className="text-gray-400 text-xs">Ghanim Enterprises</p>
        </div>
        <div className="ml-auto flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-500"></span>
            <span className="text-gray-400 text-xs">Online</span>
          </div>
          <button
            onClick={handleLogout}
            title="Sign out"
            className="text-gray-500 hover:text-gray-300 transition-colors duration-200"
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full gap-8">
            <div className="text-center">
              <div className="flex items-center justify-center w-16 h-16 rounded-2xl bg-blue-600 mx-auto mb-4">
                <Bot size={32} className="text-white" />
              </div>
              <h2 className="text-white text-xl font-semibold mb-2">ERP Copilot</h2>
              <p className="text-gray-400 text-sm max-w-sm">
                Ask me anything about your business — outstanding bills,
                customer profiles, collections, and more.
              </p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-lg">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => sendMessage(s)}
                  className="text-left px-4 py-3 rounded-xl border border-gray-700
                             bg-gray-900 hover:bg-gray-800 hover:border-gray-600
                             text-gray-300 text-sm transition-all duration-200"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            {msg.role === "assistant" && (
              <div className="shrink-0 w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center mt-1">
                <Bot size={16} className="text-white" />
              </div>
            )}

            <div
              className={`max-w-[75%] rounded-2xl px-4 py-3 ${
                msg.role === "user"
                  ? "bg-blue-600 text-white rounded-tr-sm"
                  : msg.error
                    ? "bg-red-950 border border-red-800 text-red-300 rounded-tl-sm"
                    : "bg-gray-800 text-gray-100 rounded-tl-sm"
              }`}
            >
              {msg.error && (
                <div className="flex items-center gap-2 mb-2">
                  <AlertCircle size={14} className="text-red-400" />
                  <span className="text-red-400 text-xs font-medium">Connection Error</span>
                </div>
              )}

              {msg.toolUsed && (
                <div className="mb-2">
                  <span className="text-xs bg-blue-900 text-blue-300 px-2 py-0.5 rounded-full">
                    {msg.toolUsed}
                  </span>
                </div>
              )}

              {msg.role === "assistant" ? (
                <MessageContent content={msg.content} />
              ) : (
                <p className="text-sm leading-relaxed">{msg.content}</p>
              )}

              <div className={`text-xs mt-2 ${msg.role === "user" ? "text-blue-200" : "text-gray-500"}`}>
                {msg.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              </div>
            </div>

            {msg.role === "user" && (
              <div className="shrink-0 w-8 h-8 rounded-lg bg-gray-700 flex items-center justify-center mt-1">
                <User size={16} className="text-gray-300" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex gap-3 justify-start">
            <div className="shrink-0 w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
              <Bot size={16} className="text-white" />
            </div>
            <div className="bg-gray-800 rounded-2xl rounded-tl-sm px-4 py-3">
              <Loader2 size={16} className="text-gray-400 animate-spin" />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="px-4 py-4 border-t border-gray-800 bg-gray-900">
        <div className="flex gap-3 items-end max-w-4xl mx-auto">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about your business..."
            rows={1}
            className="flex-1 bg-gray-800 text-white placeholder-gray-500
                       rounded-xl px-4 py-3 text-sm resize-none
                       border border-gray-700 focus:border-blue-500
                       focus:outline-none focus:ring-1 focus:ring-blue-500
                       transition-colors duration-200 max-h-32"
            style={{ minHeight: "44px" }}
          />
          <button
            onClick={() => sendMessage(input)}
            disabled={!input.trim() || loading}
            className="shrink-0 w-11 h-11 rounded-xl bg-blue-600
                       hover:bg-blue-500 disabled:bg-gray-700
                       disabled:cursor-not-allowed flex items-center
                       justify-center transition-colors duration-200"
          >
            <Send size={16} className="text-white" />
          </button>
        </div>
        <p className="text-gray-600 text-xs text-center mt-2">
          Press Enter to send · Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
