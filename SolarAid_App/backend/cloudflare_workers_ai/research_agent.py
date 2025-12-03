import os
from typing import Optional, List, Dict, Any
from datetime import date
from dotenv import load_dotenv

from langchain_cloudflare import ChatCloudflareWorkersAI
from langchain_tavily import TavilySearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class CloudflareResearchAgent:
    """
    Reusable Research Agent with query decomposition:
        1. Break complex questions into simple sub-queries
        2. Search each sub-query separately
        3. Synthesize all results into final answer
        - Executed using Cloudflare Workers AI + Tavily Search API.

    """
    
    def __init__(
        self,
        tavily_api_key: str,
        account_id: str,
        api_token: str,
        model: str = "@cf/meta/llama-3.1-8b-instruct",
        system_prompt: Optional[str] = None,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        max_search_results: int = 3,
        search_depth: str = "advanced",
        temperature: float = 0.1,
        max_tokens: int = 800,
        verbose: bool = True
    ):
        """
        Initialize the Research Agent.
        
        """
        self.verbose = verbose
        self.tavily_api_key = tavily_api_key
        self.model_name = model
        
        if not tavily_api_key:
            raise ValueError("Tavily API key is required")
        if not account_id or not api_token:
            raise ValueError("Cloudflare account_id and api_token are required")
        
        self.llm = self.create_llm(model, account_id, api_token, temperature, max_tokens)
        self.search_tool = self.create_search_tool(
            tavily_api_key,
            max_search_results,
            search_depth,
            include_domains,
            exclude_domains
        )
        self.system_prompt = system_prompt or self.default_system_prompt()
        self.decomposition_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a query decomposition expert. Break down the question into EXACTLY 3 simple search queries.

            CRITICAL RULES:
            1. Generate EXACTLY 3 queries - NO MORE, NO LESS
            2. Each query must be 4-8 words
            3. NO colons, NO bullets, NO numbering, NO labels
            4. Return ONLY the search queries, one per line
            5. Skip any category headers or section names

            BAD Example (DO NOT DO THIS):
            Weather patterns:
            Petaling temperature trends
            Electricity tariffs:
            Current rates

            GOOD Example:
            Selangor Malaysia weather forecast December
            Malaysia residential electricity tariff 2025
            Malaysia public holidays December 2025

            Remember: EXACTLY 3 queries, plain text only!"""),
            ("user", "{question}")
        ])
        
        self.synthesis_prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("user", """Original Question: {question}

            Search Results from Multiple Queries:
            {all_results}

            Based on ALL the search results above, provide a comprehensive answer to the original question. 
            Synthesize information from all sources and cite them when relevant.""")
        ])
        
        self.decomposition_chain = self.decomposition_prompt | self.llm | StrOutputParser()
        self.synthesis_chain = self.synthesis_prompt | self.llm | StrOutputParser()
        
        if self.verbose:
            print(f"Research Agent initialized")
            print(f"    Model: {model}")
            print(f"    Search depth: {search_depth}")
            print(f"    Max results: {max_search_results}")
            if include_domains:
                print(f"    Allowed domains: {len(include_domains)} domains")
            print()
    
    def create_llm(
        self,
        model: str,
        account_id: str,
        api_token: str,
        temperature: float,
        max_tokens: int
    ):
        """
        Create Cloudflare LLM instance.
        
        """
        return ChatCloudflareWorkersAI(
            model=model,
            cloudflare_account_id=account_id,
            cloudflare_api_token=api_token,
            temperature=temperature,
            max_tokens=max_tokens,
            model_kwargs={"streaming": False}
        )
    
    def create_search_tool(
        self,
        api_key: str,
        max_results: int,
        search_depth: str,
        include_domains: Optional[List[str]],
        exclude_domains: Optional[List[str]]
    ):
        """
        Create Tavily search tool.
        
        """
        kwargs = {
            "api_key": api_key,
            "max_results": max_results,
            "topic": "general",
            "search_depth": search_depth,
        }
        
        if include_domains:
            kwargs["include_domains"] = include_domains
        if exclude_domains:
            kwargs["exclude_domains"] = exclude_domains
        
        return TavilySearch(**kwargs)
    
    def default_system_prompt(self) -> str:
        """Default system prompt."""
        return """You are a helpful research assistant that synthesizes information from multiple sources.

        When answering questions:
        1. Analyze all provided search results carefully
        2. Synthesize information from multiple sources
        3. Provide factual, well-researched answers
        4. Cite sources when possible
        5. Keep responses clear and concise
        6. If information is conflicting, mention it
        7. If you cannot find information, say so clearly"""
    
    def format_search_results(self, results, query: str) -> str:
        """
        Format search results for LLM consumption.
        
        """
        if isinstance(results, str):
            return f"Query: {query}\n{results}\n"
        
        if isinstance(results, list):
            formatted = [f"Query: {query}\n"]
            for i, result in enumerate(results, 1):
                if isinstance(result, dict):
                    title = result.get('title', 'No title')
                    content = result.get('content', result.get('snippet', 'No content'))
                    url = result.get('url', 'No URL')
                    formatted.append(f"  [{i}] {title}\n      Source: {url}\n      Content: {content}\n")
                else:
                    formatted.append(f"  [{i}] {result}\n")
            return "".join(formatted) + "\n"
        
        return f"Query: {query}\n{str(results)}\n"
    
    def decompose_question(self, question: str) -> List[str]:
        """
        Break down complex question into simple search queries.
        
        """
        if self.verbose:
            print("Decomposing question into search queries...")
        
        try:
            response = self.decomposition_chain.invoke({"question": question})
            
            # Split by newlines and clean up
            queries = []
            for line in response.strip().split('\n'):
                line = line.strip()
                # Skip empty lines, lines with colons (headers), numbered lines
                if not line:
                    continue
                if ':' in line:
                    continue
                if line[0].isdigit() and line[1] in '.):':
                    continue
                # Skip obvious header words
                if line.lower() in ['weather', 'tariffs', 'holidays', 'weather patterns', 'electricity tariffs', 'holiday schedule']:
                    continue
                
                queries.append(line)
            
            # Force exactly 3 queries
            if len(queries) > 3:
                queries = queries[:3]
            elif len(queries) < 3:
                # If less than 3, use the original question
                if self.verbose:
                    print("Less than 3 queries generated, using original question")
                queries = [question]
            
            # Display the queries
            if self.verbose:
                print(f"Using {len(queries)} search queries:")
                for i, q in enumerate(queries, 1):
                    print(f"   {i}. {q}")
                print()
            
            return queries
            
        except Exception as e:
            if self.verbose:
                print(f"Decomposition failed: {e}")
                print("Falling back to original question")
            return [question]
    
    def search_single_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute a single search query.
        
        """
        try:
            search_results = self.search_tool.invoke({"query": query})
            
            if isinstance(search_results, dict) and "results" in search_results:
                results = search_results["results"]
            else:
                results = []
            
            # Fallback to global search if no results and we have domain restrictions
            if len(results) == 0 and hasattr(self.search_tool, 'include_domains') and self.search_tool.include_domains:
                if self.verbose:
                    print(f"No authority results, trying global search...")
                
                # Create new TavilySearch without domain restrictions
                fallback_search = TavilySearch(
                    api_key=self.tavily_api_key,
                    max_results=self.search_tool.max_results,
                    search_depth=self.search_tool.search_depth,
                    topic="general"
                )
                
                fallback_results = fallback_search.invoke({"query": query})
                results = fallback_results.get("results", [])
            
            return results
            
        except Exception as e:
            if self.verbose:
                print(f"Search failed: {e}")
            return []
    
    def research(self, question: str) -> Dict[str, Any]:
        """
        Main research method with query decomposition.
        
        """
        if self.verbose:
            print(f"\n{'='*70}")
            print(f"Question: {question}")
            print(f"{'='*70}\n")
        
        try:
            # Step 1: Decompose the question
            sub_queries = self.decompose_question(question)
            
            # Step 2: Search each sub-query
            all_results = []
            for i, query in enumerate(sub_queries, 1):
                if self.verbose:
                    print(f"Searching query {i}/{len(sub_queries)}: '{query}'")
                
                results = self.search_single_query(query)
                
                if self.verbose:
                    print(f"   ✓ Found {len(results)} results")
                    for items in results:
                        if isinstance(items, dict):
                            title = items.get('title', 'No title')
                            url = items.get('url', 'No URL')
                            print(f"      - {title} ({url})")
                        else:
                            print(f"      - {str(items)[:60]}...")
                
                    print("\n")
                    
                all_results.append({
                    "query": query,
                    "results": results
                })
            
            # Step 3: Format all results for synthesis
            formatted_all = []
            for item in all_results:
                formatted_all.append(
                    self.format_search_results(item["results"], item["query"])
                )
            
            combined_results = "\n".join(formatted_all)
            
            # Step 4: Synthesize final answer
            if self.verbose:
                print("Synthesizing final answer from all search results...\n")
            
            final_answer = self.synthesis_chain.invoke({
                "question": question,
                "all_results": combined_results
            })
            
            if self.verbose:
                print(f"\n{'='*70}")
                print("FINAL ANSWER")
                print(f"{'='*70}")
                print(final_answer)
                print(f"{'='*70}\n")
            
            return {
                "answer": final_answer,
                "sub_queries": sub_queries,
                "search_results": all_results
            }
            
        except Exception as e:
            error_msg = str(e)
            if self.verbose:
                print(f"Error: {error_msg}")
            
            return {
                "answer": f"Encountered an error: {error_msg}",
                "error": error_msg
            }
    
    def batch_research(self, questions: List[str]) -> List[Dict[str, Any]]:
        """
        Research multiple questions in batch.
        
        """
        results = []
        for i, question in enumerate(questions, 1):
            if self.verbose:
                print(f"\n{'='*70}")
                print(f"[Question {i}/{len(questions)}]")
                print(f"{'='*70}")
            results.append(self.research(question))
        return results



