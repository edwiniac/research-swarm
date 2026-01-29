"""Main coordinator for the research swarm."""

import asyncio
import concurrent.futures
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import json

from openai import OpenAI

from .agents import (
    BaseAgent,
    SearchAgent,
    DataAgent,
    LiteratureAgent,
    CriticAgent,
    SynthesisAgent,
)
from .agents.base import AgentOutput


@dataclass
class ResearchResult:
    """Result of a research query."""
    query: str
    report: str
    summary: str
    agent_outputs: dict[str, AgentOutput]
    sources: list[str]
    timestamp: datetime
    depth: str
    duration_seconds: float
    
    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "report": self.report,
            "summary": self.summary,
            "agent_outputs": {k: v.to_dict() for k, v in self.agent_outputs.items()},
            "sources": self.sources,
            "timestamp": self.timestamp.isoformat(),
            "depth": self.depth,
            "duration_seconds": self.duration_seconds,
        }


class ResearchSwarm:
    """Orchestrates multiple research agents working in parallel."""
    
    DEPTH_CONFIG = {
        "quick": {
            "agents": ["search", "synthesis"],
            "max_parallel": 2,
        },
        "standard": {
            "agents": ["search", "data", "literature", "synthesis"],
            "max_parallel": 4,
        },
        "deep": {
            "agents": ["search", "data", "literature", "critic", "synthesis"],
            "max_parallel": 5,
        },
    }
    
    def __init__(
        self,
        client: Optional[OpenAI] = None,
        model: str = "gpt-4o",
        max_workers: int = 5
    ):
        self.client = client or OpenAI()
        self.model = model
        self.max_workers = max_workers
        
        # Initialize agents
        self.agents: dict[str, BaseAgent] = {
            "search": SearchAgent(self.client, self.model),
            "data": DataAgent(self.client, self.model),
            "literature": LiteratureAgent(self.client, self.model),
            "critic": CriticAgent(self.client, self.model),
            "synthesis": SynthesisAgent(self.client, self.model),
        }
    
    def register_agent(self, agent: BaseAgent):
        """Register a custom agent."""
        self.agents[agent.name] = agent
    
    def research(
        self,
        query: str,
        depth: str = "standard",
        agents: Optional[list[str]] = None,
    ) -> ResearchResult:
        """Run a research query using the swarm."""
        start_time = datetime.now()
        
        # Get config for depth
        config = self.DEPTH_CONFIG.get(depth, self.DEPTH_CONFIG["standard"])
        
        # Determine which agents to use
        agent_names = agents or config["agents"]
        
        # Make sure synthesis is always last
        if "synthesis" in agent_names:
            agent_names.remove("synthesis")
        
        # Plan the research
        plan = self._plan_research(query, agent_names)
        
        # Execute research agents in parallel (except synthesis)
        agent_outputs = self._execute_parallel(query, agent_names, plan)
        
        # Run synthesis with all other outputs as context
        synthesis_output = self.agents["synthesis"].run(
            task=query,
            context=agent_outputs
        )
        agent_outputs["synthesis"] = synthesis_output
        
        # Collect all sources
        all_sources = []
        for output in agent_outputs.values():
            all_sources.extend(output.sources)
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()
        
        # Extract summary (first paragraph of report)
        report = synthesis_output.content
        summary = report.split("\n\n")[0] if "\n\n" in report else report[:500]
        
        return ResearchResult(
            query=query,
            report=report,
            summary=summary,
            agent_outputs=agent_outputs,
            sources=list(set(all_sources)),
            timestamp=start_time,
            depth=depth,
            duration_seconds=duration,
        )
    
    def _plan_research(self, query: str, agent_names: list[str]) -> dict:
        """Plan the research strategy."""
        system_prompt = """You are a research coordinator. Given a research query,
create a brief plan for how to investigate it.

For each agent, provide a specific task. Return JSON:
{
    "search": "specific search task",
    "data": "specific data extraction task",
    "literature": "specific literature review task",
    "critic": "specific critical analysis task"
}

Only include tasks for the agents listed. Be specific and actionable."""

        user_prompt = f"Query: {query}\n\nAgents available: {', '.join(agent_names)}"
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            # Default tasks
            return {name: query for name in agent_names}
    
    def _execute_parallel(
        self,
        query: str,
        agent_names: list[str],
        plan: dict
    ) -> dict[str, AgentOutput]:
        """Execute agents in parallel."""
        outputs = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all agent tasks
            future_to_agent = {}
            for name in agent_names:
                if name in self.agents:
                    agent = self.agents[name]
                    task = plan.get(name, query)
                    future = executor.submit(agent.run, task, {})
                    future_to_agent[future] = name
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_agent):
                agent_name = future_to_agent[future]
                try:
                    output = future.result(timeout=120)
                    outputs[agent_name] = output
                except Exception as e:
                    outputs[agent_name] = AgentOutput(
                        agent_name=agent_name,
                        content=f"Agent failed: {str(e)}",
                        success=False,
                        error=str(e)
                    )
        
        return outputs
    
    def chat(self, query: str) -> str:
        """Simple chat interface for quick queries."""
        result = self.research(query, depth="quick")
        return result.report
