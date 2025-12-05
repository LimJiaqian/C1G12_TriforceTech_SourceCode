"""
Audio Bridge Module for Voice-to-RAG Integration
Handles audio transcription via AssemblyAI and knowledge base updates via JamAI
"""

import os
import time
import re
import assemblyai as aai
from jamaibase import JamAI
from jamaibase import types as p
from dotenv import load_dotenv
from datetime import datetime

# Load .env from project root (SolarAid_App directory)
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=env_path)

# Configuration
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
VITE_JAM_API_KEY = os.getenv("VITE_JAM_API_KEY")
VITE_JAM_PROJECT_ID = os.getenv("VITE_JAM_PROJECT_ID")
KNOWLEDGE_TABLE_ID = "meeting_transcripts"

# Debug: Print loaded values (masked)
print(f"🔑 Environment loaded from: {os.path.abspath(env_path)}")
if VITE_JAM_API_KEY:
    print(f"✅ VITE_JAM_API_KEY: {VITE_JAM_API_KEY[:20]}...")
else:
    print("❌ VITE_JAM_API_KEY: NOT FOUND")
if VITE_JAM_PROJECT_ID:
    print(f"✅ VITE_JAM_PROJECT_ID: {VITE_JAM_PROJECT_ID}")
else:
    print("❌ VITE_JAM_PROJECT_ID: NOT FOUND")

# Initialize clients
if ASSEMBLYAI_API_KEY:
    aai.settings.api_key = ASSEMBLYAI_API_KEY


