"""
OpenAICompatibleLLM — Railtracks LLM for custom OpenAI-compatible endpoints.

Extends LiteLLMWrapper directly (bypassing ProviderLLMWrapper's model-registry
validation) so any model name accepted by the endpoint can be used without it
needing to appear in LiteLLM's built-in model list.

Double-prefix trick
-------------------
LiteLLM strips the first "openai/" prefix when selecting the provider handler
but forwards the remainder verbatim as the model field in the HTTP request:

    internal model_name : "openai/openai/gpt-oss-120b"
    LiteLLM strips       : "openai/"
    sent to endpoint     : model = "openai/gpt-oss-120b"   ✓

This ensures the `openai` handler is used (correct tool-calling format) while
the endpoint receives the full scoped model name it expects.

Usage:
    llm = OpenAICompatibleLLM(
        model_name="openai/gpt-oss-120b",
        api_base="https://<endpoint>/v1",
        api_key="test",
    )
"""

from railtracks.llm.models._litellm_wrapper import LiteLLMWrapper
from railtracks.llm.providers import ModelProvider


class OpenAICompatibleLLM(LiteLLMWrapper):
    """
    Railtracks LLM for self-hosted OpenAI-compatible endpoints.

    Pass the exact model name the endpoint expects (e.g. "openai/gpt-oss-120b")
    together with the endpoint base URL.  api_base and api_key are injected
    into every LiteLLM completion call.
    """

    def __init__(self, model_name: str, api_base: str, api_key: str = "test", **kwargs):
        super().__init__(
            model_name=f"openai/{model_name}",  # double-prefix — see module docstring
            api_base=api_base,
            api_key=api_key,
            **kwargs,
        )

    def model_provider(self) -> ModelProvider:
        return ModelProvider.OPENAI

    @classmethod
    def model_gateway(cls) -> ModelProvider:
        return ModelProvider.OPENAI
