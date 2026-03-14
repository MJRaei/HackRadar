"""
Abstract base for all HackRadar agents.

Every agent exposes a single async `run(**kwargs) -> dict` method.
Subclasses configure their own tools and system prompt, then delegate
execution to Railtracks (rt.agent_node / rt.call).
"""

import abc
import logging
from typing import Any, Union

logger = logging.getLogger(__name__)


class BaseAgent(abc.ABC):
    """
    Abstract base class for HackRadar judging agents.

    Subclasses must implement:
        - `run(**kwargs)` → dict

    The *model* parameter is a Railtracks LLM instance returned by
    ``hackradar.agents.models.create_model_from_settings``.
    """

    def __init__(self, model: Union[str, Any]) -> None:
        self.model = model

    @abc.abstractmethod
    async def run(self, **kwargs: Any) -> dict[str, Any]:
        """Execute the agent and return a structured result dict."""
        ...
