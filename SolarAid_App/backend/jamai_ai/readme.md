# Voice-to-RAG Backend Feature

## Overview

This module enables voice-based chat enquiries by integrating AssemblyAI for audio transcription and JamAI Base for knowledge management and RAG-based responses.

## Architecture

```
User Audio Input → AssemblyAI Transcription → JamAI Knowledge Base → JamAI Action Table → AI Response
User Text Input → JamAI Action Table → AI Response
```

## Features

✅ **Audio Transcription** - Transcribe audio files using AssemblyAI  
✅ **Knowledge Base Integration** - Upload transcripts to JamAI Knowledge Table  
✅ **Hybrid Query Routing** - Automatic RAG + Gemini fallback via JamAI Action Table  
✅ **Text Input Support** - Direct text queries without audio processing  
✅ **Automatic Cleanup** - Temporary audio files are automatically deleted  

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the `SolarAid_App/` directory:

```env
# Voice-to-RAG Configuration
ASSEMBLYAI_API_KEY=your_assemblyai_key_here
VITE_JAM_API_KEY=your_jamai_key_here
VITE_JAM_PROJECT_ID=your_jamai_project_id_here
```

**Where to get API keys:**

- **AssemblyAI**: Sign up at [assemblyai.com](https://www.assemblyai.com/) → Get API key from dashboard
- **JamAI Base**: Sign up at [jamaibase.com](https://www.jamaibase.com/) → Get API key and Project ID from settings
  - Note: The backend uses `VITE_JAM_API_KEY` and `VITE_JAM_PROJECT_ID` (same variables as frontend)

### 3. Set Up JamAI Tables

You need two tables in your JamAI Base project:

#### a. Knowledge Table: `meeting_transcripts`
Stores audio transcripts for RAG retrieval.

**Required columns:**
- `transcript` (Text) - The transcribed audio content
- `timestamp` (Text) - ISO timestamp of when transcript was created
- `audio_id` (Text, Optional) - AssemblyAI transcript ID
- `duration` (Text, Optional) - Audio duration in seconds

#### b. Action Table: `Chatbox`
Handles user queries with hybrid routing (RAG + Gemini fallback).

**Required columns:**
- `Input_text` (Input) - User query
- `Final_response` (Output) - AI-generated response

The Action Table should already have your RAG logic configured on the JamAI cloud.

## API Usage

### Endpoint

```
POST /api/chat-enquiry
```

### Audio Input (Multipart Form Data)

```javascript
const formData = new FormData();
formData.append('audio', audioFile);

fetch('http://127.0.0.1:5000/api/chat-enquiry', {
  method: 'POST',
  body: formData
})
```

**Supported audio formats:** mp3, wav, flac, ogg, m4a, webm  
**Max file size:** 50MB

### Text Input (JSON)

```javascript
fetch('http://127.0.0.1:5000/api/chat-enquiry', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: 'How much energy can I donate?' })
})
```

### Response Format

```json
{
  "success": true,
  "query": "How much energy can I donate?",
  "response": "Based on your solar setup, you can donate up to...",
  "input_type": "audio",
  "audio_metadata": {
    "transcription_id": "abc123",
    "audio_duration": 12.5,
    "knowledge_base_uploaded": true
  }
}
```

## Code Structure

### `backend/jamai_ai/audio_bridge.py`

Main module containing:

- `transcribe_audio(audio_path)` - Transcribe audio using AssemblyAI
- `upload_to_knowledge_base(text, metadata)` - Upload transcript to JamAI Knowledge Table
- `process_enquiry(input_data, type)` - Main entry point for audio/text processing
- `query_jamai_chat(query_text, table_id)` - Query JamAI Action Table for AI response

### `backend/server.py`

Flask endpoint `/api/chat-enquiry`:
- Handles multipart file uploads
- Validates audio file formats
- Manages temporary file storage and cleanup
- Routes requests to appropriate processing functions

## Example Usage

### Python Example

```python
from backend.jamai_ai.audio_bridge import process_enquiry, query_jamai_chat

# Process audio
result = process_enquiry("path/to/audio.mp3", input_type='audio_path')
transcript = result['transcript']

# Query JamAI for response
response = query_jamai_chat(transcript)
print(response['response'])
```

### JavaScript Example (Frontend)

```javascript
// Audio recording and upload
const mediaRecorder = new MediaRecorder(stream);
const audioChunks = [];

mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
mediaRecorder.onstop = async () => {
  const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.webm');
  
  const response = await fetch('http://127.0.0.1:5000/api/chat-enquiry', {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  console.log('AI Response:', data.response);
};
```

## Error Handling

The module includes comprehensive error handling:

- **Invalid file format** → 400 Bad Request
- **Missing API keys** → 500 Internal Server Error with details
- **Transcription failure** → 500 with AssemblyAI error details
- **JamAI upload failure** → 500 with JamAI error details
- **Automatic cleanup** → Temp files deleted even if errors occur

## Debugging

Enable detailed logging:

```python
# Audio transcription logs
🎤 Starting transcription for: path/to/audio.mp3
✅ Transcription completed: 1234 characters

# Knowledge base upload logs
📤 Uploading to JamAI Knowledge Base (Table: meeting_transcripts)
✅ Successfully uploaded to knowledge base

# Chat query logs
💬 Querying JamAI Action Table: Chatbox
✅ Received response from Action Table
```

## Testing

### Test Audio Input

```bash
curl -X POST http://127.0.0.1:5000/api/chat-enquiry \
  -F "audio=@test_audio.mp3"
```

### Test Text Input

```bash
curl -X POST http://127.0.0.1:5000/api/chat-enquiry \
  -H "Content-Type: application/json" \
  -d '{"text": "What is my donation impact?"}'
```

## Troubleshooting

### Issue: "ASSEMBLYAI_API_KEY not found"
**Solution:** Add the key to your `.env` file and restart the server.

### Issue: "Failed to upload to knowledge base"
**Solution:** 
1. Verify `JAMAI_API_KEY` and `JAMAI_PROJECT_ID` are correct
2. Ensure the `meeting_transcripts` table exists in JamAI Base
3. Check table column names match the code

### Issue: "No response generated"
**Solution:**
1. Verify the `Chatbox` Action Table exists
2. Check that the table has `Input_text` and `Final_response` columns
3. Ensure RAG logic is configured on the JamAI cloud side

## Performance

- **Transcription time:** ~10-30 seconds for 1-minute audio
- **Knowledge base upload:** ~1-2 seconds
- **Chat response:** ~2-5 seconds (depends on RAG complexity)
- **Total latency (audio):** ~15-40 seconds
- **Total latency (text):** ~2-5 seconds

## Security Considerations

✅ File validation (extension and size checks)  
✅ Secure filename handling  
✅ Automatic temporary file cleanup  
✅ API key protection via environment variables  
✅ CORS configuration for frontend integration  

## Future Enhancements

- [ ] Real-time streaming transcription
- [ ] Audio format conversion
- [ ] Transcript caching
- [ ] Batch audio processing
- [ ] WebSocket support for live audio
- [ ] Language detection and multi-language support

## License

Part of the SolarAid project by TriforceTech.s