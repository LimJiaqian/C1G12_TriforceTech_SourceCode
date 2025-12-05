import os
import json
import time
import json
from ast import literal_eval

from typing import Dict, Any, Optional, Union
from datetime import date, datetime
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from langchain_cloudflare import ChatCloudflareWorkersAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser



class PredictionCache:
    """Simple in-memory cache with TTL to prevent duplicate predictions."""

    def __init__(self, ttl_seconds: int = 300):
        self.cache = {}
        self.ttl_seconds = ttl_seconds

    def _get_key(self, user_id: str) -> str:
        """Generate cache key for user prediction."""
        return f"pred_{user_id}"

    def get(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached prediction if still valid."""
        key = self._get_key(user_id)
        if key in self.cache:
            cached_data, timestamp = self.cache[key]
            age = time.time() - timestamp
            if age < self.ttl_seconds:
                return cached_data
            else:
                del self.cache[key]
        return None

    def set(self, user_id: str, data: Dict[str, Any]) -> None:
        """Cache prediction result."""
        key = self._get_key(user_id)
        self.cache[key] = (data, time.time())

    def clear(self) -> None:
        """Clear all cached predictions."""
        self.cache.clear()

    def remove(self, user_id: str) -> None:
        """Remove specific user's cached prediction."""
        key = self._get_key(user_id)
        if key in self.cache:
            del self.cache[key]


class BidirectionalEnergyPredictionAgent:
    """
    Bidirectional Energy Savings Prediction Agent with offensive & defensive strategies.

    Features:
    - Offensive: How to catch up with higher-ranked users
    - Defensive: How to maintain position and avoid being overtaken
    - Promotes sustained energy conservation (SDG 7)
    - Caching and request deduplication for performance
    """

    MIN_PROBABILITY = 0
    MAX_PROBABILITY = 100

    def __init__(
        self,
        sql_agent,
        research_agent,
        account_id: str,
        api_token: str,
        model: str = "@cf/meta/llama-3.1-8b-instruct",
        temperature: float = 0.3,
        max_tokens: int = 800,
        verbose: bool = True,
        enable_external_context: bool = False,
        max_workers: int = 2,
        cache_ttl: int = 300,
        status_callback=None,
    ):
        self.verbose = verbose
        self.sql_agent = sql_agent
        self.research_agent = research_agent
        self.model_name = model
        self.enable_external_context = enable_external_context
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.prediction_cache = PredictionCache(ttl_seconds=cache_ttl)
        self.in_flight = {}

        if not account_id or not api_token:
            raise ValueError("Cloudflare account_id and api_token are required")

        self.llm = self.create_llm(
            model, account_id, api_token, temperature, max_tokens
        )
        self.prediction_prompt = self.get_prediction_prompt()
        self.prediction_chain = self.prediction_prompt | self.llm | JsonOutputParser()

        if self.verbose:
            print(f"Bidirectional Prediction Agent initialized")

            if enable_external_context:
                self._validate_research_agent()

        self.status_callback = status_callback

    def create_llm(
        self,
        model: str,
        account_id: str,
        api_token: str,
        temperature: float,
        max_tokens: int,
    ) -> ChatCloudflareWorkersAI:
        return ChatCloudflareWorkersAI(
            model=model,
            cloudflare_account_id=account_id,
            cloudflare_api_token=api_token,
            temperature=temperature,
            max_tokens=max_tokens,
            model_kwargs={"streaming": False},
        )

    def _update_status(self, message: str, progress: int = None):
        """Send status update to frontend."""
        if self.status_callback:
            self.status_callback(
                {"message": message, "progress": progress, "timestamp": time.time()}
            )
        if self.verbose:
            if progress is not None:
                print(f"[{progress}%] {message}")
            else:
                print(f"- {message}")

    def get_prediction_prompt(self) -> ChatPromptTemplate:
        SYSTEM_PROMPT = """You are an AI energy advisor for Malaysian energy-saving recommendations promoting SDG 7.

        Provide CONCRETE, ACTIONABLE predictions with specific numbers.

        CATCH-UP ANALYSIS (to overtake the user ahead):
        - predicted_increase: How much kWh the competitor will likely save this month
        - userTrend: User's recent momentum (-1=declining, 0=stable, 1=growing fast)
        - competitorMomentum: Competitor's growth rate (0-100, higher=they're accelerating)
        - overtakeProbability: Realistic chance of overtaking them (0-100)
        - TIPS: 3 specific, location-aware energy-saving actions for a solar panel user to catch up. Each tip should:
            * Be actionable and practical
            * Consider current month weather, sunlight hours, tariff rates, and public holidays
            * Include estimated kWh impact

        DEFENSE ANALYSIS (to avoid being overtaken):
        - chaserIncrease: How much the chaser is likely to save this month
        - chaserMomentum: Chaser's growth rate (0-100, higher=bigger threat)
        - overtakeRisk: Chance of being overtaken if user doesn't act (0-100)
        - sustainabilityScore: User's consistency in energy saving (0-100)
        - TIPS: 3 defensive specific, location-aware sustainable energy-saving actions for a solar panel user. Each tip should:
            * Be actionable and practical
            * Consider current month weather, sunlight hours, tariff rates, and public holidays
            * Include estimated kWh impact

        OUTPUT JSON only, no markdown:
        {{
            "catchUp": {{
                "predicted_increase": float,
                "userTrend": float (-1 to 1),
                "competitorMomentum": int (0-100),
                "overtakeProbability": int (0-100),
                "tips": [
                    {{"action": string, "estimated_kwh": float, "priority": "high/medium/low"}},
                    {{"action": string, "estimated_kwh": float, "priority": "high/medium/low"}},
                    {{"action": string, "estimated_kwh": float, "priority": "high/medium/low"}}
                ]
            }},
            "defense": {{
                "chaserIncrease": float,
                "chaserMomentum": int (0-100),
                "overtakeRisk": int (0-100),
                "sustainabilityScore": int (0-100),
                "tips": [
                    {{"action": string, "estimated_kwh": float, "priority": "high/medium/low"}},
                    {{"action": string, "estimated_kwh": float, "priority": "high/medium/low"}},
                    {{"action": string, "estimated_kwh": float, "priority": "high/medium/low"}}
                ]
            }}
        }}"""

        USER_PROMPT = """Date: {current_date}

        USER DATA:
        - Current donation amount: {user_amount} kWh
        - Location: {user_district}, {user_state}
        - Recent average: {user_avg} kWh/donation
        - Total donations: {user_count}
        - Last donation: {user_last_date}

        COMPETITOR (User ahead to catch):
        - Their current donation amount: {comp_amount} kWh
        - Gap to close: {gap_up} kWh
        - Location: {comp_district}, {comp_state}
        - Their average: {comp_avg} kWh/donation
        - Total donations: {comp_count}
        - Status: {comp_status}

        CHASER (User behind trying to overtake you):
        - Their current donation amount: {chaser_amount} kWh
        - Your buffer: {gap_down} kWh
        - Location: {chaser_district}, {chaser_state}
        - Their average: {chaser_avg} kWh/donation
        - Total donations: {chaser_count}
        - Status: {chaser_status}

        {external_context}

        Generate prediction with SPECIFIC, ACTIONABLE tips based on Malaysian context and user locations."""

        return ChatPromptTemplate.from_messages(
            [("system", SYSTEM_PROMPT), ("user", USER_PROMPT)]
        )

    def _validate_research_agent(self) -> None:
        """Validate that research agent has required methods."""
        if not hasattr(self.research_agent, "get_energy_context"):
            print("WARNING: Research agent missing 'get_energy_context' method")
            print("  External context will be unavailable")
            self.enable_external_context = False
        else:
            print("Research agent validated")

    def get_user_context_batch(self, user_id: str) -> Dict[str, Any]:
        """Fetch user info + transaction stats and return clean JSON context."""

        if self.verbose:
            print(f"Fetching user context for user {user_id}...")

        # --- LLM SQL queries ---
        queries = [
            f"""
        Find the user information for user ID {user_id}.
        Return JSON with:
        - User_ID
        - Donate_Amount
        - State
        - District
        """,
            f"""
        Analyze the transaction history for user ID {user_id}.
        Return JSON with:
        - last_donation_date (latest Date_Time)
        - total_donations (count of Certificate_ID)
        - donation_averages (avg Donation_kwh)
        """,
        ]

        try:
            # ---- Execute queries ----
            user_result = self.sql_agent.query(queries[0])
            stats_result = self.sql_agent.query(queries[1])

            # ---- Extract dictionaries properly ----
            user_dict = safe_extract(user_result)
            stats_dict = safe_extract(stats_result)

            if self.verbose:
                print("DEBUG user_result =", user_result)
                print("DEBUG stats_result =", stats_result)
                print("EXTRACTED user_dict =", user_dict)
                print("EXTRACTED stats_dict =", stats_dict)

            # ---- Parse last donation date ----
            last_donation = stats_dict.get("last_donation_date")
            if isinstance(last_donation, str):
                try:
                    last_donation = datetime.fromisoformat(
                        last_donation.replace("Z", "+00:00")
                    )
                except Exception:
                    last_donation = None

            # ---- Final JSON ----
            context = {
                "User_ID": user_dict.get("User_ID") or user_id,
                "Donate_Amount": float(user_dict.get("Donate_Amount", 0.0)),
                "state": user_dict.get("State", "Selangor"),
                "district": user_dict.get("District", "Petaling"),
                "last_donation_date": (
                    last_donation.isoformat() if last_donation else None
                ),
                "total_donations": int(stats_dict.get("total_donations", 0)),
                "donation_averages": float(stats_dict.get("donation_averages", 0.0)),
            }

            if self.verbose:
                print(
                    f"User context: {context['Donate_Amount']} kWh ({context['district']}, {context['state']})"
                )
                print("Full context:", context)

            return context

        except Exception as e:
            if self.verbose:
                print("Error fetching user context:", e)

            # return default fallback
            return {
                "User_ID": user_id,
                "Donate_Amount": 0.0,
                "state": "Selangor",
                "district": "Petaling",
                "last_donation_date": None,
                "total_donations": 0,
                "donation_averages": 0.0,
            }

    def get_adjacent_users(self, user_donate_amount: float) -> Dict[str, Optional[str]]:
        """
        Find both the next higher-ranked user (competitor) AND the next lower-ranked user (chaser) based on Donate_Amount in user table.

        Returns:
            {
                "competitor_id": str or None,  # User above (to catch up to)
                "chaser_id": str or None        # User below (defending against)
            }
        """
        if self.verbose:
            print(f"** Finding adjacent users around {user_donate_amount} kWh...")

        # Find competitor (next higher rank)
        competitor_question = f"""
            From the user table, find the User_ID where Donate_Amount is greater than {user_donate_amount}.
            Order by Donate_Amount ascending and return only the first User_ID.
            If no such user exists, return the text: null
            
            Example SQL: SELECT "User_ID" FROM "user" WHERE "Donate_Amount" > {user_donate_amount} ORDER BY "Donate_Amount" ASC LIMIT 1
        """

        # Find chaser (next lower rank)
        chaser_question = f"""
            From the user table, find the User_ID where Donate_Amount is less than {user_donate_amount}.
            Order by Donate_Amount descending and return only the first User_ID.
            If no such user exists, return the text: null
            
            Example SQL: SELECT "User_ID" FROM "user" WHERE "Donate_Amount" < {user_donate_amount} ORDER BY "Donate_Amount" DESC LIMIT 1
        """

        try:
            results = self.sql_agent.batch_query([competitor_question, chaser_question])

            # Parse competitor result - handle both JSON and plain text
            competitor_answer = results[0]["answer"]
            competitor_id = self._parse_user_id_response(competitor_answer)

            # Parse chaser result - handle both JSON and plain text
            chaser_answer = results[1]["answer"]
            chaser_id = self._parse_user_id_response(chaser_answer)

            if self.verbose:
                comp_msg = (
                    f"User {competitor_id}" if competitor_id else "None (Top rank)"
                )
                chase_msg = f"User {chaser_id}" if chaser_id else "None (Bottom rank)"
                print(f"== Competitor: {comp_msg} | Chaser: {chase_msg}")

            return {"competitor_id": competitor_id, "chaser_id": chaser_id}

        except Exception as e:
            if self.verbose:
                print(f"Error finding adjacent users: {str(e)}")
            return {"competitor_id": None, "chaser_id": None}

    def _parse_user_id_response(self, answer: Any) -> Optional[str]:
        """Parse User_ID from SQL agent response, handling various formats."""
        if not answer:
            return None

        # Handle string response
        if isinstance(answer, str):
            answer = answer.strip()

            # Check for explicit null
            if answer.lower() in ["null", "none", ""]:
                return None

            # Try parsing as JSON
            try:
                data = json.loads(answer)
                return self._extract_user_id(data)
            except (json.JSONDecodeError, TypeError):
                # Not JSON, treat as plain text user ID
                if answer.isdigit():
                    return str(answer)
                return None

        # Handle direct dict/list response
        return self._extract_user_id(answer)

    def _extract_user_id(self, data: Any) -> Optional[str]:
        """Extract User_ID from various data formats."""
        if isinstance(data, list):
            if data:
                first_item = data[0]
                if isinstance(first_item, dict):
                    user_id = first_item.get("User_ID")
                else:
                    user_id = first_item
            else:
                return None
        elif isinstance(data, dict):
            user_id = data.get("User_ID")
        else:
            user_id = data

        if not user_id or user_id == "null" or user_id == "None":
            return None

        return str(user_id)

    @lru_cache(maxsize=128)
    def get_external_context_cached(self, state: str, district: str) -> str:
        """Cached external context - prevents redundant API calls."""
        if not self.enable_external_context:
            return ""

        if self.verbose:
            print(f"** Fetching external context for {district}, {state}")

        try:
            result = self.research_agent.get_energy_context(state, district)
            context = result.get("answer", "No external context available")

            if self.verbose:
                print(f"External context retrieved\n")

            return context
        except Exception as e:
            if self.verbose:
                print(f"Warning: Could not fetch external context: {str(e)}\n")
            return f"External context unavailable for {district}, {state}"

    def validate_and_sanitize_prediction(
        self, ai_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate bidirectional prediction output with concrete metrics."""

        # Extract catch-up metrics
        catchup = ai_result.get("catchUp", {})
        validated_catchup = {
            "predicted_increase": float(catchup.get("predicted_increase", 0)),
            "userTrend": max(-1.0, min(1.0, float(catchup.get("userTrend", 0)))),
            "competitorMomentum": max(
                self.MIN_PROBABILITY,
                min(self.MAX_PROBABILITY, int(catchup.get("competitorMomentum", 50))),
            ),
            "overtakeProbability": max(
                self.MIN_PROBABILITY,
                min(self.MAX_PROBABILITY, int(catchup.get("overtakeProbability", 50))),
            ),
            "tips": [],
        }

        # Extract defense metrics
        defense = ai_result.get("defense", {})
        validated_defense = {
            "chaserIncrease": float(defense.get("chaserIncrease", 0)),
            "chaserMomentum": max(
                self.MIN_PROBABILITY,
                min(self.MAX_PROBABILITY, int(defense.get("chaserMomentum", 50))),
            ),
            "overtakeRisk": max(
                self.MIN_PROBABILITY,
                min(self.MAX_PROBABILITY, int(defense.get("overtakeRisk", 50))),
            ),
            "sustainabilityScore": max(
                self.MIN_PROBABILITY,
                min(self.MAX_PROBABILITY, int(defense.get("sustainabilityScore", 50))),
            ),
            "tips": [],
        }

        # Process catch-up tips (with estimated kWh)
        raw_catchup_tips = catchup.get("tips", [])
        for tip in raw_catchup_tips[:3]:
            if isinstance(tip, dict):
                validated_catchup["tips"].append(
                    {
                        "action": str(tip.get("action", "")),
                        "estimated_kwh": float(tip.get("estimated_kwh", 0)),
                        "priority": str(tip.get("priority", "medium")),
                    }
                )
            else:
                validated_catchup["tips"].append(
                    {"action": str(tip), "estimated_kwh": 5.0, "priority": "medium"}
                )

        # Default catch-up tips
        default_catchup_tips = [
            {
                "action": "Replace 5 regular bulbs with LED bulbs (saves ~75W each)",
                "estimated_kwh": 10.0,
                "priority": "high",
            },
            {
                "action": "Set air conditioner to 24°C instead of 20°C, use timer for 6 hours at night",
                "estimated_kwh": 15.0,
                "priority": "high",
            },
            {
                "action": "Unplug phone chargers, TV, and router when not in use (vampire power)",
                "estimated_kwh": 8.0,
                "priority": "medium",
            },
        ]

        while len(validated_catchup["tips"]) < 3:
            validated_catchup["tips"].append(
                default_catchup_tips[len(validated_catchup["tips"])]
            )

        # Process defense tips
        raw_defense_tips = defense.get("tips", [])
        for tip in raw_defense_tips[:3]:
            if isinstance(tip, dict):
                validated_defense["tips"].append(
                    {
                        "action": str(tip.get("action", "")),
                        "estimated_kwh": float(tip.get("estimated_kwh", 0)),
                        "priority": str(tip.get("priority", "medium")),
                    }
                )
            else:
                validated_defense["tips"].append(
                    {"action": str(tip), "estimated_kwh": 5.0, "priority": "medium"}
                )

        # Default defense tips
        default_defense_tips = [
            {
                "action": "Maintain your LED bulb usage and keep them on schedule (6-8 hours/day max)",
                "estimated_kwh": 12.0,
                "priority": "high",
            },
            {
                "action": "Continue optimal air conditioning habits: 24°C, clean filters monthly",
                "estimated_kwh": 18.0,
                "priority": "high",
            },
            {
                "action": "Run washing machine and dishwasher only with full loads (2-3 times/week)",
                "estimated_kwh": 10.0,
                "priority": "medium",
            },
        ]

        while len(validated_defense["tips"]) < 3:
            validated_defense["tips"].append(
                default_defense_tips[len(validated_defense["tips"])]
            )

        return {"catchUp": validated_catchup, "defense": validated_defense}

    def _generate_prediction_internal(self, user_id: str) -> Dict[str, Any]:
        """Internal method that generates bidirectional prediction."""
        self._update_status(f"Starting prediction for user {user_id}", 0)

        if self.verbose:
            print(f"\n** Generating BIDIRECTIONAL prediction for user {user_id}...")

        # Get user context
        self._update_status("Fetching user information...", 10)
        user_ctx = self.get_user_context_batch(user_id)
        user_total = user_ctx["Donate_Amount"]

        # Find both adjacent users
        self._update_status("Finding competitors and chasers...", 25)
        adjacent = self.get_adjacent_users(user_total)
        competitor_id = adjacent["competitor_id"]
        chaser_id = adjacent["chaser_id"]

        is_top_ranked = competitor_id is None
        is_bottom_ranked = chaser_id is None

        # Get competitor context (offensive target)
        self._update_status("Analyzing competitor data...", 40)
        if competitor_id:
            comp_ctx = self.get_user_context_batch(competitor_id)
        else:
            # Top ranked - set aspirational target
            is_top_ranked = True
            comp_ctx = user_ctx.copy()
            comp_ctx["User_ID"] = f"{user_ctx['User_ID']}_target"
            comp_ctx["Donate_Amount"] = user_total + 50
            if self.verbose:
                print(
                    f"User is TOP RANKED! Aspirational target: {comp_ctx['Donate_Amount']} kWh"
                )

        # Get chaser context (defensive monitoring)
        self._update_status("Analyzing chaser data...", 50)
        if chaser_id:
            chaser_ctx = self.get_user_context_batch(chaser_id)
        else:
            # Bottom ranked - minimal defensive concern
            is_bottom_ranked = True
            chaser_ctx = user_ctx.copy()
            chaser_ctx["User_ID"] = f"{user_ctx['User_ID']}_chaser"
            chaser_ctx["Donate_Amount"] = max(0, user_total - 20)
            if self.verbose:
                print(f"User is bottom ranked - minimal defensive pressure")

        comp_total = comp_ctx["Donate_Amount"]
        chaser_total = chaser_ctx["Donate_Amount"]

        # Calculate concrete gaps
        gap_up = round(comp_total - user_total, 2)
        gap_down = round(user_total - chaser_total, 2)

        # Fetch external contexts if enabled
        external_text = ""
        if self.enable_external_context:
            self._update_status("Fetching location-based energy insights...", 60)

            if self.verbose:
                print("** Fetching location-based energy contexts...")

            try:
                with ThreadPoolExecutor(max_workers=3) as executor:
                    user_future = executor.submit(
                        self.get_external_context_cached,
                        user_ctx["state"],
                        user_ctx["district"],
                    )
                    comp_future = executor.submit(
                        self.get_external_context_cached,
                        comp_ctx["state"],
                        comp_ctx["district"],
                    )
                    chaser_future = executor.submit(
                        self.get_external_context_cached,
                        chaser_ctx["state"],
                        chaser_ctx["district"],
                    )

                    user_ext = user_future.result(timeout=30)
                    comp_ext = comp_future.result(timeout=30)
                    chaser_ext = chaser_future.result(timeout=30)

                    if user_ext or comp_ext or chaser_ext:
                        external_text = f"""
                            Your Location ({user_ctx['district']}, {user_ctx['state']}):
                            {user_ext}

                            Competitor Location ({comp_ctx['district']}, {comp_ctx['state']}):
                            {comp_ext}

                            Chaser Location ({chaser_ctx['district']}, {chaser_ctx['state']}):
                            {chaser_ext}

                            Use these insights to provide location-aware, culturally relevant tips for Malaysian users."""

                        if self.verbose:
                            print(f"Location-based contexts fetched\n")

            except Exception as e:
                if self.verbose:
                    print(f"Error fetching external contexts: {str(e)}\n")
                external_text = ""
        else:
            external_text = "External context disabled - provide general Malaysian energy-saving tips"

        # Prepare AI input with concrete, structured data
        self._update_status("Preparing prediction model...", 75)
        model_input = {
            "current_date": date.today().strftime("%B %d, %Y"),
            "user_amount": user_ctx["Donate_Amount"],
            "user_district": user_ctx["district"],
            "user_state": user_ctx["state"],
            "user_avg": user_ctx["donation_averages"],
            "user_count": user_ctx["total_donations"],
            "user_last_date": user_ctx.get("last_donation_date", "N/A"),
            "comp_amount": comp_ctx["Donate_Amount"],
            "gap_up": gap_up,
            "comp_district": comp_ctx["district"],
            "comp_state": comp_ctx["state"],
            "comp_avg": comp_ctx["donation_averages"],
            "comp_count": comp_ctx["total_donations"],
            "comp_status": (
                "Aspirational target (you're #1!)"
                if is_top_ranked
                else "Next rank to achieve"
            ),
            "chaser_amount": chaser_ctx["Donate_Amount"],
            "gap_down": gap_down,
            "chaser_district": chaser_ctx["district"],
            "chaser_state": chaser_ctx["state"],
            "chaser_avg": chaser_ctx["donation_averages"],
            "chaser_count": chaser_ctx["total_donations"],
            "chaser_status": (
                "No immediate threat (bottom rank)"
                if is_bottom_ranked
                else "Actively chasing you"
            ),
            "external_context": external_text,
        }

        # Generate AI prediction
        self._update_status("Generating personalized recommendations...", 85)
        if self.verbose:
            print(f"Generating AI prediction with location-aware tips...")

        ai_result = self.prediction_chain.invoke(model_input)
        validated = self.validate_and_sanitize_prediction(ai_result)

        # Calculate catch-up metrics (to overtake competitor)
        self._update_status("Calculating strategies...", 95)
        if is_top_ranked:
            min_required = round(gap_up + 5, 2)
            max_needed = round(
                gap_up + validated["catchUp"]["predicted_increase"] + 10, 2
            )
            overtake_prob = 100  # Already at top
        else:
            # Need to close the gap + safety margin
            min_required = round(gap_up + 5, 2)  # Minimum to overtake
            max_needed = round(
                gap_up + validated["catchUp"]["predicted_increase"] + 10, 2
            )
            overtake_prob = validated["catchUp"]["overtakeProbability"]

        # Calculate defense metrics (to avoid being overtaken)
        if is_bottom_ranked:
            # No one below, minimal defensive concern
            buffer_recommended = round(gap_down * 0.3, 2)
            overtake_risk = 5  # Very low risk
        else:
            # Recommend buffer to stay safe
            buffer_recommended = round(gap_down * 0.6, 2)
            overtake_risk = validated["defense"]["overtakeRisk"]

        # Build comprehensive response
        response = {
            # === CATCH-UP STRATEGY (to overtake competitor) ===
            "catchUp": {
                "currentGap": gap_up,
                "minRequired": min_required,
                "maxNeeded": max_needed,
                "userTrend": validated["catchUp"]["userTrend"],
                "competitorMomentum": validated["catchUp"]["competitorMomentum"],
                "overtakeProbability": overtake_prob,
                "tips": validated["catchUp"]["tips"],
                "summary": self._generate_catchup_summary(
                    gap_up, min_required, overtake_prob, is_top_ranked
                ),
            },
            # === DEFENSE STRATEGY (to avoid being overtaken) ===
            "defense": {
                "currentBuffer": gap_down,
                "bufferRecommended": buffer_recommended,
                "chaserMomentum": validated["defense"]["chaserMomentum"],
                "overtakeRisk": overtake_risk,
                "sustainabilityScore": validated["defense"]["sustainabilityScore"],
                "tips": validated["defense"]["tips"],
                "summary": self._generate_defense_summary(
                    gap_down, overtake_risk, is_bottom_ranked
                ),
            },
            # === POSITION CONTEXT ===
            "position": {
                "isTopRanked": is_top_ranked,
                "isBottomRanked": is_bottom_ranked,
                "hasCompetitor": competitor_id is not None,
                "hasChaser": chaser_id is not None,
            },
        }

        self._update_status("Prediction complete!", 100)

        if self.verbose:
            print(f"PREDICTION COMPLETE!")
            print(
                f"Catch-up: Need {min_required}-{max_needed} kWh to overtake (gap: {gap_up} kWh)"
            )
            print(
                f"Defense: Keep {buffer_recommended} kWh buffer (current: {gap_down} kWh)"
            )

        return response

    def _generate_catchup_summary(
        self, gap: float, min_required: float, probability: int, is_top: bool
    ) -> str:
        """Generate human-readable catch-up summary."""
        if is_top:
            return "You're #1! Keep your lead by saving additional energy to build a stronger buffer."
        elif gap < 10:
            return "So close! You're just slightly behind. Saving a bit more will help you overtake with a strong chance."
        elif gap < 30:
            return "Within reach! The gap is manageable. Stay consistent this month to increase your overtake chances."
        else:
            return "A challenge ahead. Focus on steady savings to improve your position and increase your chances."

    def _generate_defense_summary(
        self, buffer: float, risk: int, is_bottom: bool
    ) -> str:
        """Generate human-readable defense summary."""
        if is_bottom:
            return "You're building momentum! No one is chasing you yet, so keep growing your savings."
        elif buffer < 5:
            return "Alert! Your lead is narrow. Take defensive action to stay ahead."
        elif buffer < 15:
            return "Moderate lead. Maintain consistent habits to stay safe."
        else:
            return "Strong position. Keep up your great habits to maintain your lead."

    def predict_savings(
        self, user_id: str, force_refresh: bool = False, callback=None
    ) -> Dict[str, Any]:
        """
        Generate bidirectional prediction with caching and deduplication.

        """
        # Set active callback for this request
        self.status_callback = callback

        try:
            # Check cache first (unless force_refresh)
            if not force_refresh:
                cached_result = self.prediction_cache.get(user_id)
                if cached_result is not None:
                    if self.verbose:
                        print(f" Using cached prediction for user {user_id}")
                    # Send completion status for cached results
                    if self.status_callback:
                        self.status_callback(
                            {
                                "message": "Loaded from cache",
                                "progress": 100,
                                "timestamp": time.time(),
                            }
                        )
                    return cached_result

            # Check if prediction is already in progress
            if user_id in self.in_flight:
                if self.verbose:
                    print(f"Waiting for in-flight prediction for user {user_id}...")
                start_wait = time.time()
                while user_id in self.in_flight and (time.time() - start_wait) < 30:
                    time.sleep(0.1)

                cached_result = self.prediction_cache.get(user_id)
                if cached_result is not None:
                    if self.verbose:
                        print(f"In-flight prediction completed, using result")
                    return cached_result

            # Mark this prediction as in-flight
            self.in_flight[user_id] = time.time()

            try:
                # Generate new prediction
                result = self._generate_prediction_internal(user_id)

                # Cache the result
                self.prediction_cache.set(user_id, result)

                return result

            finally:
                # Remove from in-flight tracking
                if user_id in self.in_flight:
                    del self.in_flight[user_id]

        except Exception as e:
            # Clean up in-flight tracking on error
            if user_id in self.in_flight:
                del self.in_flight[user_id]

            if self.verbose:
                print(f"Error: {str(e)}")
            raise

        finally:
            # Clear active callback when done
            self.status_callback = None


def create_prediction_agent_from_env(
    sql_agent,
    research_agent,
    verbose: bool = True,
    enable_external_context: bool = True,
    cache_ttl: int = 300,
    status_callback=None,
    **kwargs,
) -> BidirectionalEnergyPredictionAgent:
    """
    Create bidirectional prediction agent with offensive and defensive strategies.

    """
    load_dotenv()

    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    api_token = os.environ.get("CF_AI_API_TOKEN")

    if not account_id or not api_token:
        raise ValueError("Missing Cloudflare credentials")

    return BidirectionalEnergyPredictionAgent(
        sql_agent=sql_agent,
        research_agent=research_agent,
        account_id=account_id,
        api_token=api_token,
        verbose=verbose,
        enable_external_context=enable_external_context,
        cache_ttl=cache_ttl,
        status_callback=status_callback,
        **kwargs,
    )


def safe_extract(result: Union[Dict[str, Any], str], default_user_id: str = None) -> Dict[str, Any]:
    """
    Safely extract data from SQL agent result.

    Handles:
    - JSON/dict strings
    - tuple-wrapped dicts
    - scalar values (like Donate_Amount)
    - multiline stats (last_donation \n total \n avg)
    - 'null' or empty strings

    Returns a dictionary.
    """
    # If input is dict, get 'answer' or 'raw_results'
    if isinstance(result, dict):
        data = result.get("answer") or result.get("raw_results") or ""
    else:
        data = str(result)

    data = data.strip()

    if not data or data.lower() == "null":
        return {}

    # Handle tuple-wrapped dict in string form: "[({...},)]"
    if data.startswith("[") and data.endswith("]"):
        try:
            parsed = literal_eval(data)
            if isinstance(parsed, list) and len(parsed) > 0:
                first = parsed[0]
                if isinstance(first, tuple) and len(first) > 0 and isinstance(first[0], dict):
                    return first[0]
                elif isinstance(first, dict):
                    return first
        except:
            pass

    # Try single-line dict / JSON
    if data.startswith("{") and data.endswith("}"):
        try:
            return literal_eval(data)
        except:
            try:
                return json.loads(data)
            except:
                pass

    # Multiline stats: last_donation \n total \n avg
    lines = data.split("\n")
    if len(lines) == 3:
        try:
            return {
                "last_donation_date": lines[0].strip(),
                "total_donations": int(lines[1].strip()),
                "donation_averages": float(lines[2].strip()),
            }
        except:
            pass

    # Scalar numeric (like Donate_Amount)
    try:
        return {"Donate_Amount": float(data), "User_ID": default_user_id}
    except:
        pass

    return {}
