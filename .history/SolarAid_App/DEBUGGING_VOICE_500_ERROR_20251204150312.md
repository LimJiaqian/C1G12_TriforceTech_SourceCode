# Debugging 500 Internal Server Error - Voice Recording Feature

## 🔍 Problem Overview
Getting a **500 Internal Server Error** when `sendAudioMessage()` in ChatPanel.jsx tries to POST to `/api/chat-enquiry`.

---

## ✅ Frontend Code Review (ChatPanel.jsx)

### Current Implementation:
```javascript
const formData = new FormData();
formData.append("audio", audioBlob, "recording.webm");

const response = await fetch("http://127.0.0.1:5000/api/chat-enquiry", {
  method: "POST",
  body: formData,
});
```

### ✅ This is CORRECT:
- ✅ Using FormData to send file
- ✅ Field name is "audio" (matches backend expectation)
- ✅ Filename is "recording.webm"
- ✅ No Content-Type header (browser sets it automatically with boundary)

---

## 🔍 What to Look for in Flask Terminal

### 1. **Check if the request is reaching the endpoint**
Look for this line:
```
📁 Audio file saved: /path/to/uploads/timestamp_recording.webm
```

If you DON'T see this, the request isn't reaching the server.

### 2. **Check for Python errors**
Since `debug=True` is enabled, you should see a full traceback like:
```
❌ Chat enquiry error: [error message]
Traceback (most recent call last):
  File "...", line X, in chat_enquiry
    [detailed error stack]
```

### 3. **Common Error Patterns to Look For:**

#### A. **Environment Variable Missing**
```
ValueError: ASSEMBLYAI_API_KEY not found in environment variables
```
**Solution:** Check your `.env` file has:
```
ASSEMBLYAI_API_KEY=your_key_here
VITE_JAM_API_KEY=your_key_here
VITE_JAM_PROJECT_ID=your_project_id_here
```

#### B. **File Upload Issues**
```
FileNotFoundError: [Errno 2] No such file or directory: 'backend/uploads/...'
```
**Solution:** The uploads folder doesn't exist or wrong path.

#### C. **AssemblyAI API Error**
```
Exception: Audio transcription failed: Invalid audio format
```
**Solution:** AssemblyAI doesn't support WebM. Need to convert to MP3/WAV.

#### D. **JamAI Connection Error**
```
Exception: Failed to connect to JamAI API
```
**Solution:** Check API credentials and network connectivity.

#### E. **Import Error**
```
ImportError: cannot import name 'process_enquiry' from 'backend.jamai_ai.audio_bridge'
```
**Solution:** PYTHONPATH not set correctly.

---

## 🐛 Step-by-Step Debugging Process

### Step 1: Check Flask Terminal Output
1. Keep the Flask terminal visible
2. Try recording a voice message in the browser
3. Watch for ANY output in the terminal

### Step 2: Check Browser Console
Open DevTools (F12) and look for:
```
📤 Sending audio to backend:
- Blob size: [number] bytes
- Blob type: audio/webm
- Filename: recording.webm

📥 Backend response status: 500

❌ Backend error response: [error details]
```

### Step 3: Test Backend Endpoint Manually
Create a test file: `test_audio_endpoint.py`
```python
import requests

# Test with a real audio file
with open("test.mp3", "rb") as f:
    files = {"audio": ("test.mp3", f, "audio/mpeg")}
    response = requests.post("http://127.0.0.1:5000/api/chat-enquiry", files=files)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
```

---

## 🔧 Most Likely Issues & Solutions

### Issue #1: WebM Format Not Supported by AssemblyAI
**Problem:** Browser records in WebM, but AssemblyAI might not support it.

**Solution:** Convert WebM to WAV or MP3 on frontend OR backend.

**Backend Fix (Recommended):**
Add FFmpeg conversion in `audio_bridge.py`:
```python
import subprocess

def convert_webm_to_wav(webm_path):
    """Convert WebM to WAV using FFmpeg"""
    wav_path = webm_path.replace('.webm', '.wav')
    subprocess.run([
        'ffmpeg', '-i', webm_path, 
        '-acodec', 'pcm_s16le', 
        '-ar', '16000', 
        wav_path
    ], check=True)
    return wav_path
```

### Issue #2: Missing Environment Variables
**Check:** Run this in Flask terminal:
```python
import os
print("ASSEMBLYAI_API_KEY:", os.getenv("ASSEMBLYAI_API_KEY"))
print("VITE_JAM_API_KEY:", os.getenv("VITE_JAM_API_KEY"))
```

### Issue #3: CORS Issues
**Check:** Browser console for CORS errors.
**Fix:** Ensure Flask has `CORS(app)` enabled (already done).

---

## 🧪 Quick Test Commands

### Test 1: Check if Flask is Running
```powershell
curl http://127.0.0.1:5000/api/leaderboard?user_id=1
```

### Test 2: Check Environment Variables
```powershell
cd SolarAid_App
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('AssemblyAI:', os.getenv('ASSEMBLYAI_API_KEY')[:10]+'...'); print('JamAI:', os.getenv('VITE_JAM_API_KEY')[:10]+'...')"
```

### Test 3: Check Uploads Folder Exists
```powershell
Test-Path "SolarAid_App/backend/uploads"
```

---

## 📝 What Information to Collect

When reporting the error, provide:

1. **Full Flask Terminal Output** (copy the entire error traceback)
2. **Browser Console Logs** (F12 → Console tab)
3. **Network Tab Details** (F12 → Network → click the failed request)
   - Request Headers
   - Request Payload
   - Response Headers
   - Response Body
4. **Environment Check:**
   ```powershell
   python -c "import assemblyai, jamaibase; print('Packages OK')"
   ```

---

## 🚀 Next Steps

1. **Record a voice message** in the browser
2. **Immediately check Flask terminal** for error output
3. **Copy the FULL error traceback** (including line numbers)
4. **Share that error** - it will tell us exactly what's wrong!

The Flask server is configured with `debug=True`, so you WILL see detailed error messages in the terminal. That's the key to solving this! 🔑
