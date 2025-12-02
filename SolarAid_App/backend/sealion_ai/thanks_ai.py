import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("SEA_LION_API_KEY")

URL = "https://api.sea-lion.ai/v1/completions"

def generate_thankyou_message():
    system_prompt = "Generate a short, warm, unique thank-you message for someone who donated electricity."
    user_prompt = "Write only one sentence, inspiring and grateful."

    payload = {
        "model": "aisingapore/Gemma-SEA-LION-v4-27B-IT",
        "prompt": system_prompt + "\n\n" + user_prompt,
        "temperature": 1.0,
        "max_tokens": 60
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(URL, headers=headers, json=payload)
        data = response.json()

        print("RAW AI RESPONSE:", data)

        # --- If AI fails ---
        if "choices" not in data:
            return "Thank you! Your donation brings hope and light to a community."

        text = data["choices"][0]["text"].strip()

        # --- If AI returns empty string ---
        if not text:
            return "Thank you! Your generosity is making a real impact."

        return text

    except Exception as e:
        print("AI ERROR:", e)
        return "Thank you! Your support helps power a brighter future."
