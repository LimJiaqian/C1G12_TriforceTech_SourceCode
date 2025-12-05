import json
import os
from dotenv import load_dotenv
import google.generativeai as genai  
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

current_date = datetime.now().strftime("%Y-%m-%d")

class DonationAIAgent:

    def __init__(self, api_key=API_KEY):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")  

    def analyze(self, donation_context):
        prompt = f"""
You are an AI energy advisor. You have access to:

1. Donation patterns, cumulative totals and user info in JSON:
{json.dumps(donation_context, indent=2)}

2. External context:
   - Electricity usage trends in Malaysia
   - Weather, seasonal patterns, holidays, work-from-home effects

Your tasks:

1. Forecast how much energy (kWh) the user should save next month to surpass the previous ranker:
   - "savedKwh": Difference in kWh needed to climb one rank
   - "minRequired": If previous ranker doesn't donate more
   - "maxNeeded": If previous ranker also donates savedKwh kWh

2. Provide 3 practical, area-appropriate kWh-saving tips in "tips".

Current date: {current_date}.

Return STRICTLY a JSON object with these keys only:
"savedKwh", "minRequired", "maxNeeded", "tips".
"""
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            start = text.find("{")
            end = text.rfind("}") + 1
            
            if start == -1 or end == 0:
                raise ValueError("No JSON found in response")
            
            json_text = text[start:end]
            result = json.loads(json_text)

            # Ensure keys exist
            required_keys = ["savedKwh", "minRequired", "maxNeeded", "tips"]
            for key in required_keys:
                if key not in result:
                    raise ValueError(f"Missing key '{key}' in AI response")
            
            # Convert numeric values to ensure they're numbers
            result["savedKwh"] = float(result["savedKwh"])
            result["minRequired"] = float(result["minRequired"])
            result["maxNeeded"] = float(result["maxNeeded"])
            
            return result

        except Exception as e:
            # Fallback if AI fails
            print(f"Error in AI analysis: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "savedKwh": 0,
                "minRequired": 0,
                "maxNeeded": 0,
                "tips": ["Unable to generate tips at this time"]
            }
