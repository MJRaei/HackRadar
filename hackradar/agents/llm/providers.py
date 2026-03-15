"""
Model provider factory for HackRadar agents.

Supports multiple LLM backends via the Factory pattern:
  - GEMINI            → Railtracks GeminiLLM
  - OPENAI            → Railtracks OpenAILLM (standard API)
  - OPENAI_COMPATIBLE → OpenAICompatibleLLM (custom endpoint, e.g. self-hosted GPT-OSS)

Usage:
    config = ModelConfig(
        provider=ModelProvider.OPENAI_COMPATIBLE,
        model_name="openai/gpt-oss-120b",
        api_key="test",
        base_url="https://<endpoint>/v1",
    )
    model = create_model(config)
    agent = rt.agent_node(name="my_agent", llm=model, ...)
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

import railtracks as rt

from hackradar.agents.llm.openai_compatible import OpenAICompatibleLLM

logger = logging.getLogger(__name__)


class ModelProvider(str, Enum):
    """Supported LLM backend providers."""

    GEMINI = "gemini"
    OPENAI = "openai"
    OPENAI_COMPATIBLE = "openai_compatible"  # Custom base_url (self-hosted, etc.)


@dataclass
class ModelConfig:
    """All configuration needed to instantiate a specific model backend."""

    provider: ModelProvider
    model_name: str
    api_key: str = ""
    base_url: str = ""  # Only required for OPENAI_COMPATIBLE


def create_model(config: ModelConfig) -> Any:
    """
    Factory that returns a Railtracks-compatible LLM instance.

    - GEMINI:            rt.llm.GeminiLLM   — Google Gemini via Railtracks
    - OPENAI:            rt.llm.OpenAILLM   — standard OpenAI API
    - OPENAI_COMPATIBLE: OpenAICompatibleLLM — custom endpoint (vLLM, HuggingFace, etc.)
                         Uses the double-prefix trick so the endpoint receives the full
                         scoped model name (e.g. "openai/gpt-oss-120b").

    Args:
        config: ModelConfig describing the desired provider and model.

    Returns:
        A Railtracks LLM instance accepted by rt.agent_node(llm=...).

    Raises:
        ValueError: If OPENAI_COMPATIBLE is requested without a base_url.
    """
    if config.provider == ModelProvider.GEMINI:
        logger.debug("Using Gemini model: %s", config.model_name)
        return rt.llm.GeminiLLM(config.model_name, api_key=config.api_key)

    if config.provider == ModelProvider.OPENAI_COMPATIBLE:
        if not config.base_url:
            raise ValueError("base_url must be set for ModelProvider.OPENAI_COMPATIBLE")
        logger.info(
            "OpenAI-compatible endpoint: %s  model: %s", config.base_url, config.model_name
        )
        return OpenAICompatibleLLM(
            model_name=config.model_name,
            api_base=config.base_url,
            api_key=config.api_key or "test",
        )

    # Standard OpenAI
    logger.info("Using OpenAI model: %s", config.model_name)
    return rt.llm.OpenAILLM(config.model_name, api_key=config.api_key)


def create_model_from_settings(settings: Any) -> Any:
    """
    Convenience factory that builds a ModelConfig from app Settings and
    returns a Railtracks LLM instance.

    Reads the following fields from *settings*:
        llm_provider    (str)  — "gemini" | "openai" | "openai_compatible"
        llm_model       (str)  — model name (e.g. "gemini-2.0-flash", "openai/gpt-oss-120b")
        openai_api_key  (str)  — API key for OpenAI / compatible endpoint
        openai_base_url (str)  — base URL for OPENAI_COMPATIBLE provider
        google_api_key  (str)  — API key for Gemini

    Args:
        settings: App Settings instance (hackradar.config.Settings).

    Returns:
        A Railtracks LLM instance.
    """
    provider = ModelProvider(settings.llm_provider)
    api_key = (
        getattr(settings, "google_api_key", "")
        if provider == ModelProvider.GEMINI
        else getattr(settings, "openai_api_key", "")
    )
    config = ModelConfig(
        provider=provider,
        model_name=settings.llm_model,
        api_key=api_key,
        base_url=getattr(settings, "openai_base_url", ""),
    )
    return create_model(config)
