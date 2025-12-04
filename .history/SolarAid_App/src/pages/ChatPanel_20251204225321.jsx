import React, { useState, useEffect, useRef } from "react";
import { sendMessageToJamAI, sendAudioToBackend } from "../services/jamAI.service";
import { Mic, Send } from "lucide-react";

export default function ChatPanel({ onClose }) {
  const [messages, setMessages] = useState([
    { sender: "ai", text: "Hi! I'm your SolarAid Assistant. Ask me about energy donations, recipients, impact calculations, or Shariah compliance. How can I help you today? 😊" }
  ]);

  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const bottomRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

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

  /**
   * VOICE RECORDING HANDLER
   * Toggles audio recording on/off using MediaRecorder API
   * When stopped, sends audio to backend for AssemblyAI transcription + RAG processing
   */
  async function toggleRecording() {
    if (isRecording) {
      // Stop recording
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
        mediaRecorderRef.current.stop();
      }
    } else {
      // Start recording
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        audioChunksRef.current = [];

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data);
          }
        };

        mediaRecorder.onstop = async () => {
          // Stop all audio tracks
          stream.getTracks().forEach(track => track.stop());

          // Create audio blob
          const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
          
          // Send to backend for processing using the service
          await handleAudioSend(audioBlob);
          
          // Reset recording state
          setIsRecording(false);
        };

        mediaRecorder.start();
        setIsRecording(true);
      } catch (error) {
        console.error("Error accessing microphone:", error);
        setMessages((prev) => [
          ...prev,
          { 
            sender: "ai", 
            text: "Sorry, I couldn't access your microphone. Please check your browser permissions and try again." 
          }
        ]);
      }
    }
  }

  /**
   * AUDIO MESSAGE HANDLER
   * Sends recorded audio to /api/chat-enquiry endpoint
   * Backend handles AssemblyAI transcription + JamAI RAG processing
   */
  async function sendAudioMessage(audioBlob) {
    setIsLoading(true);

    try {
      // Add user message indicator
      setMessages((prev) => [...prev, { sender: "user", text: "🎤 Voice message" }]);

      // Prepare FormData with audio file
      const formData = new FormData();
      formData.append("audio", audioBlob, "recording.webm");

      // Debug: Log FormData contents
      console.log("📤 Sending audio to backend:");
      console.log("- Blob size:", audioBlob.size, "bytes");
      console.log("- Blob type:", audioBlob.type);
      console.log("- Filename: recording.webm");

      // Send to backend
      const response = await fetch("http://127.0.0.1:5000/api/chat-enquiry", {
        method: "POST",
        body: formData,
      });

      // Debug: Log response status
      console.log("📥 Backend response status:", response.status);

      if (!response.ok) {
        // Try to get error details from response
        const errorText = await response.text();
        console.error("❌ Backend error response:", errorText);
        throw new Error(`Server error: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      console.log("✅ Backend response data:", data);

      // Add AI response to chat
      setMessages((prev) => [
        ...prev,
        { 
          sender: "ai", 
          text: data.response || "I processed your voice message successfully! 🎉" 
        }
      ]);
    } catch (error) {
      console.error("❌ Audio message error:", error);
      
      // More detailed error message
      let errorMsg = "Sorry, I couldn't process your voice message. ";
      if (error.message.includes("500")) {
        errorMsg += "The server encountered an internal error. Please check the Flask terminal for details.";
      } else if (error.message.includes("Failed to fetch")) {
        errorMsg += "Cannot connect to the backend server. Is it running on port 5000?";
      } else {
        errorMsg += "Please try typing your question instead. 🙏";
      }
      
      setMessages((prev) => [
        ...prev,
        { 
          sender: "ai", 
          text: errorMsg
        }
      ]);
    } finally {
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
              <div className="max-w-[75%] bg-gray-100 text-black px-4 py-3 rounded-xl rounded-tl-sm shadow-sm whitespace-pre-wrap">
                {msg.text}
              </div>
            ) : (
              /* USER MESSAGE (GRADIENT) */
              <div className="
                max-w-[75%] text-white px-4 py-3 rounded-xl rounded-tr-sm shadow-md
                bg-gradient-to-r from-[#3BA0FF] via-[#5A32FF] to-[#6C00FF]
                whitespace-pre-wrap
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

      {/* WhatsApp-style Input bar */}
      <div className="p-4 border-t bg-white flex items-center gap-3">
        {/* Input container with gray background */}
        <div className="flex-1 bg-gray-100 rounded-full px-5 py-2 flex items-center">
          <input
            className="flex-1 bg-transparent outline-none text-gray-800 placeholder-gray-500 disabled:cursor-not-allowed"
            placeholder={isRecording ? "Recording..." : isLoading ? "Processing..." : "Type a message..."}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !isLoading && !isRecording && input.trim() && sendMessage()}
            disabled={isLoading || isRecording}
          />
        </div>

        {/* Circular button - Mic or Send based on input */}
        <button
          onClick={input.trim() ? sendMessage : toggleRecording}
          disabled={isLoading}
          className={`w-12 h-12 rounded-full text-white flex items-center justify-center transition shadow-md ${
            isRecording 
              ? "bg-red-500 hover:bg-red-600 animate-pulse" 
              : "bg-[#6C00FF] hover:bg-[#5A32FF]"
          } disabled:bg-gray-300 disabled:cursor-not-allowed`}
        >
          {isLoading ? (
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          ) : input.trim() ? (
            <Send size={20} />
          ) : (
            <Mic size={20} />
          )}
        </button>
      </div>
    </div>
  );
}
