import re
from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
from backend.sealion_ai.area_detection import get_top5_energy_need
from backend.sealion_ai.thanks_ai import generate_thankyou_message
from backend.sealion_ai.certificate_generator import generate_certificate
from backend.analytics import DonationAnalytics
from backend.gemini_ai.ai_agent import DonationAIAgent
from backend.database.supabase import supabase
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
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

def allowed_audio_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_EXTENSIONS

# Initialize analytics and AI agent for prediction feature
CSV_PATH = "backend/dataset/donations.csv"
analytics = DonationAnalytics(CSV_PATH)
analytics.load_data()
agent = DonationAIAgent() 

@app.post("/api/login")
def login():
    """Login user using Supabase 'user' table"""
    try:
        data = request.json
        email = data.get("email")
        password = data.get("password")

        # Query Supabase
        result = (
            supabase.table("user")
            .select("*")
            .eq("username", email)
            .execute()
        )

        if not result.data:
            return jsonify({"error": "User not found"}), 404

        user = result.data[0]

        # Check password
        if user["User_password"] != password:
            return jsonify({"error": "Incorrect password"}), 401

        return jsonify({
            "message": "Login successful",
            "user_id": user["User_ID"],
            "username": user["username"],
            "token": "demo-token"  # You can replace with JWT later
        })

    except Exception as e:
        print("Login error:", e)
        return jsonify({"error": str(e)}), 500

@app.get("/api/top5")
def top5():
    result = get_top5_energy_need()
    return jsonify(result)

@app.route("/api/thankyou", methods=["GET"])
def api_thankyou():
    message = generate_thankyou_message()
    return jsonify({"message": message})

@app.route("/api/certificate", methods=["POST", "GET"])
def api_certificate():
    """
    Generate a Sadaqah Jariah certificate with SEA-LION AI
    Expects: { "kwh": 100, "recipient_type": "clinic" }
    Returns: { "image_url": "data:image/png;base64,...", "metrics": {...} }
    """
    try:
        # Default values for demo
        kwh = 50
        recipient_type = "home"
        
        # Get from request if provided
        if request.method == "POST" and request.json:
            kwh = float(request.json.get("kwh", 50))
            recipient_type = request.json.get("recipient_type", "home")
        
        # Generate certificate
        result = generate_certificate(kwh, recipient_type)
        
        return jsonify({
            "image_url": result["image_base64"],
            "impact_metric": result["impact_metric"],
            "co2_kg": result["co2_kg"],
            "ai_text": result["ai_text"],
            "certificate_id": result["certificate_id"] 
        })
        
    except Exception as e:
        print(f"Certificate Generation Error: {e}")
        return jsonify({
            "error": str(e),
            "image_url": None
        }), 500

# ========================================
# PREDICTION FEATURE ENDPOINTS
# ========================================
@app.get("/api/leaderboard")
def leaderboard():
    try:
        result = (
            supabase.table("user")
            .select("User_ID, User_Name, User_Img, Donate_Amount")
            .order("Donate_Amount", desc=True)
            .execute()
        )

        users = result.data
        
        # Add ranking
        for idx, u in enumerate(users):
            u["Rank"] = idx + 1

        return jsonify({"leaderboard": users})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/user/<int:user_id>/position")
def get_user_position(user_id):
    try:
        # Get all users sorted by donation
        result = (
            supabase.table("user")
            .select("User_ID, User_Name, User_Img, Donate_Amount")
            .order("Donate_Amount", desc=True)
            .execute()
        )

        users = result.data

        # Add Rank
        for i, u in enumerate(users):
            u["Rank"] = i + 1

        # Find the current user
        myUser = next((u for u in users if u["User_ID"] == user_id), None)
        if not myUser:
            return jsonify({"error": "User not found"}), 404

        # Compute how much more kWh needed to reach top 5
        top5_cutoff = (
            users[4]["Donate_Amount"] if len(users) >= 5 else 0
        )
        myUser["kWh_needed_for_top_5"] = max(0, top5_cutoff - myUser["Donate_Amount"])

        return jsonify(myUser)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/user/<int:user_id>/previous")
def get_previous_ranker(user_id):
    try:
        result = (
            supabase.table("user")
            .select("User_ID, User_Name, User_Img, Donate_Amount")
            .order("Donate_Amount", desc=True)
            .execute()
        )

        users = result.data
        for i, u in enumerate(users):
            u["Rank"] = i + 1

        # find current rank
        my_index = next((i for i,u in enumerate(users) if u["User_ID"] == user_id), None)
        if my_index is None or my_index == 0:
            return jsonify({"message": "No one ahead"}), 404

        previous_user = users[my_index - 1]
        return jsonify(previous_user)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/api/user-electricity/<int:user_id>")
