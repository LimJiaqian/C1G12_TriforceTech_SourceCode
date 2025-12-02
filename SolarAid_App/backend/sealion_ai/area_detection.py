import json
import requests
from dotenv import load_dotenv
import os
from ..area import area_data    

# Load .env variables
load_dotenv()
API_KEY = os.getenv("SEA_LION_API_KEY")

URL = "https://api.sea-lion.ai/v1/completions"

def get_top5_energy_need():
    """
    Calls SEA-LION AI to rank the top 5 communities needing electricity
    based on real-time disaster info + dataset.
    Returns a Python dictionary or list.
    """

    if not API_KEY:
        return {"error": "API key not found in .env"}

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
    - Peak hour urgency
    - Population served
    - Impact of natural disasters based on your web findings
    - Any additional insights based on public information

    Output the result as a JSON array of 5 items with fields:
    Rank, id, Name, State, LocationType, Reasoning
    """

    user_prompt = (
        "Determine the TOP 5 areas needing electricity sponsorship:\n\n"
        + json.dumps(area_data, indent=2)
    )

    payload = {
        "model": "aisingapore/Gemma-SEA-LION-v4-27B-IT",
        "prompt": system_prompt + "\n\n" + user_prompt,
        "temperature": 0.2,
        "max_tokens": 800
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(URL, headers=headers, json=payload, timeout=10)
        result = response.json()

        llm_text = result["choices"][0]["text"]

        # Extract JSON only
        try:
            cleaned = llm_text[llm_text.find("[") : llm_text.rfind("]") + 1]
            parsed = json.loads(cleaned)
            # Ensure it's an array
            if isinstance(parsed, list):
                return parsed
            else:
                print(f"⚠️ SEA-LION returned non-array: {parsed}")
                return get_fallback_top5()
        except Exception as parse_err:
            print(f"⚠️ JSON parsing error: {parse_err}")
            return get_fallback_top5()

    except Exception as e:
        print(f"⚠️ SEA-LION API error: {e}")
        return get_fallback_top5()


def get_fallback_top5():
    """
    Returns a hardcoded fallback list of top 5 areas when AI call fails
    """
    return [
        {
            "Rank": 1,
            "id": 1,
            "Name": "Kampung Batu Hampar",
            "State": "Kelantan",
            "LocationType": "Medical Clinic",
            "Reasoning": "Rural medical facility with unstable electricity and high vulnerability during monsoon season"
        },
        {
            "Rank": 2,
            "id": 5,
            "Name": "Pos Lenjang Orang Asli",
            "State": "Pahang",
            "LocationType": "Remote Village",
            "Reasoning": "Deep rural Orang Asli settlement with no grid access and urgent basic needs"
        },
        {
            "Rank": 3,
            "id": 3,
            "Name": "SK Ulu Tembeling",
            "State": "Pahang",
            "LocationType": "Primary School",
            "Reasoning": "Remote school serving 80 students with frequent power outages affecting education"
        },
        {
            "Rank": 4,
            "id": 7,
            "Name": "Kampung Gual Periok",
            "State": "Terengganu",
            "LocationType": "Community Center",
            "Reasoning": "Coastal village prone to flooding with electricity issues during natural disasters"
        },
        {
            "Rank": 5,
            "id": 9,
            "Name": "Felda Jengka",
            "State": "Pahang",
            "LocationType": "Settlement",
            "Reasoning": "Large agricultural community with grid instability affecting 500+ families"
        }
    ]


if __name__ == "__main__":
    top5 = get_top5_energy_need()
    print(json.dumps(top5, indent=2))