"""Base agent class."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime

from openai import OpenAI


@dataclass
class AgentOutput:
    """Output from an agent."""
    agent_name: str
    content: str
    sources: list[str] = field(default_factory=list)
    data: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "agent_name": self.agent_name,
            "content": self.content,
            "sources": self.sources,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "error": self.error,
        }


class BaseAgent(ABC):
    """Base class for all research agents."""
    
    name: str = "base"
    description: str = "Base agent"
    
    def __init__(self, client: Optional[OpenAI] = None, model: str = "gpt-4o"):
        self.client = client or OpenAI()
        self.model = model
    
    @abstractmethod
    def run(self, task: str, context: dict = None) -> AgentOutput:
        """Execute the agent's task."""
        pass
    
    def _complete(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """Call the LLM."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=kwargs.get("temperature", 0.3),
            **{k: v for k, v in kwargs.items() if k != "temperature"}
        )
        return response.choices[0].message.content
    
    def _complete_with_tools(self, system_prompt: str, user_prompt: str, tools: list) -> tuple[str, list]:
        """Call the LLM with tools."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.3,
        )
        
        tool_calls = []
        assistant_message = response.choices[0].message
        
        # Handle tool calls
        while assistant_message.tool_calls:
            messages.append(assistant_message)
            
            for tool_call in assistant_message.tool_calls:
                tool_calls.append({
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                })
                # Tool execution would happen here
                # For now, just acknowledge the tool call
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": "Tool executed successfully"
                })
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.3,
            )
            assistant_message = response.choices[0].message
        
        return assistant_message.content, tool_calls
