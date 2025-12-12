# tools/info_search.py
import os
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from tavily import TavilyClient # Direct import, no LangChain wrapper

# Set this in your .env file: TAVILY_API_KEY=tvly-...
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# max_results=3 means it reads the top 3 pages fully
search_tool = TavilySearch(max_results=3)

@tool
def search_university_info(query: str):
    """
    Performs a deep search for Northumbria University information.
    Returns actual page content, not just snippets.
    """
    # 1. Define the whitelist of trusted domains
    trusted_sites = [
        "northumbria.ac.uk",
        "mynsu.co.uk",
        "linkedin.com/school/northumbria-university",
        "northumbria.native.fm",       # <--- The REAL events calendar
        "store.northumbria.ac.uk"      # <--- Ticketed trips and workshops
    ]
    
    # 2. Join them with OR
    # Result: "(site:northumbria.ac.uk OR site:mynsu.co.uk OR ...)"
    domain_filter = " OR ".join([f"site:{d}" for d in trusted_sites])
    
    site_query = f"({domain_filter}) {query}"
    
    try:
        response = tavily_client.search(
            query=site_query, 
            search_depth="advanced", 
            max_results=3
        )
        
        # 4. Parse Results
        results = response.get("results", [])

        if not results:
            return "No information found on the university websites."
        
        # Format the results nicely for the LLM
        # Tavily returns a list of dicts: [{'url': '...', 'content': '...'}]
        context = ""
        for res in results:
            context += f"\nSource: {res['url']}\nContent: {res['content']}\n"
            
        return context
    except Exception as e:
        return f"Search failed: {e}"