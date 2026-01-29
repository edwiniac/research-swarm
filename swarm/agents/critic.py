"""Critic agent for critical analysis."""

import json
from typing import Optional

from .base import BaseAgent, AgentOutput


class CriticAgent(BaseAgent):
    """Agent that provides critical analysis and counterarguments."""
    
    name = "critic"
    description = "Identifies limitations, counterarguments, and alternative perspectives"
    
    def run(self, task: str, context: dict = None) -> AgentOutput:
        """Critically analyze the research findings."""
        try:
            # Generate critical analysis
            analysis = self._critical_analysis(task, context)
            
            return AgentOutput(
                agent_name=self.name,
                content=analysis["content"],
                data={
                    "counterarguments": analysis.get("counterarguments", []),
                    "limitations": analysis.get("limitations", []),
                    "alternative_views": analysis.get("alternative_views", [])
                },
                success=True
            )
        
        except Exception as e:
            return AgentOutput(
                agent_name=self.name,
                content=f"Critical analysis failed: {str(e)}",
                success=False,
                error=str(e)
            )
    
    def _critical_analysis(self, task: str, context: dict = None) -> dict:
        """Generate critical analysis."""
        system_prompt = """You are a critical analyst and devil's advocate. Your job is to:

1. Identify potential weaknesses in arguments or findings
2. Present counterarguments and alternative perspectives
3. Note limitations and caveats
4. Question assumptions
5. Identify what might be missing or overlooked

Be constructive but thorough. The goal is to strengthen the research 
by identifying potential blind spots.

Return JSON:
{
    "content": "Full critical analysis text...",
    "counterarguments": [
        "Counterargument 1: ...",
        "Counterargument 2: ..."
    ],
    "limitations": [
        "Limitation 1: ...",
        "Limitation 2: ..."
    ],
    "alternative_views": [
        "Alternative perspective: ...",
        "Different interpretation: ..."
    ],
    "missing_considerations": [
        "Not addressed: ...",
        "Should consider: ..."
    ]
}"""

        context_str = ""
        if context:
            context_str = f"\n\nFindings to critique:\n"
            for key, value in context.items():
                if isinstance(value, str):
                    context_str += f"\n{key}:\n{value[:1500]}\n"
        
        user_prompt = f"Research task: {task}{context_str}"
        
        response = self._complete(
            system_prompt,
            user_prompt,
            response_format={"type": "json_object"}
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"content": response, "counterarguments": [], "limitations": []}
