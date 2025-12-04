"""
Audio Bridge Module for Voice-to-RAG Integration
Handles audio transcription via AssemblyAI and knowledge base updates via JamAI
With Google Gemini fallback support
"""

import os
import time
import assemblyai as aai
import google.generativeai as genai
from jamaibase import JamAI
from jamaibase import types as p
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Configuration
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
VITE_JAM_API_KEY = os.getenv("VITE_JAM_API_KEY")
VITE_JAM_PROJECT_ID = os.getenv("VITE_JAM_PROJECT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
KNOWLEDGE_TABLE_ID = "meeting_transcripts"

# Initialize clients
if ASSEMBLYAI_API_KEY:
    aai.settings.api_key = ASSEMBLYAI_API_KEY

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


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
                
                # Step 3: Wait for database indexing
                print("Waiting for database indexing...")
                time.sleep(5)  # Wait 5 seconds for JamAI to index the knowledge base
                print("Indexing wait complete")
                
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


def handle_fallback(user_query: str) -> str:
    """
    Fallback handler using Google Gemini when JamAI returns FALLBACK_MODE
    
    Args:
        user_query (str): The user's original query
        
    Returns:
        str: Response from Google Gemini
        
    Raises:
        Exception: If Gemini API fails
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    try:
        print(f">> Switching to Local Gemini...")
        print(f"User query: {user_query[:100]}...")
        
        # Initialize Gemini 1.5 Flash model with system instruction
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash-latest',
            system_instruction="You are a helpful, friendly assistant. Answer the user naturally."
        )
        
        # Generate response with the ORIGINAL user query (not "FALLBACK_MODE")
        # We send the user's actual question, not the JamAI response
        prompt = f"User said: '{user_query}'. You are a helpful assistant. Answer naturally."
        fallback_response = model.generate_content(prompt)
        
        # Extract ONLY the text content (not the full ChatCompletion object)
        # Use .text to get the actual message string
        final_output = fallback_response.text
        
        print(f"Gemini response generated: {len(final_output)} characters")
        print(f"Final Answer sent to user: {final_output[:100]}...")
        
        # Return ONLY the text string (this is what frontend receives)
        return final_output
        
    except Exception as e:
        print(f"Gemini fallback error: {e}")
        raise Exception(f"Gemini fallback failed: {str(e)}")


def query_jamai_chat(query_text: str, table_id: str = "Chatbox") -> dict:
    """
    Query the JamAI Action Table for a response
    The Action Table handles hybrid routing (RAG + Gemini fallback)
    
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
        
        # Extract response using dot notation (as per JamAI API contract)
        if hasattr(response, 'rows') and len(response.rows) > 0:
            row = response.rows[0]
            # Use dot notation to access columns
            if hasattr(row, 'columns'):
                columns = row.columns
                # Access Final_response column
                if 'Final_response' in columns:
                    final_response_col = columns['Final_response']
                    # Extract value from column
                    response_text = final_response_col.get('value') if isinstance(final_response_col, dict) else str(final_response_col)
                else:
                    response_text = "No Final_response column found in table"
            else:
                response_text = "No columns found in response"
        else:
            response_text = "No rows returned from Action Table"
        
        # Extract clean text (strip any whitespace)
        jam_response_text = response_text.strip()
        
        print(f"Received response from JamAI: {jam_response_text[:100]}...")
        
        # The "Switch" Logic - Check for FALLBACK_MODE trigger
        if "FALLBACK_MODE" in jam_response_text:
            print(f">> Switching to Local Gemini...")
            print(f"Original user query: {query_text[:100]}...")
            
            try:
                # Call Gemini with the ORIGINAL user query (not the JamAI response)
                final_answer = handle_fallback(query_text)
                
                print(f"Returning Gemini response to frontend")
                print(f"Final answer preview: {final_answer[:100]}...")
                
                return {
                    "success": True,
                    "response": final_answer,  # This is the actual answer sent to user
                    "table_id": table_id,
                    "fallback_used": True,
                    "fallback_provider": "Google Gemini"
                }
            except Exception as fallback_error:
                print(f"Fallback failed: {fallback_error}")
                return {
                    "success": False,
                    "response": "Sorry, both JamAI and Gemini fallback failed. Please try again.",
                    "error": str(fallback_error)
                }
        
        # Return JamAI response normally
        return {
            "success": True,
            "response": response_text,
            "table_id": table_id,
            "fallback_used": False
        }
        
    except Exception as e:
        print(f"JamAI query error: {e}")
        raise Exception(f"Failed to query JamAI Action Table: {str(e)}")
