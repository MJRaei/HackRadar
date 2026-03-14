"""
Abstract base for all HackRadar ADK agents.

Every agent exposes a single async `run(**kwargs) -> dict` method.
Subclasses configure their own tools and system prompt, then delegate
execution to the Google ADK Runner.
"""

import abc
import logging
from typing import Any

logger = logging.getLogger(__name__)


class BaseAgent(abc.ABC):
    """
    Abstract base class for HackRadar judging agents.

    Subclasses must implement:
        - `_build_agent()` → google.adk.agents.Agent
        - `run(**kwargs)` → dict
    """

    def __init__(self, model: str) -> None:
        self.model = model

    @abc.abstractmethod
    async def run(self, **kwargs: Any) -> dict[str, Any]:
        """Execute the agent and return a structured result dict."""
        ...