class MalaysianEnergyAgent(CloudflareResearchAgent):
    """
    Specialized agent for Malaysian energy research.
    
    """
    # Malaysian authority domains
    AUTHORITY_DOMAINS = [
        "met.gov.my",      # Malaysian Meteorological Department
        "st.gov.my",       # Suruhanjaya Tenaga (Energy Commission)
        "tnb.com.my",      # Tenaga Nasional Berhad
        "seda.gov.my",     # Sustainable Energy Development Authority
        "ketsa.gov.my",    # Ministry of Energy Transition
        "epu.gov.my",      # Economic Planning Unit
    ]
    
    ENERGY_SYSTEM_PROMPT = """You are a Malaysian energy research assistant specialized in electricity consumption analysis.

    When synthesizing energy research:
    1. Prioritize official Malaysian government and utility data
    2. Focus on quantified, actionable insights for forecasting
    3. Identify top 1-3 most influential factors per category
    4. Provide specific numbers, percentages, and dates when available
    5. Ignore data older than 3 years unless comparing long-term trends
    6. Keep responses concise and structured
    7. Flag any conflicting information from different sources
    8. If data is missing or unavailable, state this clearly

    Structure your answer clearly with PAST TRENDS, CURRENT CONTEXT, and FUTURE IMPACTS for each factor (weather, tariffs, holidays)."""
    
    def __init__(
        self,
        tavily_api_key: str,
        account_id: str,
        api_token: str,
        **kwargs
    ):
        """
        Initialize Malaysian Energy Agent with preset domains and prompt.
        
        """
        super().__init__(
            tavily_api_key=tavily_api_key,
            account_id=account_id,
            api_token=api_token,
            system_prompt=self.ENERGY_SYSTEM_PROMPT,
            include_domains=self.AUTHORITY_DOMAINS,
            max_search_results=2,  
            **kwargs
        )
    
    def get_energy_context(
        self,
        state: str,
        district: str,
    ) -> Dict[str, Any]:
        """
        Get energy consumption context for a specific location.
        
        """
        current_date = date.today().strftime("%B %d, %Y")
        
        # Simplified question to get exactly 3 focused queries
        question = f"""For {district} {state} Malaysia on {current_date}, find:
        Weather trends and forecast for electricity consumption
        Residential electricity tariff rates and changes
        Public holiday schedule and consumption patterns

        Provide past trends, current data, and future outlook for forecasting."""
        
        return self.research(question)