def transcribe_audio(audio_path: str) -> dict:
    """
    Transcribe audio file using AssemblyAI
    
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
        print(f"Starting transcription for: {audio_path}")
        
        # Create transcriber and transcribe
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_path)
        
        if transcript.status == aai.TranscriptStatus.error:
            raise Exception(f"Transcription failed: {transcript.error}")
        
        print(f"Transcription completed: {len(transcript.text)} characters")
        
        return {
            "text": transcript.text,
            "id": transcript.id,
            "status": transcript.status,
            "audio_duration": transcript.audio_duration,
            "confidence": getattr(transcript, 'confidence', None)
        }
        
    except Exception as e:
        print(f"Transcription error: {e}")
        raise Exception(f"Audio transcription failed: {str(e)}")


def upload_to_knowledge_base(transcript_text: str, metadata: dict = None) -> dict:
    """
    Upload transcribed text to JamAI Knowledge Table
    
    Args:
        transcript_text (str): The transcribed text
        metadata (dict): Optional metadata (audio_id, duration, etc.)
        
    Returns:
        dict: Response from JamAI API
        
    Raises:
        Exception: If upload fails
    """
    if not VITE_JAM_API_KEY or not VITE_JAM_PROJECT_ID:
        raise ValueError("VITE_JAM_API_KEY or VITE_JAM_PROJECT_ID not found in environment variables")
    
    try:
        print(f"Uploading to JamAI Knowledge Base (Table: {KNOWLEDGE_TABLE_ID})")
        
        # Initialize JamAI client
        jamai = JamAI(
            token=VITE_JAM_API_KEY,
            project_id=VITE_JAM_PROJECT_ID
        )
        
        # Prepare row data
        timestamp = datetime.now().isoformat()
        
        row_data = {
            "transcript": transcript_text,
            "timestamp": timestamp,
        }
        
        # Add metadata if provided
        if metadata:
            if "audio_id" in metadata:
                row_data["audio_id"] = metadata["audio_id"]
            if "audio_duration" in metadata:
                row_data["duration"] = str(metadata["audio_duration"])
        
        # Create request
        add_request = p.RowAddRequest(
            table_id=KNOWLEDGE_TABLE_ID,
            data=[row_data],
            stream=False
        )
        
        # Upload to knowledge table
        response = jamai.table.add_table_rows(
            table_type="knowledge",
            request=add_request
        )
        
        print(f"Successfully uploaded to knowledge base")
        
        return {
            "success": True,
            "table_id": KNOWLEDGE_TABLE_ID,
            "row_count": len(response.rows) if hasattr(response, 'rows') else 1,
            "timestamp": timestamp
        }
        
    except Exception as e:
        print(f"Knowledge base upload error: {e}")
        raise Exception(f"Failed to upload to knowledge base: {str(e)}")


def process_enquiry(input_data: str, input_type: str = 'text') -> dict:
    """
    Process user enquiry - handles both audio and text inputs
    """
    try:
        if input_type == 'audio_path':
            print(f"Processing audio enquiry: {input_data}")
            
            # Step 1: Transcribe audio
            transcription_result = transcribe_audio(input_data)
            transcript_text = transcription_result["text"]
            
            # Step 2: Upload to knowledge base (Background task)
            try:
                upload_to_knowledge_base(
                    transcript_text=transcript_text,
                    metadata={
                        "audio_id": transcription_result.get("id"),
                        "audio_duration": transcription_result.get("audio_duration")
                    }
                )
            except Exception as upload_error:
                print(f"KB upload skipped: {upload_error}")

            # Step 3: IMMEDIATE HANDOFF -> Query the Chatbot with the transcript
            # This is the missing link that was causing your issue
            print(f"Audio transcribed. sending to JamAI Chat: {transcript_text[:50]}...")
            return query_jamai_chat(transcript_text)
            
        elif input_type == 'text':
            print(f"Processing text enquiry: {input_data[:100]}...")
            # For text, we assume the caller will call query_jamai_chat separately 
            # OR we can just return the text payload as you had before.
            return {
                "success": True,
                "type": "text",
                "text": input_data
            }
            
        else:
            raise ValueError(f"Invalid input_type: {input_type}")
            
    except Exception as e:
        print(f"Enquiry processing error: {e}")
        return {
            "success": False,
            "error": str(e),
            "type": input_type
        }


def query_jamai_chat(query_text: str, table_id: str = "Chatbox") -> dict:
    if not VITE_JAM_API_KEY or not VITE_JAM_PROJECT_ID:
        raise ValueError("API Keys missing")
    
    try:
        print(f"Querying JamAI Action Table: {table_id}")
        jamai = JamAI(token=VITE_JAM_API_KEY, project_id=VITE_JAM_PROJECT_ID)
        
        add_request = p.RowAddRequest(
            table_id=table_id,
            data=[{"Input_text": query_text}],
            stream=False
        )
        
        response = jamai.table.add_table_rows(
            table_type="action",
            request=add_request
        )
        
        response_text = ""
        
        if response.rows:
            row = response.rows[0]
            columns = row.columns
            
            # Get the raw object/dict/string
            target_col = None
            if isinstance(columns, dict):
                target_col = columns.get("Final_response")
            else:
                target_col = getattr(columns, "Final_response", None)

            # --- THE FIX: AGGRESSIVE PARSING ---
            
            # 1. If it is already a simple string, check if it's the "messy" metadata string
            if isinstance(target_col, str):
                # Check for that specific "id='chatcmpl" pattern you are seeing
                if "id='chatcmpl" in target_col or "ChatCompletion" in target_col:
                    print("[DEBUG] Detected raw object string. Attempting Regex extraction...")
                    # Regex to find content='...' (handling newlines with DOTALL)
                    match = re.search(r"content='(.*?)'(?:, role=|, function_call=)", target_col, re.DOTALL)
                    if not match:
                        # Try double quotes just in case
                        match = re.search(r'content="(.*?)"(?:, role=|, function_call=)', target_col, re.DOTALL)
                    
                    if match:
                        response_text = match.group(1)
                        # Clean up escaped newlines often found in raw repr strings
                        response_text = response_text.encode('utf-8').decode('unicode_escape')
                    else:
                        response_text = "Error: Could not extract message content from raw response."
                else:
                    response_text = target_col
            
            # 2. If it is a Pydantic object (The "Correct" way)
            elif hasattr(target_col, 'choices'):
                try:
                    response_text = target_col.choices[0].message.content
                except:
                    response_text = str(target_col)

            # 3. If it is a Dict (The other "Correct" way)
            elif isinstance(target_col, dict):
                try:
                    response_text = target_col['choices'][0]['message']['content']
                except:
                    response_text = str(target_col)
            
            else:
                response_text = str(target_col)

        return {
            "success": True,
            "response": response_text.strip(), # This is the clean text
            "table_id": table_id
        }
        
    except Exception as e:
        print(f"JamAI query error: {e}")
        return {
            "success": False,
            "response": "Connection error.",
            "error": str(e)
        }