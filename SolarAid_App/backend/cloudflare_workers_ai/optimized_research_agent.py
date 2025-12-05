import os
from typing import Optional, List, Dict, Any
from datetime import date
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

from langchain_cloudflare import ChatCloudflareWorkersAI
from langchain_tavily import TavilySearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class OptimizedResearchAgent:
    """
    Reusable Research Agent for (search data through online => analysis)
        - Executed using Cloudflare Workers AI + Tavily Search API.

    """

    def __init__(
        self,
        tavily_api_key: str,
        account_id: str,
        api_token: str,
        model: str = "@cf/meta/llama-3.1-8b-instruct",
        system_prompt: Optional[str] = None,
        max_search_results: int = 3,
        search_depth: str = "basic",
        temperature: float = 0.1,
        max_tokens: int = 500,
        verbose: bool = True,
        enable_caching: bool = True,
        cache_ttl_seconds: int = 3600,
    ):
        self.verbose = verbose
        self.enable_caching = enable_caching
        self.cache_ttl_seconds = cache_ttl_seconds

        # Simple in-memory cache
        self._search_cache = {}
        self._cache_timestamps = {}

        if not tavily_api_key:
            raise ValueError("Tavily API key is required")
        if not account_id or not api_token:
            raise ValueError("Cloudflare credentials missing")

        # Setup LLM
        self.llm = ChatCloudflareWorkersAI(
            model=model,
            cloudflare_account_id=account_id,
            cloudflare_api_token=api_token,
            temperature=temperature,
            max_tokens=max_tokens,
            model_kwargs={"streaming": False},
        )

        self.search_tool = TavilySearch(
            api_key=tavily_api_key,
            max_results=max_search_results,
            topic="general",
            search_depth=search_depth,
        )

        # Prompts
        self.system_prompt = system_prompt or self.default_system_prompt()
        self.synthesis_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                (
                    "user",
                    "Question: {question}\n\nSearch Results:\n{search_results}\n\nProvide a clear, structured answer.",
                ),
            ]
        )
        self.synthesis_chain = self.synthesis_prompt | self.llm | StrOutputParser()

        if verbose:
            print("\nResearch Agent initialized")
            print(f"    Model: {model}")
            print(f"    Max results: {max_search_results}")
            print(f"    Caching: {enable_caching}")
            print("----------------------------------\n")

    def default_system_prompt(self) -> str:
        return (
            "You are a concise research assistant. Extract the clearest insights "
            "from search results. Keep answers <200 words. If info missing, say so."
        )

    # ------------------------------------------------------------
    #                     CACHE LOGIC
    # ------------------------------------------------------------
    def _cache_valid(self, key: str) -> bool:
        """Check if cache exists & within TTL."""
        if not self.enable_caching or key not in self._cache_timestamps:
            return False

        import time

        return time.time() - self._cache_timestamps[key] < self.cache_ttl_seconds

    def _cache_get(self, key: str):
        if self._cache_valid(key):
            if self.verbose:
                print(f"Using cached result for: {key}")
            return self._search_cache[key]
        return None

    def _cache_set(self, key: str, value):
        if self.enable_caching:
            import time

            self._search_cache[key] = value
            self._cache_timestamps[key] = time.time()

    # ------------------------------------------------------------
    #                     SEARCH LOGIC
    # ------------------------------------------------------------

    def format_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        formatted = []
        for i, r in enumerate(results, 1):
            formatted.append(
                {
                    "title": r.get("title", "No title"),
                    "url": r.get("url", ""),
                    "snippet": r.get("results", r.get("content", ""))[:300],
                }
            )
        return formatted

    def search_once(self, query: str):
        cache_key = f"search:{query}"

        cached = self._cache_get(cache_key)
        if cached:
            return cached

        if self.verbose:
            print(f"Searching: {query}")

        try:
            resp = self.search_tool.invoke({"query": query})
            results = resp.get("results", [])

            if self.verbose:
                if len(results) == 0:
                    print("   No results found")
                    print()
                else:
                    for i, r in enumerate(results):
                        print(f"   Result {i+1}:")
                        print(f"      Title: {r.get('title')}")
                        print(f"      URL: {r.get('url')}")
                        print(f"      Content (first 500 chars):")
                        print(f"      {r.get('content', '')[:500]}")
                        print()

        except Exception as e:
            if self.verbose:
                print("Search failed:", e)
            results = []

        self._cache_set(cache_key, results)
        return results

    def research(self, questions: str):
        """Core logic: run multiple queries and merge results."""
        if isinstance(questions, str):
            questions = [questions]

        all_results = []

        for question in questions:
            if self.verbose:
                print(f"\n{'='*70}")
                print(f"Question: {question}")
                print(f"{'='*70}\n")

            results = self.search_once(question)
            formatted = self.format_results(results)
            all_results.extend(formatted)

        combined_answer = self.synthesis_chain.invoke(
            {"question": " | ".join(questions), "search_results": all_results}
        )

        return {"answer": combined_answer, "search_results": all_results}


# ============================================================
#        MALAYSIAN ENERGY SPECIALIZATION (for our app only)
# ============================================================


class OptimizedMalaysianEnergyAgent(OptimizedResearchAgent):

    ENERGY_PROMPT = (
        "You are a Malaysian energy research assistant.\n\n"
        "Structure the answer:\n"
        "- WEATHER: Impact on electricity\n"
        "- HOLIDAYS: Upcoming high-demand periods\n"
        "- KEY INSIGHT: Forecast takeaway\n\n"
        "Keep under 200 words. Be precise and practical."
    )

    def __init__(self, tavily_api_key, account_id, api_token, **kwargs):
        super().__init__(
            tavily_api_key,
            account_id,
            api_token,
            system_prompt=self.ENERGY_PROMPT,
            max_search_results=3,
            search_depth="basic",
            max_tokens=350,
            **kwargs,
        )

    def get_energy_context(self, state: str, district: str):
        """Get multiple relevant energy-related questions and run research."""
        today = date.today()
        current_month = today.strftime("%B %Y")

        # List of sub-queries
        questions = [
            f"{district} {state} Malaysia weather forecast {current_month}",
            f"Malaysia public holidays {current_month}",
        ]

        # Run research for all these questions
        return self.research(questions)


def create_energy_agent_from_env(verbose=True, **kwargs):
    load_dotenv()
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    api_token = os.getenv("CF_AI_API_TOKEN") or os.getenv("CLOUDFLARE_API_TOKEN")

    if not tavily_api_key:
        raise ValueError("Missing TAVILY_API_KEY")
    if not account_id:
        raise ValueError("Missing CLOUDFLARE_ACCOUNT_ID")
    if not api_token:
        raise ValueError("Missing CF_AI_API_TOKEN or CLOUDFLARE_API_TOKEN")

    return OptimizedMalaysianEnergyAgent(
        tavily_api_key=tavily_api_key,
        account_id=account_id,
        api_token=api_token,
        verbose=verbose,
        **kwargs,
    )


# --- Example Usage For Testing Purposes ---
if __name__ == "__main__":
    agent = create_energy_agent_from_env(verbose=True)

    print("\n[TEST] Searching Selangor -> Petaling")
    res = agent.get_energy_context("Selangor", "Petaling")
    print("Answer:\n", res["answer"])
