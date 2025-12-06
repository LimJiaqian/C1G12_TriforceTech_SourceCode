from backend.database.supabase import supabase
import json
import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("SEA_LION_API_KEY")

URL = "https://api.sea-lion.ai/v1/completions"

def get_area_data():
    """Fetch all rows from Supabase 'area' table."""
    try:
        result = supabase.table("area").select("*").execute()
        return result.data if result.data else []
    except Exception as e:
        print("Error fetching Supabase area table:", e)
        return []


def get_top5_energy_need():
    """Call SEA-LION AI and enrich output with Area + District from Supabase."""
    
    # Step 1: AI System prompt
    system_prompt = """
    You are an Energy Need Prioritization AI.

    Your task:
    Analyze the provided community dataset and determine the TOP 5 areas needing urgent electricity sponsorship.

    You MUST:
    1. Read the dataset carefully.
    2. Perform real-time web searches for each location’s State to identify any natural disasters or emergency events.
    - Search for terms like "<State> flood", "<State> storm", "<State> landslide", "<State> electricity outage".
    - Consider the severity of any recent events.
    3. Combine both:
    - Dataset information (economy, electricity status, population, grid status, facility purpose, etc.)
    - Real-time disaster information
    4. Use your own reasoning and judgement (NO fixed formulas) to determine which areas are most in need.
    5. Rank the areas from highest to lowest need.
    6. Return ONLY the top 5.

    When ranking, consider factors such as:
    - Whether the area is blackout or unstable
    - Vulnerability (rural, deep rural, low income)
    - Importance of the facility (medical > school > shelter > mosque > household)
    - Population served
    - Impact of natural disasters based on your web findings
    - Any additional insights based on public information

    Output the result as a JSON array of 5 items with fields:
    Rank, id, Name, State, LocationType, Reasoning
    """

    # Your existing dataset
    area_table = get_area_data()
    user_prompt = json.dumps(area_table, indent=2)

    payload = {
        "model": "aisingapore/Gemma-SEA-LION-v4-27B-IT",
        "prompt": system_prompt + "\n\n" + user_prompt,
        "temperature": 0.2,
        "max_tokens": 800,
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    # Step 2: AI request (with fallback)
    try:
        response = requests.post(URL, json=payload, headers=headers, timeout=25)
        result = response.json()
        llm_text = result["choices"][0]["text"]

        # Extract JSON list
        clean = llm_text[llm_text.find("[") : llm_text.rfind("]") + 1]
        ai_list = json.loads(clean)

    except Exception as e:
        print(" AI error:", e)
        return get_fallback_top5()

    #  Step 3: Fetch Supabase reference table
    area_table = get_area_data()

    #  Step 4: Enrich AI output with “Area” and “District”
    enriched = []
    for item in ai_list:
        match = next(
            (
                row for row in area_table
                if row["Name"].lower() == item["Name"].lower()
                and row["State"].lower() == item["State"].lower()
            ),
            None
        )

        if match:
            item["Area"] = match.get("Area")
            item["District"] = match.get("District")
        else:
            item["Area"] = None
            item["District"] = None

        enriched.append(item)

    return enriched


def get_fallback_top5():
    """Your existing fallback list (unchanged)."""
    return [
        {
            "Rank": 1,
            "id": 1,
            "Name": "Kampung Batu Hampar",
            "State": "Kelantan",
            "LocationType": "Medical Clinic",
            "Reasoning": "Rural medical facility with unstable electricity",
            "Area": "Kapit Divisi",
            "District": "Song",
        },
        {
            "Rank": 2,
            "id": 5,
            "Name": "Pos Lenjang Orang Asli",
            "State": "Pahang",
            "LocationType": "Remote Village",
            "Reasoning": "Deep rural Orang Asli settlement with no grid access",
            "Area": "Interior Divisi",
            "District": "Pitas",
        },
        {
            "Rank": 3,
            "id": 3,
            "Name": "SK Ulu Tembeling",
            "State": "Pahang",
            "LocationType": "Primary School",
            "Reasoning": "Remote school serving 80 students",
            "Area": "Bandaraya Johor Bahru",
            "District": "Gopeng",
        },
        {
            "Rank": 4,
            "id": 7,
            "Name": "Kampung Gual Periok",
            "State": "Terengganu",
            "LocationType": "Community Center",
            "Reasoning": "Coastal village prone to flooding",
            "Area": "Petaling Jaya",
            "District": "Petaling",
        },
        {
            "Rank": 5,
            "id": 9,
            "Name": "Felda Jengka",
            "State": "Pahang",
            "LocationType": "Settlement",
            "Reasoning": "Large agricultural community with grid instability",
            "Area": "Kota Bharu",
            "District": "Kota Bharu",
        },
    ]
