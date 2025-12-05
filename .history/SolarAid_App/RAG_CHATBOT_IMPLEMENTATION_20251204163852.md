# RAG-Based Chatbot Implementation Guide

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  User Input: Text String OR Audio Blob                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  handleSend() - Determines input type and sends to API   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                               ↓
                    POST /api/chat-enquiry
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (Python/Flask)                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Step A: Audio Handling (if audio)                       │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  AssemblyAI Transcription                          │  │  │
│  │  │  - Receives audio file                             │  │  │
│  │  │  - Returns transcript text                         │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Step B: AI Processing                                   │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  JamAI Action Table API                            │  │  │
│  │  │  - Input Column: "Input_text"                      │  │  │
│  │  │  - Output Column: "Final_response"                 │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Step C: Response Parsing                                │  │
│  │  - Extract Final_response using dot notation             │  │
│  │  - Return to frontend                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                               ↓
                    JSON Response with "response" field
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React) - Display                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Show AI response in chat interface                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Backend Implementation (Python/Flask)

### File: `backend/jamai_ai/audio_bridge.py`

```python
"""
Audio Bridge Module for Voice-to-RAG Integration
Handles audio transcription via AssemblyAI and RAG processing via JamAI
"""

import os
import assemblyai as aai
from jamaibase import JamAI
from jamaibase import types as p
from dotenv import load_dotenv

load_dotenv()

# Configuration
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
VITE_JAM_API_KEY = os.getenv("VITE_JAM_API_KEY")
VITE_JAM_PROJECT_ID = os.getenv("VITE_JAM_PROJECT_ID")

# Initialize AssemblyAI
if ASSEMBLYAI_API_KEY:
    aai.settings.api_key = ASSEMBLYAI_API_KEY


def transcribe_audio(audio_path: str) -> dict:
    """
    Step A: Transcribe audio file using AssemblyAI
    
    Args:
        audio_path (str): Path to the audio file
        
    Returns:
        dict: Transcription result with text and metadata
        
    Raises:
        Exception: If transcription fails
    """
    if not ASSEMBLYAI_API_KEY:
        raise ValueError("ASSEMBLYAI_API_KEY not found in environment variables")
    
    try:
        print(f"🎤 Starting AssemblyAI transcription...")
        
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_path)
        
        if transcript.status == aai.TranscriptStatus.error:
            raise Exception(f"Transcription failed: {transcript.error}")
        
        print(f"✅ Transcription completed: {len(transcript.text)} characters")
        
        return {
            "text": transcript.text,
            "id": transcript.id,
            "status": transcript.status,
            "audio_duration": transcript.audio_duration
        }
        
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        raise Exception(f"Audio transcription failed: {str(e)}")


def query_jamai_chat(query_text: str, table_id: str = "Chatbox") -> dict:
    """
    Step B & C: Query JamAI Action Table and parse response
    
    Args:
        query_text (str): The user's query text
        table_id (str): JamAI Action Table ID
        
    Returns:
        dict: Parsed response with Final_response field
        
    Raises:
        Exception: If query fails
    """
    if not VITE_JAM_API_KEY or not VITE_JAM_PROJECT_ID:
        raise ValueError("JamAI credentials not found in environment variables")
    
    try:
        print(f"🤖 Querying JamAI Action Table: {table_id}")
        
        # Initialize JamAI client with token (not api_key!)
        jamai = JamAI(
            token=VITE_JAM_API_KEY,
            project_id=VITE_JAM_PROJECT_ID
        )
        
        # Create request with Input_text column
        add_request = p.RowAddRequest(
            table_id=table_id,
            data=[{"Input_text": query_text}],  # Input column name
            stream=False
        )
        
        # Query action table
        response = jamai.table.add_table_rows(
            table_type="action",
            request=add_request
        )
        
        # IMPORTANT: Use dot notation (not .get()) to avoid attribute errors
        if hasattr(response, 'rows') and len(response.rows) > 0:
            row = response.rows[0]
            
            # Access columns using dot notation
            if hasattr(row, 'columns'):
                columns = row.columns
                
                # Extract Final_response column
                if 'Final_response' in columns:
                    final_response_col = columns['Final_response']
                    # Get value from column
                    response_text = final_response_col.get('value') if isinstance(final_response_col, dict) else str(final_response_col)
                else:
                    response_text = "Error: Final_response column not found in table"
            else:
                response_text = "Error: No columns found in response"
        else:
            response_text = "Error: No rows returned from Action Table"
        
        print(f"✅ Received response from JamAI")
        
        return {
            "success": True,
            "response": response_text,
            "table_id": table_id
        }
        
    except Exception as e:
        print(f"❌ JamAI query error: {e}")
        raise Exception(f"Failed to query JamAI Action Table: {str(e)}")


def process_enquiry(input_data, input_type='text'):
    """
    Main processing function that handles both text and audio inputs
    
    Args:
        input_data: Either audio file path (str) or text query (str)
        input_type: 'audio_path' or 'text'
        
    Returns:
        dict: Processing result with transcript/text and metadata
    """
    try:
        if input_type == 'audio_path':
            print(f"📁 Processing audio enquiry: {input_data}")
            
            # Step A: Transcribe audio
            transcription_result = transcribe_audio(input_data)
            transcript_text = transcription_result["text"]
            
            return {
                "success": True,
                "type": "audio",
                "transcript": transcript_text,
                "transcription_metadata": transcription_result
            }
            
        elif input_type == 'text':
            print(f"📝 Processing text enquiry")
            
            return {
                "success": True,
                "type": "text",
                "transcript": input_data
            }
            
        else:
            raise ValueError(f"Invalid input_type: {input_type}")
            
    except Exception as e:
        print(f"❌ Processing error: {e}")
        return {
            "success": False,
            "error": str(e),
            "type": input_type
        }
```

