from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
from backend.sealion_ai.area_detection import get_top5_energy_need
from backend.sealion_ai.thanks_ai import generate_thankyou_message
from backend.sealion_ai.certificate_generator import generate_certificate
from backend.database.supabase import supabase
from backend.cloudflare_workers_ai.prediction_agent import (
    create_prediction_agent_from_env,
)
from backend.cloudflare_workers_ai.sql_agent import create_agent_from_env
from backend.cloudflare_workers_ai.research_agent import create_energy_agent_from_env

app = Flask(__name__)
CORS(app)

@app.post("/api/login")
def login():
    """Login user using Supabase 'user' table"""
    try:
        data = request.json
        email = data.get("email")
        password = data.get("password")

        # Query Supabase
        result = supabase.table("user").select("*").eq("username", email).execute()

        if not result.data:
            return jsonify({"error": "User not found"}), 404

        user = result.data[0]

        # Check password
        if user["User_password"] != password:
            return jsonify({"error": "Incorrect password"}), 401

        return jsonify(
            {
                "message": "Login successful",
                "user_id": user["User_ID"],
                "username": user["username"],
                "token": "demo-token",  # You can replace with JWT later
            }
        )

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

        return jsonify(
            {
                "image_url": result["image_base64"],
                "impact_metric": result["impact_metric"],
                "co2_kg": result["co2_kg"],
                "ai_text": result["ai_text"],
                "certificate_id": result["certificate_id"],
            }
        )

    except Exception as e:
        print(f"Certificate Generation Error: {e}")
        return jsonify({"error": str(e), "image_url": None}), 500


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


@app.get("/api//user/<int:user_id>/position")
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
        top5_cutoff = users[4]["Donate_Amount"] if len(users) >= 5 else 0
        myUser["kWh_needed_for_top_5"] = max(0, top5_cutoff - myUser["Donate_Amount"] + 1)

        return jsonify(myUser)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/api/user/<int:user_id>/previous")
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
        my_index = next(
            (i for i, u in enumerate(users) if u["User_ID"] == user_id), None
        )
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

        return jsonify(
            {
                "capacity": row["Electricity_Capacity"],
                "donated": row["Monthly_Donation"],
                "remaining": row["Electricity_Capacity"] - row["Monthly_Donation"],
            }
        )

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


sql_agent = create_agent_from_env(verbose=False)
research_agent = create_energy_agent_from_env(verbose=False)
prediction_agent = create_prediction_agent_from_env(
    sql_agent, research_agent, verbose=False
)


@app.route("/api/predict/<int:user_id>", methods=["GET"])
def get_prediction(user_id):
    """
    Analyzes user and competitor data, and external context to generate
    energy savings predictions for a given user_id.
    """
    if prediction_agent is None:
        return (
            jsonify(
                {
                    "error": "Service Unavailable",
                    "detail": "Prediction agents failed to initialize on startup.",
                }
            ),
            503,
        )

    try:
        # Call the core prediction logic
        print(f"\n--- Calling predict_savings for user_id: {user_id} ---")
        result = prediction_agent.predict_savings(user_id=user_id)
        print(result)

        # Flask's jsonify automatically handles serialization
        return jsonify(result), 200

    except ValueError as e:
        # Handle errors during data fetching (e.g., user not found, SQL error)
        return jsonify({"error": "Invalid Data or Request", "detail": str(e)}), 400
    except Exception as e:
        # Handle general processing errors (e.g., LLM generation failure)
        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "detail": f"Prediction processing error: {str(e)}",
                }
            ),
            500,
        )
    
@app.post("/api/donate")
def donate_energy():
    try:
        data = request.json
        user_id = int(data.get("user_id"))
        kwh = int(float(data.get("kwh", 0)))     

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


if __name__ == "__main__":
    print("Flask server running on http://127.0.0.1:5000")
    app.run(port=5000, debug=True)