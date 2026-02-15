"""
OpenAI API: Chat Completions only (Model capabilities); embeddings. Retry + cost tracking.
Uses /v1/chat/completions so projects with 'Model capabilities' but not 'Responses API' work.
"""
import os
import time
from typing import Optional, List, Any

# Lazy import openai to avoid import errors if key missing
def _client():
    import openai
    return openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _retry(max_retries: int = 3, backoff: tuple = (1, 2, 4)):
    def decorator(f):
        def wrapped(*args, **kwargs):
            last = None
            for i, wait in enumerate(backoff[:max_retries]):
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    last = e
                    if i < max_retries - 1:
                        time.sleep(wait)
            raise last
        return wrapped
    return decorator


def _default_chat_model() -> str:
    """First model to try. Default gpt-4.1 (Chat Completions); set OPENAI_CHAT_MODEL to override."""
    return (os.getenv("OPENAI_CHAT_MODEL") or "").strip() or "gpt-4.1"


def _fallback_chat_models() -> List[str]:
    """If default returns 403/model_not_found, try these in order. Set OPENAI_FALLBACK_CHAT_MODEL (comma-separated) to override."""
    custom = (os.getenv("OPENAI_FALLBACK_CHAT_MODEL") or "").strip()
    if custom:
        return [m.strip() for m in custom.split(",") if m.strip()]
    return ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4.1-nano"]


def _is_model_access_error(e: Exception) -> bool:
    """True if error indicates project lacks access to the model."""
    s = str(e).lower()
    return "403" in s or "model_not_found" in s or "does not have access" in s


def _chat_completion_chat_api(
    client: Any, messages: List[dict], model: str, temperature: float
) -> tuple[str, float]:
    """Call Chat Completions API (/v1/chat/completions); return (content, cost)."""
    r = client.chat.completions.create(model=model, messages=messages, temperature=temperature)
    content = (r.choices[0].message.content or "").strip()
    in_tokens = r.usage.prompt_tokens if r.usage else 0
    out_tokens = r.usage.completion_tokens if r.usage else 0
    if "gpt-4" in model and "mini" not in model and "nano" not in model:
        cost = (in_tokens * 0.00003) + (out_tokens * 0.00006)
    elif "gpt-4o-mini" in model or "gpt-3.5" in model:
        cost = (in_tokens * 0.00000015) + (out_tokens * 0.0000006)
    else:
        cost = (in_tokens * 0.0000015) + (out_tokens * 0.000002)
    return content, cost


@_retry()
def chat_completion(
    messages: List[dict],
    model: Optional[str] = None,
    temperature: float = 0.7,
) -> tuple[str, float]:
    """Return (content, estimated_cost_usd). Uses Chat Completions only (Model capabilities). Tries default model then fallbacks on 403."""
    preferred = (model or "").strip() or _default_chat_model()
    fallbacks = _fallback_chat_models()
    # Try preferred first, then each fallback (skip if already preferred)
    to_try = [preferred] + [m for m in fallbacks if m != preferred]
    client = _client()
    last_err = None
    for m in to_try:
        try:
            return _chat_completion_chat_api(client, messages, m, temperature)
        except Exception as e:
            last_err = e
            if _is_model_access_error(e):
                continue
            raise
    if last_err is not None:
        raise last_err
    raise RuntimeError("No chat model available")


def _default_embedding_model() -> str:
    """Default embedding model; set OPENAI_EMBEDDING_MODEL to override."""
    return (os.getenv("OPENAI_EMBEDDING_MODEL") or "").strip() or "text-embedding-3-small"


def _fallback_embedding_models() -> List[str]:
    """When default embedding model returns 403, try these. Set OPENAI_FALLBACK_EMBEDDING_MODEL (comma-separated) to override."""
    custom = (os.getenv("OPENAI_FALLBACK_EMBEDDING_MODEL") or "").strip()
    if custom:
        return [m.strip() for m in custom.split(",") if m.strip()]
    return ["text-embedding-ada-002"]


@_retry()
def get_embeddings(texts: List[str], model: Optional[str] = None) -> tuple[List[List[float]], float]:
    """Return (list of embedding vectors, estimated_cost_usd). Tries default model then fallbacks on 403."""
    preferred = (model or "").strip() or _default_embedding_model()
    fallbacks = _fallback_embedding_models()
    to_try = [preferred] + [m for m in fallbacks if m != preferred]
    client = _client()
    last_err = None
    for emb_model in to_try:
        try:
            r = client.embeddings.create(input=texts, model=emb_model)
            vectors = [e.embedding for e in r.data]
            total_tokens = r.usage.total_tokens if r.usage else (sum(len(t.split()) * 4 for t in texts))
            cost = total_tokens * 0.00000002  # ~$0.02/1M
            return vectors, cost
        except Exception as e:
            last_err = e
            if _is_model_access_error(e):
                continue
            raise
    if last_err is not None:
        raise last_err
    raise RuntimeError("No embedding model available")
