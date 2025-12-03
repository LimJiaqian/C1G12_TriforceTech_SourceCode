import os
import json
from typing import Optional, Dict, Any, List
from datetime import date
from dotenv import load_dotenv
from langchain_cloudflare import ChatCloudflareWorkersAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from backend.cloudflare_workers_ai.sql_agent import (
    create_agent_from_env as create_sql_agent,
)
from backend.cloudflare_workers_ai.research_agent import create_energy_agent_from_env


class CloudflareEnergyPredictionAgent:
    """
    Energy Savings Prediction Agent for climbing the donation leaderboard.

        - Analyzes user and competitor donation patterns combined with external research to generate personalized energy-saving predictions and recommendations.

    """

    DEFAULT_MODEL = "@cf/meta/llama-3.1-8b-instruct"
    DEFAULT_TEMPERATURE = 0.3
    DEFAULT_MAX_TOKENS = 1000
    MIN_PROBABILITY = 0
    MAX_PROBABILITY = 100

    def __init__(
        self,
        sql_agent,
        research_agent,
        account_id: str,
        api_token: str,
        model: str = DEFAULT_MODEL,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        verbose: bool = True,
    ):
        """
        Initialize the Energy Prediction Agent.

        """
        self.verbose = verbose
        self.sql_agent = sql_agent
        self.research_agent = research_agent
        self.model_name = model

        if not account_id or not api_token:
            raise ValueError("Cloudflare account_id and api_token are required")

        self.llm = self._create_llm(model, account_id, api_token, temperature, max_tokens)
        self.prediction_prompt = self._get_prediction_prompt()
        self.prediction_chain = self.prediction_prompt | self.llm | JsonOutputParser()

        if self.verbose:
            print("Energy Prediction Agent initialized")
            print(f"  Model: {model}")
            print(f"  Temperature: {temperature}")
            print(f"  Output: JSON format\n")

    def _create_llm(
        self,
        model: str,
        account_id: str,
        api_token: str,
        temperature: float,
        max_tokens: int,
    ) -> ChatCloudflareWorkersAI:
        """
        Create and configure Cloudflare LLM instance.
        
        """
        return ChatCloudflareWorkersAI(
            model=model,
            cloudflare_account_id=account_id,
            cloudflare_api_token=api_token,
            temperature=temperature,
            max_tokens=max_tokens,
            model_kwargs={"streaming": False},
        )

    def _get_prediction_prompt(self) -> ChatPromptTemplate:
        """
        Create the prompt template for AI predictions.
        
        """
        SYSTEM_PROMPT = """You are an AI energy advisor specializing in Malaysian energy-saving recommendations.

You analyze donation/saving patterns and external factors to provide accurate predictions.

INPUT DATA:
1. User Profile:
   - user_id, donate_amount, state, district
   - last_donation_date, donations_per_month, donation_averages

2. Competitor Profile:
   - Donation amounts and patterns of the user ranked immediately above

3. External Context:
   - Weather trends, electricity tariffs, holidays, seasonal events in Malaysia

OUTPUT REQUIREMENTS:
Generate a JSON object with the following fields:

- predicted_difference (float): Gap between competitor and user donations
- predicted_increase (float): Estimated competitor's next donation increase
- userTrend (float): User's donation trend (-1 = decreasing, 0 = stable, 1 = increasing)
- competitorMomentum (int): Probability (0-100) that competitor will donate next month
- rankProbability (int): Probability (0-100) user can climb one rank next month
- tips (array): Exactly 3 actionable, location-specific energy-saving recommendations to help the user climb the leaderboard

IMPORTANT:
- Return ONLY valid JSON, no markdown or explanations
- Base predictions on data patterns and external context
- Keep tips practical and relevant to the user's location
- Consider seasonal factors (monsoon, hot season, holidays)"""

        USER_PROMPT = """Current Date: {current_date}

USER & COMPETITOR DATA:
{donation_context}

EXTERNAL CONTEXT:
{external_context}

Generate prediction JSON with: predicted_difference, predicted_increase, userTrend, competitorMomentum, rankProbability, tips"""

        return ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("user", USER_PROMPT)
        ])

    def _get_donation_context(self, user_id: str) -> Dict[str, Any]:
        """
        Fetch comprehensive donation context for a user.

        """
        if self.verbose:
            print(f"Fetching donation context for user_id: {user_id}")

        # Query 1: Get user basic info including donate_amount from user table
        user_query = f"""
            Find the user information for user ID {user_id}.
            Return JSON with the following fields from the user table:
            - User_ID
            - Donate_Amount (in user table)
            - State
            - District
        """

        # Query 2: Get donation statistics
        donation_stats_query = f"""
            Analyze the donation history for user ID {user_id}.
            From the donation table where Donor_ID equals {user_id}, calculate:
            - last_donation_date: the most recent Donation_Time
            - total_donations: count of all Donation_ID records
            - donation_averages: average of all Donation_Amount_kWh values
            
            Return as JSON with these three fields.
        """

        try:
            # Execute user query
            user_result = self.sql_agent.query(user_query, output_format="JSON")
            user_data = json.loads(user_result["answer"]) if isinstance(user_result["answer"], str) else user_result["answer"]
            
            # Execute donation stats query
            stats_result = self.sql_agent.query(donation_stats_query, output_format="JSON")
            stats_data = json.loads(stats_result["answer"]) if isinstance(stats_result["answer"], str) else stats_result["answer"]
            
            # Merge the results
            context = {
                "User_ID": user_data.get("User_ID", user_id),
                "Donate_Amount": user_data.get("Donate_Amount", 0),
                "state": user_data.get("State", "Unknown"),
                "district": user_data.get("District", "Unknown"),
                "last_donation_date": stats_data.get("last_donation_date"),
                "total_donations": stats_data.get("total_donations", 0),
                "donation_averages": stats_data.get("donation_averages", 0)
            }
            
            if self.verbose:
                print(f"✓ Context retrieved for user {user_id}")
                print(f"  Donate Amount: {context['Donate_Amount']} kWh")
                print(f"  Location: {context['district']}, {context['state']}\n")
            
            return context
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            raise ValueError(f"Failed to parse donation context for user {user_id}: {str(e)}")

    def _get_external_context(self, state: str, district: str) -> str:
        """
        Retrieve location-specific external context.

        """
        if self.verbose:
            print(f"Fetching external context for {district}, {state}")

        try:
            result = self.research_agent.get_energy_context(state, district)
            context = result.get("answer", "No external context available")
            
            if self.verbose:
                print(f"✓ External context retrieved\n")
            
            return context
        except Exception as e:
            if self.verbose:
                print(f"Warning: Could not fetch external context: {str(e)}\n")
            return f"External context unavailable for {district}, {state}"

    def _get_competitor_context(self, user_id: str) -> Dict[str, Any]:
        """
        Fetch donation context of the user ranked immediately above.

        """
        if self.verbose:
            print(f"Identifying competitor above user_id: {user_id}")

        # Get current user's donation amount
        current_user_query = f"""
            SELECT "Donate_Amount"
            FROM "user"
            WHERE "User_ID" = {user_id};
        """
        
        try:
            current_result = self.sql_agent.query(current_user_query, output_format="JSON")
            answer = current_result["answer"]
            parsed = json.loads(answer) if isinstance(answer, str) else answer
            current_amount = float(parsed["Donate_Amount"])
        except Exception as e:
            raise ValueError(f"Failed to get user's donation amount: {str(e)}")

        # Find next higher donor
        competitor_query = f"""
            SELECT "User_ID"
            FROM "user"
            WHERE "Donate_Amount" > {current_amount}
            ORDER BY "Donate_Amount" ASC
            LIMIT 1;
        """
        
        try:
            competitor_result = self.sql_agent.query(competitor_query, output_format="JSON")
            answer = competitor_result["answer"]
            next_rank_user = json.loads(answer) if isinstance(answer, str) else answer
            competitor_id = next_rank_user.get("User_ID", user_id)
        except Exception:
            # If no higher donor, user is already top-ranked
            if self.verbose:
                print(f"User {user_id} is already top-ranked\n")
            competitor_id = user_id

        # Fetch full competitor context
        context = self._get_donation_context(competitor_id)
        
        if self.verbose:
            print(f"✓ Competitor context retrieved (User {competitor_id})\n")
        
        return context

    def _validate_and_sanitize_prediction(self, ai_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize AI-generated prediction values.

        """
        # Ensure all required fields exist with defaults
        validated = {
            "predicted_difference": float(ai_result.get("predicted_difference", 0)),
            "predicted_increase": float(ai_result.get("predicted_increase", 0)),
            "userTrend": max(-1.0, min(1.0, float(ai_result.get("userTrend", 0)))),
            "competitorMomentum": max(self.MIN_PROBABILITY, min(self.MAX_PROBABILITY, int(ai_result.get("competitorMomentum", 50)))),
            "rankProbability": max(self.MIN_PROBABILITY, min(self.MAX_PROBABILITY, int(ai_result.get("rankProbability", 50)))),
            "tips": []
        }

        # Extract tips and ensure they're strings (not dictionaries)
        raw_tips = ai_result.get("tips", [])
        for tip in raw_tips:
            if isinstance(tip, dict):
                # If tip is a dict with 'tip' key, extract the string
                tip_text = tip.get("tip", str(tip))
            else:
                # If tip is already a string
                tip_text = str(tip)
            validated["tips"].append(tip_text)

        # Ensure we have exactly 3 tips
        default_tips = [
            "Monitor your energy usage regularly to identify saving opportunities",
            "Use energy-efficient appliances to reduce electricity consumption",
            "Schedule high-energy activities during off-peak hours to save on costs"
        ]
        
        while len(validated["tips"]) < 3:
            validated["tips"].append(default_tips[len(validated["tips"])])
        
        # Limit to exactly 3 tips
        validated["tips"] = validated["tips"][:3]

        return validated

    def predict_savings(self, user_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive energy savings prediction for a user.

        """
        try:
            if self.verbose:
                print(f"\n{'='*70}")
                print(f"GENERATING PREDICTION FOR USER {user_id}")
                print(f"{'='*70}\n")

            # Step 1: Fetch user context
            user_context = self._get_donation_context(user_id)
            user_total = float(user_context.get("Donate_Amount", 0))
            user_state = user_context.get("state", "Selangor")
            user_district = user_context.get("district", "Petaling")

            # Step 2: Fetch competitor context
            competitor_context = self._get_competitor_context(user_id)
            competitor_total = float(competitor_context.get("Donate_Amount", user_total))
            competitor_state = competitor_context.get("state", user_state)
            competitor_district = competitor_context.get("district", user_district)

            # Step 3: Fetch external contexts (only if location data exists)
            user_external = "No location data available"
            competitor_external = "No location data available"
            
            if user_state and user_state != "Unknown" and user_district and user_district != "Unknown":
                user_external = self._get_external_context(user_state, user_district)
            
            if (competitor_state and competitor_state != "Unknown" and 
                competitor_district and competitor_district != "Unknown"):
                competitor_external = self._get_external_context(competitor_state, competitor_district)

            # Step 4: Prepare AI input
            current_date = date.today().strftime("%B %d, %Y")
            
            donation_data = {
                "user": {
                    "user_id": user_context.get("User_ID"),
                    "donate_amount": user_context.get("Donate_Amount"),
                    "state": user_state,
                    "district": user_district,
                    "last_donation_date": user_context.get("last_donation_date"),
                    "total_donations": user_context.get("total_donations"),
                    "donation_averages": user_context.get("donation_averages")
                },
                "competitor": {
                    "user_id": competitor_context.get("User_ID"),
                    "donate_amount": competitor_context.get("Donate_Amount"),
                    "state": competitor_state,
                    "district": competitor_district,
                    "last_donation_date": competitor_context.get("last_donation_date"),
                    "total_donations": competitor_context.get("total_donations"),
                    "donation_averages": competitor_context.get("donation_averages")
                }
            }
            
            external_data = f"""User Location Context ({user_state}, {user_district}):
            {user_external}

            Competitor Location Context ({competitor_state}, {competitor_district}):
            {competitor_external}"""

            model_input = {
                "current_date": current_date,
                "donation_context": json.dumps(donation_data, indent=2),
                "external_context": external_data
            }

            # Step 5: Generate AI prediction
            if self.verbose:
                print("Generating AI prediction...\n")
            
            ai_result = self.prediction_chain.invoke(model_input)
            validated_result = self._validate_and_sanitize_prediction(ai_result)

            # Step 6: Calculate final metrics with safety rules
            predicted_diff = validated_result["predicted_difference"]
            
            # Ensure positive values and apply +1 kWh buffer to guarantee rank climb
            savedKwh = max(abs(competitor_total - user_total) + 1, 1.0)
            minRequired = round(savedKwh * 1.05, 2)  # 5% safety buffer
            
            predicted_increase = validated_result["predicted_increase"]
            maxNeeded = round(savedKwh + abs(predicted_increase) * 1.3, 2)  # 30% buffer on increase

            response = {
                "savedKwh": round(savedKwh, 2),
                "minRequired": minRequired,
                "maxNeeded": max(maxNeeded, minRequired),  # Ensure max >= min
                "userTrend": validated_result["userTrend"],
                "competitorMomentum": validated_result["competitorMomentum"],
                "rankProbability": validated_result["rankProbability"],
                "tips": validated_result["tips"]
            }

            if self.verbose:
                print("✓ Prediction generated successfully")
                print(f"  User: {user_district}, {user_state} | {user_total} kWh")
                print(f"  Competitor: {competitor_district}, {competitor_state} | {competitor_total} kWh")
                print(f"  Gap: {competitor_total - user_total} kWh\n")
                print(f"{'='*70}\n")

            return response

        except Exception as e:
            error_msg = f"Prediction failed for user {user_id}: {str(e)}"
            if self.verbose:
                print(f"{error_msg}\n")
            raise Exception(error_msg)


def create_prediction_agent_from_env(
    sql_agent,
    research_agent,
    verbose: bool = True,
    **kwargs
) -> CloudflareEnergyPredictionAgent:
    """
    Create energy prediction agent from environment variables.

    """
    load_dotenv()

    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    api_token = os.environ.get("CF_AI_API_TOKEN")

    if not account_id:
        raise ValueError("CLOUDFLARE_ACCOUNT_ID not found in environment variables")
    if not api_token:
        raise ValueError("CF_AI_API_TOKEN not found in environment variables")

    return CloudflareEnergyPredictionAgent(
        sql_agent=sql_agent,
        research_agent=research_agent,
        account_id=account_id,
        api_token=api_token,
        verbose=verbose,
        **kwargs,
    )


if __name__ == "__main__":
    """Example usage of the Energy Prediction Agent."""
    print("=" * 70)
    print("ENERGY SAVINGS PREDICTION AGENT - EXAMPLE")
    print("=" * 70)
    print()

    try:
        # Initialize agents
        sql_agent = create_sql_agent()
        research_agent = create_energy_agent_from_env()
        prediction_agent = create_prediction_agent_from_env(sql_agent, research_agent)

        # Generate prediction
        result = prediction_agent.predict_savings(user_id="1008")

        # Display results
        print("\nPREDICTION RESULTS:")
        print(f"  Energy to Save: {result['savedKwh']} kWh")
        print(f"  Minimum Required: {result['minRequired']} kWh")
        print(f"  Maximum Needed: {result['maxNeeded']} kWh")
        print(f"  User Trend: {result['userTrend']}")
        print(f"  Competitor Momentum: {result['competitorMomentum']}%")
        print(f"  Rank Climb Probability: {result['rankProbability']}%")
        print("\n ENERGY SAVING TIPS:")
        for i, tip in enumerate(result.get("tips", []), 1):
            print(f"  {i}. {tip}")
        print()

    except Exception as e:
        print(f"\nError: {str(e)}\n")