"""Data extraction agent."""

import json
from typing import Optional

from .base import BaseAgent, AgentOutput


class DataAgent(BaseAgent):
    """Agent that extracts and analyzes data from content."""
    
    name = "data"
    description = "Extracts statistics, figures, and structured data"
    
    def run(self, task: str, context: dict = None) -> AgentOutput:
        """Extract data relevant to the task."""
        try:
            # Get any existing content from other agents
            existing_content = ""
            if context:
                for key, value in context.items():
                    if isinstance(value, str):
                        existing_content += f"\n{key}:\n{value}\n"
            
            # Extract structured data
            data_extraction = self._extract_data(task, existing_content)
            
            return AgentOutput(
                agent_name=self.name,
                content=data_extraction["summary"],
                data=data_extraction["data"],
                success=True
            )
        
        except Exception as e:
            return AgentOutput(
                agent_name=self.name,
                content=f"Data extraction failed: {str(e)}",
                success=False,
                error=str(e)
            )
    
    def _extract_data(self, task: str, content: str) -> dict:
        """Extract structured data from content."""
        system_prompt = """You are a data extraction specialist. Your job is to:

1. Identify any statistics, numbers, percentages, or quantitative data
2. Extract key metrics and figures
3. Organize data into a structured format
4. Note the source/context of each data point

Return a JSON object with:
{
    "summary": "A paragraph summarizing the key data findings",
    "data": {
        "metrics": [
            {"name": "metric name", "value": "value", "context": "where this came from"},
            ...
        ],
        "trends": ["trend 1", "trend 2"],
        "comparisons": [{"item1": "x", "item2": "y", "comparison": "description"}]
    }
}

If no quantitative data is available, provide qualitative insights instead."""

        user_prompt = f"Task: {task}\n\nContent to analyze:\n{content[:8000]}"
        
        response = self._complete(
            system_prompt, 
            user_prompt,
            response_format={"type": "json_object"}
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "summary": response,
                "data": {}
            }
