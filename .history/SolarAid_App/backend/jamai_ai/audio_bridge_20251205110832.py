"""
Audio Bridge Module for Voice-to-RAG Integration
Handles audio transcription via AssemblyAI and knowledge base updates via JamAI
"""

import os
import time
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
    
    Args:
        input_data (str): Either audio file path or text query
        input_type (str): 'audio_path' or 'text'
        
    Returns:
        dict: Processing result with transcript/text and metadata
        
    Raises:
        Exception: If processing fails
    """
    try:
        if input_type == 'audio_path':
            print(f"Processing audio enquiry: {input_data}")
            
            # Step 1: Transcribe audio
            transcription_result = transcribe_audio(input_data)
            transcript_text = transcription_result["text"]
            
            # Step 2: Upload to knowledge base (optional - skip if table doesn't exist)
            upload_result = {"success": False, "skipped": True}
            try:
                upload_result = upload_to_knowledge_base(
                    transcript_text=transcript_text,
                    metadata={
                        "audio_id": transcription_result.get("id"),
                        "audio_duration": transcription_result.get("audio_duration")
                    }
                )
                print("Knowledge base upload successful")
                
            except Exception as upload_error:
                print(f"Knowledge base upload skipped: {upload_error}")
                print("   (Continuing with transcription only)")
            
            return {
                "success": True,
                "type": "audio",
                "transcript": transcript_text,
                "transcription_metadata": transcription_result,
                "knowledge_base_result": upload_result
            }
            
        elif input_type == 'text':
            print(f"Processing text enquiry: {input_data[:100]}...")
            
            return {
                "success": True,
                "type": "text",
                "text": input_data
            }
            
        else:
            raise ValueError(f"Invalid input_type: {input_type}. Must be 'audio_path' or 'text'")
            
    except Exception as e:
        print(f"Enquiry processing error: {e}")
        return {
            "success": False,
            "error": str(e),
            "type": input_type
        }


def query_jamai_chat(query_text: str, table_id: str = "Chatbox") -> dict:
    """
    Query the JamAI Action Table for a response
    
    Args:
        query_text (str): The user's query
        table_id (str): JamAI Action Table ID (default: "Chatbox")
        
    Returns:
        dict: Response from JamAI Action Table
        
    Raises:
        Exception: If query fails
    """
    if not VITE_JAM_API_KEY or not VITE_JAM_PROJECT_ID:
        raise ValueError("VITE_JAM_API_KEY or VITE_JAM_PROJECT_ID not found in environment variables")
    
    try:
        print(f"Querying JamAI Action Table: {table_id}")
        
        # Initialize JamAI client
        jamai = JamAI(
            token=VITE_JAM_API_KEY,
            project_id=VITE_JAM_PROJECT_ID
        )
        
        # Create request
        add_request = p.RowAddRequest(
            table_id=table_id,
            data=[{"Input_text": query_text}],
            stream=False
        )
        
        # Query action table
        response = jamai.table.add_table_rows(
            table_type="action",
            request=add_request
        )
        
        # --- ROBUST PARSING LOGIC ---
        # Handles both Dictionary (old SDK) and Pydantic Model (new SDK)
        response_text = ""
        
        print(f"[DEBUG] Response object type: {type(response)}")
        print(f"[DEBUG] Has rows: {hasattr(response, 'rows')}")
        
        if response.rows:
            row = response.rows[0]
            columns = row.columns
            
            print(f"[DEBUG] Columns type: {type(columns)}")
            
            # Handle both Dictionary and Pydantic Model
            if isinstance(columns, dict):
                # Dictionary access
                target_col = columns.get("Final_response")
                print(f"[DEBUG] Got Final_response from dict")
            else:
                # Pydantic Model access
                target_col = getattr(columns, "Final_response", None)
                print(f"[DEBUG] Got Final_response from Pydantic model")

            # Extract actual text value safely - OpenAI-style structure
            if target_col:
                print(f"[DEBUG] target_col type: {type(target_col)}")
                print(f"[DEBUG] target_col repr: {repr(target_col)[:200]}...")
                
                # Try OpenAI-style response structure FIRST (most common)
                if hasattr(target_col, 'choices') and hasattr(target_col.choices, '__iter__'):
                    # OpenAI-style: object.choices[0].message.content
                    try:
                        content = target_col.choices[0].message.content
                        response_text = str(content)
                        print(f"[DEBUG] Extracted from OpenAI object structure")
                    except (IndexError, AttributeError) as e:
                        print(f"[DEBUG] OpenAI structure parse error: {e}")
                        response_text = "Error: Invalid OpenAI response structure."
                
                # If it's a dictionary
                elif isinstance(target_col, dict):
                    # Try OpenAI dict structure: {'choices': [{'message': {'content': '...'}}]}
                    if 'choices' in target_col and len(target_col['choices']) > 0:
                        try:
                            content = target_col['choices'][0]['message']['content']
                            response_text = str(content)
                            print(f"[DEBUG] Extracted from OpenAI dict structure")
                        except (KeyError, IndexError) as e:
                            print(f"[DEBUG] OpenAI dict parse error: {e}")
                            response_text = "Error: Invalid OpenAI dict structure."
                    else:
                        # Fallback: try standard fields
                        response_text = str(target_col.get("text") or target_col.get("value") or target_col.get("content") or "")
                        print(f"[DEBUG] Extracted from dict fallback")
                
                # If it's a string already (check for stringified object)
                elif isinstance(target_col, str):
                    # Check if it's a stringified object (starts with class name)
                    if target_col.startswith("ChatCompletion") or "choices=" in target_col:
                        print(f"[DEBUG] Detected stringified object - cannot parse")
                        response_text = "Error: Received stringified object instead of proper structure."
                    else:
                        response_text = target_col
                        print(f"[DEBUG] Already a clean string")
                
                # Other attribute-based objects
                elif hasattr(target_col, "text"):
                    response_text = str(target_col.text)
                    print(f"[DEBUG] Extracted from .text attribute")
                elif hasattr(target_col, "value"):
                    response_text = str(target_col.value)
                    print(f"[DEBUG] Extracted from .value attribute")
                elif hasattr(target_col, "content"):
                    response_text = str(target_col.content)
                    print(f"[DEBUG] Extracted from .content attribute")
                
                else:
                    print(f"[DEBUG] Unknown structure - checking __dict__")
                    if hasattr(target_col, '__dict__'):
                        print(f"[DEBUG] Object attributes: {list(target_col.__dict__.keys())}")
                    response_text = "Error: Unable to extract response text from unknown structure."
                    
            else:
                response_text = "Error: 'Final_response' column missing."
        else:
            response_text = "Error: No response received from JamAI."
        # ---------------------------------
        
        print(f"Received response from JamAI: {response_text[:100]}...")
        
        # Return JamAI response directly
        return {
            "success": True,
            "response": response_text.strip(),
            "table_id": table_id
        }
        
    except Exception as e:
        print(f"JamAI query error: {e}")
        import traceback
        traceback.print_exc()
        
        # Return safe fallback so frontend doesn't crash
        return {
            "success": False,
            "response": "I'm having trouble connecting to my brain right now. Please try again in a moment.",
            "error": str(e)
        }
