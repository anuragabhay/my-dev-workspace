"""
LLM provider abstraction: Anthropic and OpenAI backends.
Exposes chat_sync and chat_stream; brain and server integrate via this module.

Anthropic and OpenAI branches are preserved for open-source use and future extensibility.
The unified Orchestrator UI enforces local-only at startup; these branches are not reachable
in normal operation.
"""

from typing import AsyncIterator, List, Optional


ANTHROPIC_DEFAULT_MODEL = "claude-sonnet-4-20250514"


def _resolve_model(
    model: str,
    provider: str,
    openai_fallback_model: str,
) -> str:
    """
    Resolve model when it is missing, empty, or equals provider name (anthropic/openai).
    Ensures the API never receives "anthropic" or "openai" as the model.
    """
    # model param must be a valid model ID (see chat_completions.md)
    def _safe_openai_fallback() -> str:
        if openai_fallback_model.strip().lower() in ("anthropic", "openai"):
            return "gpt-4o-mini"
        return openai_fallback_model

    if not model or not str(model).strip():
        if provider == "anthropic":
            return ANTHROPIC_DEFAULT_MODEL
        if provider == "openai":
            return _safe_openai_fallback()
        return model or ""
    m = str(model).strip().lower()
    if m in ("anthropic", "openai"):
        if provider == "anthropic":
            return ANTHROPIC_DEFAULT_MODEL
        if provider == "openai":
            return _safe_openai_fallback()
    return model


def _resolve_openai_model(model: str, openai_fallback: str) -> str:
    """If model is Anthropic-specific (claude-*), use openai_fallback; else use model as-is."""
    if model and model.lower().startswith("claude-"):
        return openai_fallback
    return model


def _call_anthropic_sync(
    system: str,
    user: str,
    model: str,
    api_key: str,
    max_tokens: int = 2048,
    messages: Optional[List[dict]] = None,
) -> str:
    """Call Anthropic API synchronously. Returns full reply text."""
    from anthropic import Anthropic

    client = Anthropic(api_key=api_key)
    msg_list = messages if messages is not None else [{"role": "user", "content": user}]
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=msg_list,
    )

    if not response.content:
        return ""
    parts = []
    for block in response.content:
        if hasattr(block, "text"):
            parts.append(block.text)
    return "\n".join(parts)


async def _call_anthropic_stream(
    system: str,
    messages: list[dict],
    model: str,
    api_key: str,
    max_tokens: int = 2048,
) -> AsyncIterator[str]:
    """Stream Anthropic API. Yields text chunks."""
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic(api_key=api_key)
    async with client.messages.stream(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=messages,
    ) as stream:
        async for text in stream.text_stream:
            if text:
                yield text


def _call_openai_sync(
    system: str,
    user: str,
    model: str,
    api_key: str,
    max_tokens: int = 2048,
    messages: Optional[List[dict]] = None,
) -> str:
    """Call OpenAI API synchronously. Returns full reply text."""
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    if messages is not None:
        openai_messages = [{"role": "system", "content": system}] + [
            {"role": m.get("role", "user"), "content": m.get("content", "")}
            for m in messages
        ]
    else:
        openai_messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
    response = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=openai_messages,
    )

    choice = response.choices[0] if response.choices else None
    if not choice or not choice.message:
        return ""
    return choice.message.content or ""


async def _call_openai_stream(
    system: str,
    messages: list[dict],
    model: str,
    api_key: str,
    max_tokens: int = 2048,
) -> AsyncIterator[str]:
    """Stream OpenAI API. Yields text chunks."""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=api_key)
    openai_messages = [{"role": "system", "content": system}] + [
        {"role": m.get("role", "user"), "content": m.get("content", "")}
        for m in messages
    ]

    stream = await client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=openai_messages,
        stream=True,
    )

    async for chunk in stream:
        if chunk.choices and chunk.choices[0].delta:
            content = chunk.choices[0].delta.content
            if content:
                yield content


def chat_sync(
    system: str,
    user: str,
    model: str,
    anthropic_key: Optional[str],
    openai_key: Optional[str],
    provider: str,
    openai_fallback_model: str = "gpt-4o-mini",
    messages: Optional[List[dict]] = None,
) -> str:
    """
    Single non-streaming LLM call.

    Args:
        system: System prompt.
        user: User message (used when messages is None).
        model: Model name (e.g. claude-sonnet-4-20250514 or gpt-4o-mini).
        anthropic_key: Anthropic API key (required if provider=anthropic).
        openai_key: OpenAI API key (required if provider=openai).
        provider: "anthropic" or "openai".
        openai_fallback_model: Model to use when provider=openai and model is claude-*.
        messages: Optional multi-turn messages [{"role":"user"|"assistant","content":str}].
                  When provided, used instead of user for the API call.

    Returns:
        Full reply text.

    Raises:
        ValueError: If provider is unknown or required API key is missing.
    """
    provider = provider.lower()
    if provider == "anthropic":
        if not anthropic_key:
            raise ValueError(
                "ANTHROPIC_API_KEY or ORCHESTRATOR_LLM_API_KEY required when provider=anthropic. "
                "Set one of these env vars."
            )
        model = _resolve_model(model, provider, openai_fallback_model)
        return _call_anthropic_sync(system, user, model, anthropic_key, messages=messages)
    if provider == "openai":
        if not openai_key:
            raise ValueError(
                "OPENAI_API_KEY or ORCHESTRATOR_OPENAI_API_KEY required when provider=openai. "
                "Set one of these env vars."
            )
        model = _resolve_model(model, provider, openai_fallback_model)
        resolved_model = _resolve_openai_model(model, openai_fallback_model)
        return _call_openai_sync(system, user, resolved_model, openai_key, messages=messages)
    raise ValueError(f"Unknown provider: {provider}. Use 'anthropic' or 'openai'.")


async def chat_stream(
    system: str,
    messages: list[dict],
    model: str,
    anthropic_key: Optional[str],
    openai_key: Optional[str],
    provider: str,
    openai_fallback_model: str = "gpt-4o-mini",
) -> AsyncIterator[str]:
    """
    Streaming LLM call. Yields text chunks.

    Args:
        system: System prompt.
        messages: List of {"role": "user"|"assistant", "content": str}.
        model: Model name.
        anthropic_key: Anthropic API key (required if provider=anthropic).
        openai_key: OpenAI API key (required if provider=openai).
        provider: "anthropic" or "openai".
        openai_fallback_model: Model to use when provider=openai and model is claude-*.

    Yields:
        Text chunks.

    Raises:
        ValueError: If provider is unknown or required API key is missing.
    """
    provider = provider.lower()
    if provider == "anthropic":
        if not anthropic_key:
            raise ValueError(
                "ANTHROPIC_API_KEY or ORCHESTRATOR_LLM_API_KEY required when provider=anthropic. "
                "Set one of these env vars."
            )
        model = _resolve_model(model, provider, openai_fallback_model)
        async for chunk in _call_anthropic_stream(system, messages, model, anthropic_key):
            yield chunk
        return
    if provider == "openai":
        if not openai_key:
            raise ValueError(
                "OPENAI_API_KEY or ORCHESTRATOR_OPENAI_API_KEY required when provider=openai. "
                "Set one of these env vars."
            )
        model = _resolve_model(model, provider, openai_fallback_model)
        resolved_model = _resolve_openai_model(model, openai_fallback_model)
        async for chunk in _call_openai_stream(system, messages, resolved_model, openai_key):
            yield chunk
        return
    raise ValueError(f"Unknown provider: {provider}. Use 'anthropic' or 'openai'.")
