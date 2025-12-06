"""
Voice-to-RAG Architecture Visualization
"""

ARCHITECTURE = """
┌─────────────────────────────────────────────────────────────────────────────┐
│                         VOICE-TO-RAG SYSTEM ARCHITECTURE                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  FRONTEND (React)                                                            │
│  ┌─────────────┐      ┌─────────────┐      ┌──────────────┐                │
│  │ Text Input  │      │ Audio File  │      │ Voice Record │                │
│  │  (JSON)     │      │  (Upload)   │      │  (MediaAPI)  │                │
│  └──────┬──────┘      └──────┬──────┘      └──────┬───────┘                │
│         │                    │                     │                         │
│         └────────────────────┴─────────────────────┘                         │
│                              │                                               │
│                              ▼                                               │
│                   POST /api/chat-enquiry                                     │
│                   http://127.0.0.1:5000                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  BACKEND (Flask)                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  server.py - /api/chat-enquiry endpoint                              │   │
│  │  • Receives multipart/form-data (audio) OR JSON (text)               │   │
│  │  • Validates file format and size                                    │   │
│  │  • Saves audio temporarily                                           │   │
│  │  • Calls audio_bridge.process_enquiry()                              │   │
│  │  • Deletes temp file after processing                                │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                              │                                               │
│                              ▼                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  jamai_ai/audio_bridge.py                                            │   │
│  │                                                                       │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │  If Audio:                                                  │    │   │
│  │  │  1. transcribe_audio(audio_path)                           │    │   │
│  │  │     → AssemblyAI API                                       │    │   │
│  │  │     → Returns transcript text                              │    │   │
│  │  │                                                             │    │   │
│  │  │  2. upload_to_knowledge_base(transcript)                   │    │   │
│  │  │     → JamAI Knowledge Table: "meeting_transcripts"        │    │   │
│  │  │     → Stores for RAG retrieval                            │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  │                                                                       │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │  If Text:                                                   │    │   │
│  │  │  → Skip transcription                                       │    │   │
│  │  │  → Use text directly                                        │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  │                                                                       │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │  Final Step:                                                │    │   │
│  │  │  3. query_jamai_chat(query_text)                           │    │   │
│  │  │     → JamAI Action Table: "Chatbox"                        │    │   │
│  │  │     → Hybrid RAG + Gemini routing                          │    │   │
│  │  │     → Returns AI response                                  │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  EXTERNAL SERVICES                                                           │
│  ┌─────────────────┐  ┌────────────────────────────┐  ┌─────────────────┐  │
│  │  AssemblyAI     │  │  JamAI Base                │  │  Google Gemini  │  │
│  │  ─────────────  │  │  ──────────────────────    │  │  ──────────────  │  │
│  │  • Audio → Text │  │  • Knowledge Table (RAG)   │  │  • Fallback AI  │  │
│  │  • Transcribe   │  │  • Action Table (Routing)  │  │  • General Q&A  │  │
│  │  • High accuracy│  │  • Hybrid routing logic    │  │  • Context-aware│  │
│  └─────────────────┘  └────────────────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│  RESPONSE FLOW                                                               │
│                                                                              │
│  Backend → Frontend                                                          │
│  ───────────────────                                                         │
│  {                                                                           │
│    "success": true,                                                          │
│    "query": "How much energy can I donate?",                                │
│    "response": "Based on your solar setup...",                              │
│    "input_type": "audio",                                                    │
│    "audio_metadata": {                                                       │
│      "transcription_id": "abc123",                                          │
│      "audio_duration": 12.5,                                                │
│      "knowledge_base_uploaded": true                                        │
│    }                                                                         │
│  }                                                                           │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│  FILE STRUCTURE                                                              │
│                                                                              │
│  SolarAid_App/                                                               │
│  ├── backend/                                                                │
│  │   ├── jamai_ai/              ← NEW MODULE                                │
│  │   │   ├── __init__.py         (Package initialization)                   │
│  │   │   ├── audio_bridge.py     ⭐ (Main implementation)                   │
│  │   │   ├── README.md           (Documentation)                            │
│  │   │   └── test_setup.py       (Verification script)                      │
│  │   ├── uploads/                ← NEW FOLDER (temp audio files)            │
│  │   └── server.py               ⭐ (Modified - new endpoint)               │
│  ├── src/                                                                    │
│  │   └── services/                                                           │
│  │       └── voiceChat.integration.example.js  ⭐ (Frontend examples)       │
│  ├── requirements.txt            ⭐ (Updated - new dependencies)             │
│  ├── .env.example                ⭐ (Updated - new API keys)                 │
│  ├── VOICE_TO_RAG_IMPLEMENTATION.md  (Full documentation)                   │
│  └── QUICK_START.md              (Step-by-step guide)                       │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│  KEY FEATURES                                                                │
│                                                                              │
│  ✅ Audio Transcription          AssemblyAI converts speech to text         │
│  ✅ Knowledge Base Integration   Transcripts stored for RAG                 │
│  ✅ Hybrid Query Routing         Automatic RAG + Gemini fallback            │
│  ✅ Text Input Support           Direct text queries without audio          │
│  ✅ File Validation             Format and size checks                      │
│  ✅ Auto Cleanup                 Temporary files deleted automatically      │
│  ✅ Error Handling               Comprehensive error messages               │
│  ✅ CORS Enabled                 Works with frontend                        │
│  ✅ Multiple Formats             mp3, wav, flac, ogg, m4a, webm            │
│  ✅ Production Ready             50MB limit, secure file handling           │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│  SETUP CHECKLIST                                                             │
│                                                                              │
│  1. ☐ Install dependencies: pip install -r requirements.txt                 │
│  2. ☐ Get AssemblyAI API key from assemblyai.com                           │
│  3. ☐ Get JamAI API key and Project ID from jamaibase.com                  │
│  4. ☐ Add API keys to .env file                                            │
│  5. ☐ Create JamAI Knowledge Table: meeting_transcripts                    │
│  6. ☐ Create JamAI Action Table: Chatbox (with RAG logic)                 │
│  7. ☐ Run test script: python backend/jamai_ai/test_setup.py              │
│  8. ☐ Start Flask server: python backend/server.py                         │
│  9. ☐ Test endpoint with cURL or Postman                                   │
│  10. ☐ Integrate with frontend using provided examples                     │
└─────────────────────────────────────────────────────────────────────────────┘
"""

if __name__ == "__main__":
    print(ARCHITECTURE)