import React, { useState, useEffect, useRef } from "react";
import { sendMessageToJamAI } from "../services/jamAI.service";
import { Mic, Send } from "lucide-react";

export default function ChatPanel({ onClose }) {
  const [messages, setMessages] = useState([
    { sender: "ai", text: "Hi! I'm your SolarAid Assistant. Ask me about energy donations, recipients, impact calculations, or Shariah compliance. How can I help you today? 😊" }
  ]);

  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef(null);

  // Auto scroll on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  /**
   * MESSAGE HANDLER
   * Manages the complete flow of sending user message and receiving AI response
   * Connects to Jam AI backend with 7-step processing:
   * Extraction -> Legality Check -> Recipient Matching -> Impact Calculation -> Shariah Verification
   */
  async function sendMessage() {
    if (!input.trim() || isLoading) return;

    // Step 1: Add user message to UI immediately
    const userMessage = input;
    setMessages((prev) => [...prev, { sender: "user", text: userMessage }]);
    setInput("");

    // Step 2: Set loading state to show typing indicator
    setIsLoading(true);

    try {
      // Step 3: Call the Jam AI API (processes through 7 backend steps)
      const aiResponse = await sendMessageToJamAI(userMessage);

      // Step 4: Add AI response to UI
      setMessages((prev) => [
        ...prev,
        { sender: "ai", text: aiResponse }
      ]);
    } catch (error) {
      // Step 5: Handle errors gracefully
      console.error("Chat error:", error);
      
      let errorMessage = "Sorry, I couldn't connect to the server right now. Please try again in a moment. 🙏";
      
      // Provide more specific error messages when possible
      if (error.message.includes("Authentication")) {
        errorMessage = "Authentication error. Please contact support to verify your API credentials.";
      } else if (error.message.includes("timeout")) {
        errorMessage = "The request took too long. Please try with a shorter message or try again later.";
      }
      
      setMessages((prev) => [
        ...prev,
        { 
          sender: "ai", 
          text: errorMessage
        }
      ]);
    } finally {
      // Step 6: Reset loading state
      setIsLoading(false);
    }
  }

  return (
    <div
        className="
            fixed right-0 top-16   /* start BELOW the navbar */
            h-[calc(100vh-4rem)]  /* full height minus navbar height */
            w-[30%]
            bg-white shadow-xl z-[9999]
            flex flex-col border-l border-gray-200
        "
    >
      
      {/* Close button */}
      <div className="p-4 border-b flex justify-between items-center">
        <h2 className="text-xl font-semibold text-[#6C00FF]">SolarAid Assistant</h2>
        <button onClick={onClose} className="text-[#6C00FF] hover:text-black text-xl">
          ✕
        </button>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
            
            {/* AI Message */}
            {msg.sender === "ai" ? (
              <div className="max-w-[75%] bg-gray-100 text-black px-4 py-3 rounded-xl rounded-tl-sm shadow-sm">
                {msg.text}
              </div>
            ) : (
              /* USER MESSAGE (GRADIENT) */
              <div className="
                max-w-[75%] text-white px-4 py-3 rounded-xl rounded-tr-sm shadow-md
                bg-gradient-to-r from-[#3BA0FF] via-[#5A32FF] to-[#6C00FF]
              ">
                {msg.text}
              </div>
            )}

          </div>
        ))}

        {/* Typing Indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="max-w-[75%] bg-gray-100 text-black px-4 py-3 rounded-xl rounded-tl-sm shadow-sm">
              <div className="flex items-center gap-1">
                <span className="text-sm text-gray-600">Processing your request</span>
                <span className="flex gap-1 ml-1">
                  <span className="w-2 h-2 bg-[#6C00FF] rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></span>
                  <span className="w-2 h-2 bg-[#6C00FF] rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></span>
                  <span className="w-2 h-2 bg-[#6C00FF] rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></span>
                </span>
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef}></div>
      </div>

      {/* Input bar */}
      <div className="p-4 border-t bg-white flex items-center gap-2">
        <input
          className="flex-1 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C00FF] disabled:bg-gray-50 disabled:cursor-not-allowed"
          placeholder={isLoading ? "Processing..." : "Ask something..."}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !isLoading && sendMessage()}
          disabled={isLoading}
        />

        <button
          onClick={sendMessage}
          disabled={isLoading || !input.trim()}
          className="px-5 py-3 bg-[#6C00FF] text-white rounded-lg hover:bg-[#5A32FF] transition disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          {isLoading ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
}
