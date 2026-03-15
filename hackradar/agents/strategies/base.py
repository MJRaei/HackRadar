"""
Abstract base class for agent execution strategies.

Concrete strategies implement different approaches based on LLM capabilities
(e.g. tool-calling vs. RAG prefetch for models without function-calling support).
"""

from abc import ABC, abstractmethod
from typing import Any


class Strategy(ABC):
    @abstractmethod
    async def run(self, model: Any, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Execute the strategy and return a result dict."""
        ...
