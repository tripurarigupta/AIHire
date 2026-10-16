"""Lazy LangChain client for LLM-backed features (AI mock interview).

Deliberately NOT imported at application startup: `langchain` and its provider
packages are optional dependencies, so importing them eagerly would stop the
whole API from booting when they are absent or when no API key is configured.
Importing this module is always safe; the heavy imports happen on first use.
"""
from __future__ import annotations

import logging
from functools import lru_cache
from typing import TypeVar

from pydantic import BaseModel

from app.core.config import settings

logger = logging.getLogger(__name__)

SchemaT = TypeVar("SchemaT", bound=BaseModel)


class LLMUnavailableError(RuntimeError):
    """The LLM path cannot be used; callers must fall back to the rule engine."""


def is_llm_enabled() -> bool:
    """True only when the feature is switched on *and* fully configured.

    Logs once per misconfiguration rather than raising, so an unset key degrades
    to the rule-based engine instead of breaking the interview feature.
    """
    if not settings.LLM_ENABLED:
        return False

    if not settings.LLM_API_KEY or not settings.LLM_MODEL:
        logger.warning(
            "LLM_ENABLED is set but LLM_API_KEY/LLM_MODEL are missing; "
            "falling back to the rule-based interview engine."
        )
        return False

    return True


@lru_cache(maxsize=8)
def _cached_structured_model(schema: type[SchemaT], temperature: float):
    """Build (and memoise) a chat model bound to `schema`.

    Cached per (schema, temperature) so repeated requests do not re-create the
    underlying client on every call.
    """
    # Imported lazily: a missing optional dependency must break only this
    # feature, never `app.main`.
    from langchain.chat_models import init_chat_model

    model = init_chat_model(
        f"{settings.LLM_PROVIDER}:{settings.LLM_MODEL}",
        temperature=temperature,
        timeout=settings.LLM_TIMEOUT_SECONDS,
        max_retries=settings.LLM_MAX_RETRIES,
        api_key=settings.LLM_API_KEY,
    )
    # Uses provider-native structured output where available (OpenAI,
    # Anthropic, Gemini), otherwise falls back to tool calling.
    return model.with_structured_output(schema)


def get_structured_model(schema: type[SchemaT], temperature: float = 0.2):
    """Return a chat model bound to `schema`, or raise LLMUnavailableError."""
    if not is_llm_enabled():
        raise LLMUnavailableError("LLM is not enabled or not configured.")

    try:
        return _cached_structured_model(schema, temperature)
    except ImportError as exc:
        raise LLMUnavailableError(
            "langchain is not installed. Run: "
            "pip install langchain langchain-google-genai"
        ) from exc
    except Exception as exc:  # unknown model id, bad key format, etc.
        raise LLMUnavailableError(f"Could not initialise LLM: {exc}") from exc