"""Research agents."""

from .base import BaseAgent
from .search import SearchAgent
from .data import DataAgent
from .literature import LiteratureAgent
from .critic import CriticAgent
from .synthesis import SynthesisAgent

__all__ = [
    "BaseAgent",
    "SearchAgent",
    "DataAgent", 
    "LiteratureAgent",
    "CriticAgent",
    "SynthesisAgent",
]
