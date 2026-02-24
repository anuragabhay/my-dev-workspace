"""
LLM Router: Routes chat and embedding calls to OpenAI or Anthropic based on config.

Reads agents.* from config.yaml (provider, model) and delegates to openai_service
or anthropic_service. Agents without provider (tts, video, etc.) are not routed here.
"""
from typing import Optional, List

from src.utils.config import load_config


def _get_agent_config(agent_name: str) -> dict:
    """Get agent config from config.agents.agent_name. Returns {} if missing."""
    config = load_config()
    agents = config.get("agents") or {}
    return agents.get(agent_name) or {}


def _resolve_provider_and_model(agent_name: str, model_override: Optional[str], for_embeddings: bool = False) -> tuple[str, str]:
    """Resolve (provider, model) for an agent. Defaults to openai + env/default model."""
    cfg = _get_agent_config(agent_name)
    provider = (cfg.get("provider") or "openai")
    if provider and str(provider).lower() == "null":
        provider = "openai"
    provider = str(provider or "openai").lower()

    model = model_override or cfg.get("model") or ""
    if not model or not str(model).strip():
        if for_embeddings:
            from src.services.openai_service import _default_embedding_model
            model = _default_embedding_model()
        else:
            from src.services.openai_service import _default_chat_model
            model = _default_chat_model()

    if for_embeddings and provider == "anthropic":
        raise NotImplementedError(
            "Anthropic does not support embeddings. Set provider: openai for agent "
            f"'{agent_name}' (or use a different agent with OpenAI embeddings)."
        )
    return provider, str(model).strip()


def chat_completion(
    agent_name: str,
    messages: List[dict],
    model: Optional[str] = None,
    temperature: float = 0.7,
) -> tuple[str, float]:
    """Route chat completion to OpenAI or Anthropic based on agents.{agent_name} config.

    Args:
        agent_name: Agent name (e.g. "research", "script") for config lookup.
        messages: List of message dicts with "role" and "content".
        model: Override model from config. If None, uses config agents.{agent_name}.model.
        temperature: Sampling temperature.

    Returns:
        Tuple of (response_content, estimated_cost_usd).
    """
    provider, resolved_model = _resolve_provider_and_model(agent_name, model, for_embeddings=False)
    if provider == "anthropic":
        from src.services.anthropic_service import chat_completion as anthropic_chat
        return anthropic_chat(messages=messages, model=resolved_model, temperature=temperature)
    from src.services.openai_service import chat_completion as openai_chat
    return openai_chat(messages=messages, model=resolved_model, temperature=temperature)


def get_model_for_agent(agent_name: str, for_embeddings: bool = False) -> Optional[str]:
    """Get the configured model for an agent. Returns None if not applicable or on error."""
    try:
        _, model = _resolve_provider_and_model(agent_name, None, for_embeddings=for_embeddings)
        return model.strip() if model else None
    except Exception:
        return None


def get_embeddings(
    agent_name: str,
    texts: List[str],
    model: Optional[str] = None,
) -> tuple[List[List[float]], float]:
    """Route embedding call to OpenAI (or Anthropic if supported) based on agents.{agent_name} config.

    Anthropic does not support embeddings; config must use provider: openai for embedding agents.

    Args:
        agent_name: Agent name (e.g. "uniqueness", "rag") for config lookup.
        texts: List of strings to embed.
        model: Override model from config. If None, uses config agents.{agent_name}.model.

    Returns:
        Tuple of (list of embedding vectors, estimated_cost_usd).
    """
    provider, resolved_model = _resolve_provider_and_model(agent_name, model, for_embeddings=True)
    from src.services.openai_service import get_embeddings as openai_embeddings
    return openai_embeddings(texts=texts, model=resolved_model)