def get_user_electricity(user_id):
    try:
        result = (
            supabase.table("user_electricity")
            .select("*")
            .eq("User_ID", user_id)
            .execute()
        )

        if not result.data:
            return jsonify({"error": "No electricity record found"}), 404

        row = result.data[0]

        return jsonify({
            "capacity": row["Electricity_Capacity"],
            "donated": row["Monthly_Donation"],
            "remaining": row["Electricity_Capacity"] - row["Monthly_Donation"]
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

@app.get("/api/user-profile/<int:user_id>")
def get_user_profile(user_id):
    try:
        result = (
            supabase.table("user")
            .select("User_ID, User_Name, User_Img")
            .eq("User_ID", user_id)
            .execute()
        )

        if not result.data:
            return jsonify({"error": "User not found"}), 404

        return jsonify(result.data[0])

    except Exception as e:
        print("User profile error:", e)
        return jsonify({"error": str(e)}), 500



@app.route("/user/<int:user_id>/ai-analysis", methods=["GET"])
def get_ai_analysis(user_id):
    """Get AI-powered analysis and recommendations for the user"""
    try:
        # Get the previous ranker
        previous_ranker = analytics.get_previous_ranker(user_id)

        # Extract the user_id if it exists
        previous_ranker_id = previous_ranker['user_id'] if previous_ranker else None

        # Get the patterns
        donation_context = analytics.get_yearly_patterns(
            user_id=user_id,
            previous_ranker_id=previous_ranker_id,
        )

        # Get AI analysis
        ai_result = agent.analyze(donation_context)

        return jsonify({
            "donation_context": donation_context,
            "ai_analysis": ai_result
        })
    except ValueError as e:
        print(f"ValueError in get_ai_analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Invalid user_id: {str(e)}"}), 400
    except Exception as e:
        print(f"Error in get_ai_analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
@app.post("/api/donate")
def donate_energy():
    try:
        data = request.json
        user_id = int(data.get("user_id"))
        kwh = int(float(data.get("kwh", 0)))     # <<< FIXED HERE

        if not user_id or kwh <= 0:
            return jsonify({"error": "Invalid user_id or donation amount"}), 400

        # 1. Read user_electricity
        result = (
            supabase.table("user_electricity")
            .select("*")
            .eq("User_ID", user_id)
            .execute()
        )

        if not result.data:
            return jsonify({"error": "Electricity record not found"}), 404

        row = result.data[0]
        current_monthly = int(row["Monthly_Donation"])   # ensure int
        capacity = int(row["Electricity_Capacity"])

        new_monthly = current_monthly + kwh
        if new_monthly > capacity:
            new_monthly = capacity

        # 2. UPDATE user_electricity
        supabase.table("user_electricity").update({
            "Monthly_Donation": int(new_monthly)
        }).eq("User_ID", user_id).execute()

        # 3. UPDATE user total donation
        result_user = (
            supabase.table("user")
            .select("Donate_Amount")
            .eq("User_ID", user_id)
            .single()
            .execute()
        )

        total_prev = int(result_user.data["Donate_Amount"])
        new_total = total_prev + kwh

        supabase.table("user").update({
            "Donate_Amount": int(new_total)
        }).eq("User_ID", user_id).execute()

        return jsonify({
            "message": "Donation updated successfully",
            "updated_monthly": new_monthly,
            "updated_total": new_total
        })

    except Exception as e:
        print("Donate API error:", e)
        return jsonify({"error": str(e)}), 500
    
@app.post("/api/save-transaction")
def save_transaction():
    try:
        data = request.json

        print("DATA RECEIVED:", data)

        certificate_id = data.get("certificate_id")
        user_id = int(data.get("user_id"))
        donation_kwh = int(data.get("donation_kwh"))
        impact_metric = data.get("impact_metric")
        context = data.get("context")
        co2 = float(data.get("co2"))

        # Save into Supabase
        result = supabase.table("transaction").insert({
            "Certificate_ID": certificate_id,
            "User_ID": user_id,
            "Donation_kwh": donation_kwh,
            "Impact_Metric": impact_metric,
            "Context": context,
            "Co2": co2
        }).execute()

        return jsonify({"message": "Transaction stored successfully!"})

    except Exception as e:
        print("Save transaction error:", e)
        return jsonify({"error": str(e)}), 500
    
@app.get("/api/transactions/<int:user_id>")
def get_transactions(user_id):
    try:
        result = (
            supabase.table("transaction")
            .select("Certificate_ID, User_ID, Date_Time, Donation_kwh, Impact_Metric, Context, Co2")
            .eq("User_ID", user_id)
            .order("Date_Time", desc=True)   # sort by timestamp
            .execute()
        )

        return jsonify(result.data), 200

    except Exception as e:
        print("GET TRANSACTIONS ERROR:", e)
        return jsonify({"error": str(e)}), 500

# ========================================
# VOICE-TO-RAG CHAT ENQUIRY ENDPOINT
# ========================================
@app.route("/api/chat-enquiry", methods=["POST"])
def chat_enquiry():
    """
    Handle chat enquiries with both audio and text input support
    
    Accepts:
    - multipart/form-data with 'audio' file (mp3, wav, etc.)
    - application/json with 'text' field
    
    Returns:
    - AI response from JamAI Action Table
    """
    try:
        print("\n" + "="*60)
        print("NEW CHAT ENQUIRY REQUEST")
        print(f"Content-Type: {request.content_type}")
        print(f"Request files: {list(request.files.keys())}")
        print(f"Request form: {list(request.form.keys())}")
        print("="*60 + "\n")
        
        query_text = None
        processing_result = None
        
        # Check if request contains a file (audio input)
        if 'audio' in request.files:
            audio_file = request.files['audio']
            
            # Validate file
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
            
            print(f"Saving audio file...")
            print(f"   - Original filename: {audio_file.filename}")
            print(f"   - Secure filename: {filename}")
            print(f"   - Unique filename: {unique_filename}")
            print(f"   - Full path: {audio_path}")
            
            audio_file.save(audio_path)
            file_size = os.path.getsize(audio_path)
            print(f"Audio file saved successfully!")
            print(f"   - Size: {file_size} bytes ({file_size/1024:.2f} KB)")
            
            try:
                # Process audio enquiry (transcribe + upload to knowledge base)
                print(f"Starting audio processing (transcription + RAG)...")
                processing_result = process_enquiry(audio_path, input_type='audio_path')
                print(f"Audio processing completed!")
                
                if not processing_result.get("success"):
                    error_msg = processing_result.get("error", "Unknown error")
                    print(f"Audio processing failed: {error_msg}")
                    return jsonify({
                        "error": "Audio processing failed",
                        "details": error_msg
                    }), 500
                
                # Extract transcript for chat query
                query_text = processing_result.get("transcript")
                print(f"Transcript extracted: {query_text[:100]}..." if len(query_text) > 100 else f"📝 Transcript: {query_text}")
                
            finally:
                # Clean up: delete temporary audio file
                try:
                    if os.path.exists(audio_path):
                        os.remove(audio_path)
                        print(f"Temporary file deleted: {audio_path}")
                except Exception as cleanup_error:
                    print(f"Cleanup warning: {cleanup_error}")
        
        # Check if request contains text input
        elif request.is_json:
            data = request.json
            query_text = data.get("text")
            
            if not query_text:
                return jsonify({"error": "No text provided"}), 400
            
            # Process text enquiry
            processing_result = process_enquiry(query_text, input_type='text')
        
        # Check for form data (alternative text input)
        elif 'text' in request.form:
            query_text = request.form.get('text')
            
            if not query_text:
                return jsonify({"error": "No text provided"}), 400
            
            # Process text enquiry
            processing_result = process_enquiry(query_text, input_type='text')
        
        else:
            return jsonify({
                "error": "Invalid request. Send either 'audio' file or 'text' field"
            }), 400
        
        # Query JamAI Action Table for response
        if not query_text:
            return jsonify({"error": "No query text generated"}), 500
        
        chat_response = query_jamai_chat(query_text)
        
        if not chat_response.get("success"):
            return jsonify({
                "error": "Failed to get chat response",
                "details": str(chat_response)
            }), 500
        
        # --- Extract only the assistant text ---
        raw_response = chat_response.get("response", "")

        # Match content inside either single or double quotes (non-greedy)
        match = re.search(r'content=(?P<quote>["\'])(.*?)\1', raw_response, re.DOTALL)

        # If match fails, fallback to full response
        assistant_text = match.group(2) if match else raw_response

        # Replace literal \n with actual newlines
        assistant_text = assistant_text.replace("\\n", "\n").strip()

        # Build response to frontend
        response_data = {
            "success": True,
            "query": query_text,
            "response": assistant_text,   # <-- only assistant text
            "input_type": processing_result.get("type") if processing_result else "text"
        }

        if processing_result and processing_result.get("type") == "audio":
            response_data["audio_metadata"] = {
                "transcription_id": processing_result.get("transcription_metadata", {}).get("id"),
                "audio_duration": processing_result.get("transcription_metadata", {}).get("audio_duration"),
                "knowledge_base_uploaded": processing_result.get("knowledge_base_result", {}).get("success", False)
            }
        
        return jsonify(response_data), 200
    
    except Exception as e:
        print(f"Chat enquiry error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    print("Flask server running on http://127.0.0.1:5000")
    app.run(port=5000, debug=True)