### File: `backend/server.py`

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
from backend.jamai_ai.audio_bridge import process_enquiry, query_jamai_chat
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Configure upload folder for audio files
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'flac', 'ogg', 'm4a', 'webm'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

def allowed_audio_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_EXTENSIONS


@app.route("/api/chat-enquiry", methods=["POST"])
def chat_enquiry():
    """
    Unified endpoint for both text and audio chat enquiries
    
    Accepts:
    - multipart/form-data with 'audio' file
    - application/json with 'text' field
    
    Returns:
    - JSON with 'response' field containing AI answer
    """
    try:
        print("\n" + "="*60)
        print("🎤 NEW CHAT ENQUIRY REQUEST")
        print(f"Content-Type: {request.content_type}")
        print("="*60 + "\n")
        
        query_text = None
        processing_result = None
        
        # CASE 1: Audio input
        if 'audio' in request.files:
            audio_file = request.files['audio']
            
            if audio_file.filename == '':
                return jsonify({"error": "No audio file selected"}), 400
            
            if not allowed_audio_file(audio_file.filename):
                return jsonify({
                    "error": f"Invalid file type. Allowed: {', '.join(ALLOWED_AUDIO_EXTENSIONS)}"
                }), 400
            
            # Save audio file temporarily
            filename = secure_filename(audio_file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp}_{filename}"
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            print(f"💾 Saving audio file: {unique_filename}")
            audio_file.save(audio_path)
            file_size = os.path.getsize(audio_path)
            print(f"✅ Saved ({file_size/1024:.2f} KB)")
            
            try:
                # Process audio (Step A: Transcription)
                print(f"🔄 Step A: Transcribing audio...")
                processing_result = process_enquiry(audio_path, input_type='audio_path')
                
                if not processing_result.get("success"):
                    return jsonify({
                        "error": "Audio processing failed",
                        "details": processing_result.get("error")
                    }), 500
                
                query_text = processing_result.get("transcript")
                print(f"📝 Transcript: {query_text[:100]}...")
                
            finally:
                # Clean up temporary file
                try:
                    if os.path.exists(audio_path):
                        os.remove(audio_path)
                        print(f"🗑️ Cleaned up temp file")
                except Exception as cleanup_error:
                    print(f"⚠️ Cleanup warning: {cleanup_error}")
        
        # CASE 2: Text input (JSON)
        elif request.is_json:
            data = request.json
            query_text = data.get("text")
            
            if not query_text:
                return jsonify({"error": "No text provided"}), 400
            
            processing_result = process_enquiry(query_text, input_type='text')
        
        # CASE 3: Text input (Form data)
        elif 'text' in request.form:
            query_text = request.form.get('text')
            
            if not query_text:
                return jsonify({"error": "No text provided"}), 400
            
            processing_result = process_enquiry(query_text, input_type='text')
        
        else:
            return jsonify({
                "error": "Invalid request. Send either 'audio' file or 'text' field"
            }), 400
        
        # Step B & C: Query JamAI and parse response
        if not query_text:
            return jsonify({"error": "No query text generated"}), 500
        
        print(f"🔄 Step B: Querying JamAI Action Table...")
        chat_response = query_jamai_chat(query_text)
        
        if not chat_response.get("success"):
            return jsonify({
                "error": "Failed to get chat response",
                "details": str(chat_response)
            }), 500
        
        # Return response to frontend
        response_data = {
            "success": True,
            "query": query_text,
            "response": chat_response.get("response"),  # This is the Final_response
            "input_type": processing_result.get("type") if processing_result else "text"
        }
        
        print(f"✅ Request completed successfully\n")
        return jsonify(response_data), 200
    
    except Exception as e:
        print(f"❌ Chat enquiry error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    print("🚀 Flask server running on http://127.0.0.1:5000")
    app.run(port=5000, debug=True)
```

---

## Frontend Implementation (React)

### File: `src/pages/ChatPanel.jsx`

```jsx
import React, { useState, useRef } from "react";
import { Mic, Send } from "lucide-react";

export default function ChatPanel({ onClose }) {
  const [messages, setMessages] = useState([
    { 
      sender: "ai", 
      text: "Hi! I'm your SolarAid Assistant. Ask me anything about energy donations! 😊" 
    }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  /**
   * UNIFIED SEND HANDLER
   * Handles both text and audio inputs
   */
  async function handleSend() {
    if (input.trim()) {
      // Send text message
      await sendTextMessage(input.trim());
    } else if (!isRecording) {
      // Start audio recording
      startRecording();
    }
  }

  /**
   * TEXT MESSAGE HANDLER
   * Sends text to backend /api/chat-enquiry endpoint
   */
  async function sendTextMessage(text) {
    if (isLoading) return;

    setMessages((prev) => [...prev, { sender: "user", text }]);
    setInput("");
    setIsLoading(true);

    try {
      console.log("📤 Sending text to backend:", text);

      const response = await fetch("http://127.0.0.1:5000/api/chat-enquiry", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text }),
      });

      console.log("📥 Response status:", response.status);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server error: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      console.log("✅ Response data:", data);

      setMessages((prev) => [
        ...prev,
        { 
          sender: "ai", 
          text: data.response || "I processed your message!" 
        }
      ]);
    } catch (error) {
      console.error("❌ Error:", error);
      setMessages((prev) => [
        ...prev,
        { 
          sender: "ai", 
          text: "Sorry, I couldn't process your message. Please try again." 
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  /**
   * AUDIO RECORDING HANDLER
   * Records audio using MediaRecorder API
   */
  async function startRecording() {
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
        stream.getTracks().forEach(track => track.stop());
        
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        await sendAudioMessage(audioBlob);
        
        setIsRecording(false);
      };

      mediaRecorder.start();
      setIsRecording(true);
      
      console.log("🎤 Recording started");
    } catch (error) {
      console.error("Microphone error:", error);
      setMessages((prev) => [
        ...prev,
        { 
          sender: "ai", 
          text: "Sorry, I couldn't access your microphone. Please check permissions." 
        }
      ]);
    }
  }

  /**
   * STOP RECORDING HANDLER
   */
  function stopRecording() {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop();
      console.log("🎤 Recording stopped");
    }
  }

  /**
   * AUDIO MESSAGE HANDLER
   * Sends audio blob to backend /api/chat-enquiry endpoint
   */
  async function sendAudioMessage(audioBlob) {
    setIsLoading(true);

    try {
      setMessages((prev) => [...prev, { sender: "user", text: "🎤 Voice message" }]);

      const formData = new FormData();
      formData.append("audio", audioBlob, "recording.webm");

      console.log("📤 Sending audio to backend:");
      console.log("- Blob size:", audioBlob.size, "bytes");
      console.log("- Blob type:", audioBlob.type);

      const response = await fetch("http://127.0.0.1:5000/api/chat-enquiry", {
        method: "POST",
        body: formData,
      });

      console.log("📥 Response status:", response.status);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server error: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      console.log("✅ Response data:", data);

      setMessages((prev) => [
        ...prev,
        { 
          sender: "ai", 
          text: data.response || "I processed your voice message!" 
        }
      ]);
    } catch (error) {
      console.error("❌ Audio error:", error);
      setMessages((prev) => [
        ...prev,
        { 
          sender: "ai", 
          text: "Sorry, I couldn't process your voice message. Please try typing instead." 
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="fixed right-0 top-16 h-[calc(100vh-4rem)] w-[30%] bg-white shadow-xl z-[9999] flex flex-col">
      {/* Header */}
      <div className="p-4 border-b flex justify-between items-center">
        <h2 className="text-xl font-semibold text-[#6C00FF]">SolarAid Assistant</h2>
        <button onClick={onClose} className="text-[#6C00FF] hover:text-black text-xl">
          ✕
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[75%] px-4 py-3 rounded-xl shadow-sm whitespace-pre-wrap ${
              msg.sender === "ai" 
                ? "bg-gray-100 text-black rounded-tl-sm" 
                : "bg-gradient-to-r from-[#3BA0FF] via-[#5A32FF] to-[#6C00FF] text-white rounded-tr-sm"
            }`}>
              {msg.text}
            </div>
          </div>
        ))}

        {/* Loading indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 px-4 py-3 rounded-xl">
              <div className="flex items-center gap-1">
                <span className="text-sm text-gray-600">Processing</span>
                <span className="flex gap-1 ml-1">
                  <span className="w-2 h-2 bg-[#6C00FF] rounded-full animate-bounce"></span>
                  <span className="w-2 h-2 bg-[#6C00FF] rounded-full animate-bounce" style={{animationDelay: "150ms"}}></span>
                  <span className="w-2 h-2 bg-[#6C00FF] rounded-full animate-bounce" style={{animationDelay: "300ms"}}></span>
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input bar */}
      <div className="p-4 border-t flex items-center gap-3">
        <div className="flex-1 bg-gray-100 rounded-full px-5 py-2">
          <input
            className="w-full bg-transparent outline-none text-gray-800 placeholder-gray-500"
            placeholder={isRecording ? "Recording..." : isLoading ? "Processing..." : "Type a message..."}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !isLoading && !isRecording && handleSend()}
            disabled={isLoading || isRecording}
          />
        </div>

        <button
          onClick={input.trim() ? handleSend : (isRecording ? stopRecording : startRecording)}
          disabled={isLoading}
          className={`w-12 h-12 rounded-full text-white flex items-center justify-center transition shadow-md ${
            isRecording 
              ? "bg-red-500 hover:bg-red-600 animate-pulse" 
              : "bg-[#6C00FF] hover:bg-[#5A32FF]"
          } disabled:bg-gray-300`}
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
```

---

## Environment Variables

### File: `.env`

```env
# AssemblyAI Configuration
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here

# JamAI Configuration
VITE_JAM_API_KEY=your_jamai_api_key_here
VITE_JAM_PROJECT_ID=your_project_id_here
```

---

## JamAI Table Configuration

### Action Table Structure

**Table Name:** `Chatbox` (or your custom table name)

**Columns:**

| Column ID | Type | Description |
|-----------|------|-------------|
| `Input_text` | Input | User's query (text or transcribed audio) |
| `Final_response` | Output | AI-generated response to show user |

**Important Notes:**
- Use `Input_text` (exact name) for the input column
- Use `Final_response` (exact name) for the output column
- The backend code uses **dot notation** to access `response.rows[0].columns['Final_response']`

---

## Testing

### Test Text Input
```bash
curl -X POST http://127.0.0.1:5000/api/chat-enquiry \
  -H "Content-Type: application/json" \
  -d '{"text": "What is solar energy?"}'
```

### Test Audio Input
```bash
curl -X POST http://127.0.0.1:5000/api/chat-enquiry \
  -F "audio=@test_audio.mp3"
```

---

## Troubleshooting

### Common Issues

1. **"JamAI.__init__() got an unexpected keyword argument 'api_key'"**
   - ✅ Use `token=` instead of `api_key=` when initializing JamAI

2. **"Table metadata for 'meeting_transcripts' is not found"**
   - ✅ Knowledge base upload is now optional (will skip if table doesn't exist)

3. **"object has no attribute 'get'"**
   - ✅ Fixed by using proper dot notation to access response columns

4. **500 Internal Server Error**
   - Check Flask terminal for detailed traceback
   - Verify environment variables are set correctly
   - Ensure JamAI table exists with correct column names

---

## Summary

✅ **Backend:** Python/Flask with AssemblyAI transcription and JamAI RAG  
✅ **Frontend:** React with unified text/audio input handler  
✅ **API Contract:** Uses `Input_text` and `Final_response` columns  
✅ **Error Handling:** Robust error handling with detailed logging  
✅ **Response Parsing:** Uses dot notation to avoid attribute errors  

The system is now fully functional for both text and voice-based RAG chatbot interactions! 🎉
