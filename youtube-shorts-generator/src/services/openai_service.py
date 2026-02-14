"""
OpenAI API: GPT-4 (script), GPT-3.5 (metadata), embeddings. Retry + cost tracking.
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


@_retry()
def chat_completion(
    messages: List[dict],
    model: str = "gpt-4",
    temperature: float = 0.7,
) -> tuple[str, float]:
    """Return (content, estimated_cost_usd). Cost is approximate."""
    client = _client()
    r = client.chat.completions.create(model=model, messages=messages, temperature=temperature)
    content = (r.choices[0].message.content or "").strip()
    # Rough cost: gpt-4 ~$0.03/1k in, $0.06/1k out; gpt-3.5 much lower
    in_tokens = r.usage.prompt_tokens if r.usage else 0
    out_tokens = r.usage.completion_tokens if r.usage else 0
    if "gpt-4" in model:
        cost = (in_tokens * 0.00003) + (out_tokens * 0.00006)
    else:
        cost = (in_tokens * 0.0000015) + (out_tokens * 0.000002)
    return content, cost


@_retry()
def get_embeddings(texts: List[str], model: str = "text-embedding-3-small") -> tuple[List[List[float]], float]:
    """Return (list of embedding vectors, estimated_cost_usd)."""
    client = _client()
    r = client.embeddings.create(input=texts, model=model)
    vectors = [e.embedding for e in r.data]
    total_tokens = r.usage.total_tokens if r.usage else (sum(len(t.split()) * 4 for t in texts))
    cost = total_tokens * 0.00000002  # ~$0.02/1M
    return vectors, cost
