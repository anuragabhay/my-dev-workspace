"""
Anthropic API: Chat completions via Messages API.

Used by llm_router when agents.agent_name.provider is 'anthropic'.
Embeddings are not supported by Anthropic; use provider: openai for embedding agents.
"""
import os
from typing import Optional, List

from src.utils.retry import retry_decorator


def _client():
    import anthropic
    return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def _convert_messages(messages: List[dict]) -> List[dict]:
    """Convert OpenAI-format messages to Anthropic format (user/assistant)."""
    out: List[dict] = []
    for m in messages:
        role = (m.get("role") or "user").lower()
        content = m.get("content") or ""
        if role == "system":
            # Anthropic uses system in create() param, not in messages
            continue
        if role in ("user", "assistant"):
            out.append({"role": role, "content": content})
    return out


def _extract_system(messages: List[dict]) -> str:
    """Extract system message if present."""
    for m in messages:
        if (m.get("role") or "").lower() == "system":
            return (m.get("content") or "").strip()
    return ""


@retry_decorator(max_retries=3, base_delay=1.0, max_delay=60.0)
def chat_completion(
    messages: List[dict],
    model: Optional[str] = None,
    temperature: float = 0.7,
) -> tuple[str, float]:
    """Call Anthropic Messages API and return response text plus estimated cost.

    Args:
        messages: List of message dicts with "role" and "content" (OpenAI format).
        model: Model name (e.g. "claude-3-5-sonnet-20241022"). If None, uses claude-3-5-sonnet.
        temperature: Sampling temperature in [0, 1]. Default 0.7.

    Returns:
        Tuple of (response_content, estimated_cost_usd).
    """
    model_name = (model or "").strip() or "claude-3-5-sonnet-20241022"
    client = _client()
    system = _extract_system(messages)
    converted = _convert_messages(messages)
    if not converted:
        return "", 0.0

    kwargs: dict = {
        "model": model_name,
        "max_tokens": 4096,
        "messages": converted,
        "temperature": min(1.0, max(0.0, temperature)),
    }
    if system:
        kwargs["system"] = system

    resp = client.messages.create(**kwargs)
    text = ""
    if resp.content:
        for block in resp.content:
            if hasattr(block, "text"):
                text += block.text
    text = text.strip()

    # Rough cost estimate (Claude 3.5 Sonnet: ~$3/1M input, ~$15/1M output)
    in_tok = resp.usage.input_tokens if resp.usage else 0
    out_tok = resp.usage.output_tokens if resp.usage else 0
    cost = (in_tok * 0.000003) + (out_tok * 0.000015)
    return text, cost


def get_embeddings(texts: List[str], model: Optional[str] = None) -> tuple[List[List[float]], float]:
    """Anthropic does not provide an embeddings API. Use provider: openai for embedding agents.

    Raises:
        NotImplementedError: Anthropic does not support embeddings.
    """
    raise NotImplementedError(
        "Anthropic does not provide embeddings. Use provider: openai for agents that need "
        "embeddings (e.g. uniqueness, rag)."
    )