def create_research_agent_from_env(
    include_domains: Optional[List[str]] = None,
    system_prompt: Optional[str] = None,
    verbose: bool = True,
    **kwargs
) -> CloudflareResearchAgent:
    """
    Create research agent from environment variables.
    
    """
    load_dotenv()
    
    tavily_api_key = os.environ.get("TAVILY_API_KEY")
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    api_token = os.environ.get("CF_AI_API_TOKEN") or os.environ.get("CLOUDFLARE_API_TOKEN")
    
    if not tavily_api_key:
        raise ValueError("TAVILY_API_KEY not found in environment")
    if not account_id:
        raise ValueError("CLOUDFLARE_ACCOUNT_ID not found in environment")
    if not api_token:
        raise ValueError("CF_AI_API_TOKEN not found in environment")
    
    return CloudflareResearchAgent(
        tavily_api_key=tavily_api_key,
        account_id=account_id,
        api_token=api_token,
        include_domains=include_domains,
        system_prompt=system_prompt,
        verbose=verbose,
        **kwargs
    )


def create_energy_agent_from_env(verbose: bool = True, **kwargs) -> MalaysianEnergyAgent:
    """Create Malaysian Energy Agent from environment variables."""
    load_dotenv()
    
    tavily_api_key = os.environ.get("TAVILY_API_KEY")
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    api_token = os.environ.get("CF_AI_API_TOKEN") or os.environ.get("CLOUDFLARE_API_TOKEN")
    
    if not tavily_api_key:
        raise ValueError("TAVILY_API_KEY not found in environment")
    if not account_id:
        raise ValueError("CLOUDFLARE_ACCOUNT_ID not found in environment")
    if not api_token:
        raise ValueError("CF_AI_API_TOKEN not found in environment")
    
    return MalaysianEnergyAgent(
        tavily_api_key=tavily_api_key,
        account_id=account_id,
        api_token=api_token,
        verbose=verbose,
        **kwargs
    )


# --- Example Usage ---
if __name__ == "__main__":
    print("="*70)
    print("EXAMPLE: Malaysian Energy Research Agent")
    print("="*70)
    
    # Create the agent
    energy_agent = create_energy_agent_from_env(verbose=True)
    
    # Get energy context for a specific location
    result = energy_agent.get_energy_context(
        state="Selangor",
        district="Petaling",
    )
    
    print("\n" + "="*70)
    print("RESULT")
    print("="*70)
    print(result["answer"])
    
    if "sub_queries" in result:
        print("\n" + "="*70)
        print("SUB-QUERIES USED")
        print("="*70)
        for i, q in enumerate(result["sub_queries"], 1):
            print(f"{i}. {q}")