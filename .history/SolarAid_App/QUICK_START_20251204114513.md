# Quick Start Guide - Voice-to-RAG Setup

## Step-by-Step Installation

### 1. Navigate to Project Directory
```bash
cd "c:\Users\flc06\OneDrive - Universiti Malaya\Documents\GitHub\C1G12_TriforceTech_SourceCode\SolarAid_App"
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- `assemblyai==0.30.0` - Audio transcription
- `jamaibase==0.3.18` - JamAI Base SDK
- `supabase==2.0.0` - Supabase client
- Plus all existing dependencies (flask, pandas, etc.)

### 3. Set Up Environment Variables

Create/Edit `.env` file in the `SolarAid_App` directory:

```env
# Existing variables (keep these)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
GEMINI_API_KEY=your_gemini_key
SEA_LION_API_KEY=your_sealion_key
SEA_LION_API_KEY2=your_sealion_key2

# NEW: Voice-to-RAG variables (add these)
ASSEMBLYAI_API_KEY=your_assemblyai_key_here
VITE_JAM_API_KEY=your_jamai_key_here
VITE_JAM_PROJECT_ID=your_jamai_project_id_here
```

**Get API Keys:**
1. **AssemblyAI**: 
   - Go to https://www.assemblyai.com/
   - Sign up for free account
   - Get API key from dashboard

2. **JamAI Base**:
   - Go to https://www.jamaibase.com/
   - Sign up/Login
   - Go to Settings → Get API Key and Project ID
   - Note: Use `VITE_JAM_API_KEY` and `VITE_JAM_PROJECT_ID` (same variables as frontend)

### 4. Set Up JamAI Tables

Log into JamAI Base and create:

**Knowledge Table: `meeting_transcripts`**
- Type: Knowledge Table
- Columns:
  - `transcript` (Text)
  - `timestamp` (Text) 
  - `audio_id` (Text)
  - `duration` (Text)

**Action Table: `Chatbox`**
- Type: Action Table
- Columns:
  - `Input_text` (Input)
  - `Final_response` (Output)
- Configure RAG logic to query `meeting_transcripts`

### 5. Test Your Setup

Run the verification script:
```bash
python backend/jamai_ai/test_setup.py
```

Expected output:
```
✅ AssemblyAI API Key: abc12345...
✅ JamAI API Key: xyz98765...
✅ JamAI Project ID: proj_...
✅ All functions imported successfully
✅ Text processing successful
✅ JamAI connection successful

🎉 All tests passed! Your Voice-to-RAG setup is ready.
```

### 6. Start the Flask Server

```bash
python backend/server.py
```

You should see:
```
Flask server running on http://127.0.0.1:5000
```

### 7. Test the Endpoint

**Test with text:**
```bash
curl -X POST http://127.0.0.1:5000/api/chat-enquiry -H "Content-Type: application/json" -d "{\"text\": \"Hello, how does SolarAid work?\"}"
```

**Test with audio file:**
```bash
curl -X POST http://127.0.0.1:5000/api/chat-enquiry -F "audio=@path/to/audio.mp3"
```

---

## Troubleshooting

### Import Errors
If you see "Import could not be resolved":
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Verify installation
pip list | grep -E "assemblyai|jamaibase|supabase"
```

### Module Not Found
```bash
# Make sure you're in the correct directory
cd SolarAid_App
python -c "import assemblyai; print('AssemblyAI:', assemblyai.__version__)"
python -c "import jamaibase; print('JamAI installed')"
```

### API Key Errors
1. Check `.env` file exists in `SolarAid_App/` directory
2. Verify no typos in variable names
3. Restart Flask server after adding keys

---

## Next Steps

1. ✅ Dependencies installed
2. ✅ Environment variables configured
3. ✅ JamAI tables created
4. ✅ Test script passed
5. ✅ Flask server running
6. ➡️ **Integrate with frontend** (see `VOICE_TO_RAG_IMPLEMENTATION.md`)

---

## Quick Reference

**Project Structure:**
```
SolarAid_App/
├── backend/
│   ├── jamai_ai/
│   │   ├── audio_bridge.py    ← Main module
│   │   └── test_setup.py      ← Run this to test
│   └── server.py              ← Modified with new endpoint
├── requirements.txt           ← Updated with new packages
└── .env                       ← Add your API keys here
```

**New Endpoint:**
```
POST http://127.0.0.1:5000/api/chat-enquiry
```

**Supported Formats:**
- Audio: mp3, wav, flac, ogg, m4a, webm
- Text: JSON with "text" field
- Max file size: 50MB

---

**Need help?** Check `VOICE_TO_RAG_IMPLEMENTATION.md` for full documentation.
