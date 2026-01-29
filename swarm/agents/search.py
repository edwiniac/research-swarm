"""Search agent for web research."""

import os
import json
from typing import Optional

import requests

from .base import BaseAgent, AgentOutput


class SearchAgent(BaseAgent):
    """Agent that searches the web for relevant information."""
    
    name = "search"
    description = "Searches the web for relevant information and sources"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
    
    def run(self, task: str, context: dict = None) -> AgentOutput:
        """Search the web for information related to the task."""
        try:
            # Generate search queries
            queries = self._generate_search_queries(task, context)
            
            # Execute searches
            all_results = []
            sources = []
            
            for query in queries[:3]:  # Limit to 3 queries
                results = self._search(query)
                all_results.extend(results)
                sources.extend([r.get("url", "") for r in results if r.get("url")])
            
            # Synthesize search results
            content = self._synthesize_results(task, all_results)
            
            return AgentOutput(
                agent_name=self.name,
                content=content,
                sources=list(set(sources))[:10],  # Dedupe and limit
                data={"queries": queries, "result_count": len(all_results)},
                success=True
            )
        
        except Exception as e:
            return AgentOutput(
                agent_name=self.name,
                content=f"Search failed: {str(e)}",
                success=False,
                error=str(e)
            )
    
    def _generate_search_queries(self, task: str, context: dict = None) -> list[str]:
        """Generate search queries for the task."""
        system_prompt = """You are a search query generator. Given a research task, 
generate 3 diverse search queries that will help find relevant information.

Return a JSON array of strings, nothing else.
Example: ["query 1", "query 2", "query 3"]"""

        user_prompt = f"Research task: {task}"
        if context:
            user_prompt += f"\n\nAdditional context: {json.dumps(context)}"
        
        response = self._complete(system_prompt, user_prompt)
        
        try:
            # Try to parse as JSON
            queries = json.loads(response)
            if isinstance(queries, list):
                return queries[:5]
        except json.JSONDecodeError:
            pass
        
        # Fallback: use the task as the query
        return [task]
    
    def _search(self, query: str) -> list[dict]:
        """Execute a web search."""
        if self.tavily_api_key:
            return self._tavily_search(query)
        else:
            return self._duckduckgo_search(query)
    
    def _tavily_search(self, query: str) -> list[dict]:
        """Search using Tavily API."""
        try:
            response = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": self.tavily_api_key,
                    "query": query,
                    "search_depth": "basic",
                    "max_results": 5,
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            return [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", ""),
                    "score": r.get("score", 0),
                }
                for r in data.get("results", [])
            ]
        except Exception as e:
            print(f"Tavily search error: {e}")
            return []
    
    def _duckduckgo_search(self, query: str) -> list[dict]:
        """Fallback search using DuckDuckGo (limited)."""
        try:
            # Using DuckDuckGo instant answer API (limited but free)
            response = requests.get(
                "https://api.duckduckgo.com/",
                params={
                    "q": query,
                    "format": "json",
                    "no_html": 1,
                },
                timeout=10
            )
            data = response.json()
            
            results = []
            
            # Abstract
            if data.get("Abstract"):
                results.append({
                    "title": data.get("Heading", ""),
                    "url": data.get("AbstractURL", ""),
                    "content": data.get("Abstract", ""),
                })
            
            # Related topics
            for topic in data.get("RelatedTopics", [])[:3]:
                if isinstance(topic, dict) and topic.get("Text"):
                    results.append({
                        "title": topic.get("Text", "")[:50],
                        "url": topic.get("FirstURL", ""),
                        "content": topic.get("Text", ""),
                    })
            
            return results
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            return []
    
    def _synthesize_results(self, task: str, results: list[dict]) -> str:
        """Synthesize search results into useful information."""
        if not results:
            return "No search results found."
        
        # Format results for LLM
        results_text = ""
        for i, r in enumerate(results[:10], 1):
            results_text += f"\n[{i}] {r.get('title', 'Untitled')}\n"
            results_text += f"    URL: {r.get('url', 'N/A')}\n"
            results_text += f"    Content: {r.get('content', '')[:500]}\n"
        
        system_prompt = """You are a research assistant. Synthesize the search results 
into a coherent summary that addresses the research task. 

Include:
1. Key findings from the sources
2. Important facts and data
3. Different perspectives if present
4. Note which sources support which claims [1], [2], etc.

Be comprehensive but concise."""

        user_prompt = f"Research task: {task}\n\nSearch Results:{results_text}"
        
        return self._complete(system_prompt, user_prompt)
