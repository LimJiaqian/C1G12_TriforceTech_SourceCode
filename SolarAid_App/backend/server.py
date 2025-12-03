from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
from backend.sealion_ai.area_detection import get_top5_energy_need
from backend.sealion_ai.thanks_ai import generate_thankyou_message
from backend.sealion_ai.certificate_generator import generate_certificate
from backend.analytics import DonationAnalytics
from backend.gemini_ai.ai_agent import DonationAIAgent
from backend.database.supabase import supabase

app = Flask(__name__)
CORS(app)

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
@app.route("/leaderboard", methods=["GET"])
def get_leaderboard():
    try:
        leaderboard_df = analytics.get_latest_leaderboard()
        if leaderboard_df.empty:
            return jsonify({"error": "No donation data available"}), 404
        return jsonify({
            "year": int(analytics.latest_year),
            "leaderboard": leaderboard_df.to_dict('records')
        })
    except Exception as e:
        print(f"Error in get_leaderboard: {str(e)}")  # Add logging
        return jsonify({"error": str(e)}), 500

@app.route("/user/<int:user_id>/position", methods=["GET"])
def get_user_position(user_id):
    try:
        position = analytics.get_user_position(user_id)
        if position is None:
            return jsonify({"error": "No data available"}), 404
        return jsonify(position)
    except ValueError as e:
        return jsonify({"error": f"Invalid user_id: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/user/<int:user_id>/previous", methods=["GET"])
def get_previous_ranker(user_id):
    try:
        prev_user = analytics.get_previous_ranker(user_id)
        if prev_user is None:
            return jsonify({"message": "No one ahead"}), 404
        return jsonify(prev_user)
    except Exception as e:
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

if __name__ == "__main__":
    print("Flask server running on http://127.0.0.1:5000")
    app.run(port=5000, debug=True)
