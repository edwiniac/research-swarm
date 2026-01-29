"""Literature review agent."""

import json
from typing import Optional

from .base import BaseAgent, AgentOutput


class LiteratureAgent(BaseAgent):
    """Agent that reviews academic and industry literature."""
    
    name = "literature"
    description = "Reviews academic papers, research, and industry reports"
    
    def run(self, task: str, context: dict = None) -> AgentOutput:
        """Review relevant literature for the task."""
        try:
            # Generate literature review
            review = self._generate_review(task, context)
            
            return AgentOutput(
                agent_name=self.name,
                content=review["content"],
                sources=review.get("sources", []),
                data=review.get("key_papers", {}),
                success=True
            )
        
        except Exception as e:
            return AgentOutput(
                agent_name=self.name,
                content=f"Literature review failed: {str(e)}",
                success=False,
                error=str(e)
            )
    
    def _generate_review(self, task: str, context: dict = None) -> dict:
        """Generate a literature review based on knowledge."""
        system_prompt = """You are an academic research assistant with extensive knowledge 
of published research, papers, and industry reports.

For the given research task:
1. Identify key academic concepts and theories
2. Reference relevant research areas and seminal works
3. Discuss current state of research
4. Note any research gaps or open questions
5. Mention relevant conferences, journals, or organizations

Format your response as a structured literature review.
When mentioning specific works, papers, or researchers, be accurate - 
only reference things you're confident exist.

Return JSON:
{
    "content": "The full literature review text...",
    "sources": ["arxiv.org/...", "paper title by author", ...],
    "key_papers": {
        "foundational": ["paper/concept 1", "paper/concept 2"],
        "recent": ["recent work 1", "recent work 2"]
    }
}"""

        context_str = ""
        if context:
            context_str = f"\n\nContext from other research:\n{json.dumps(context, default=str)[:2000]}"
        
        user_prompt = f"Research task: {task}{context_str}"
        
        response = self._complete(
            system_prompt,
            user_prompt,
            response_format={"type": "json_object"}
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"content": response, "sources": [], "key_papers": {}}
