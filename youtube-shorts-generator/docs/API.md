# Service API Reference

Short reference for service entry points used by youtube-shorts-generator.

## OpenAI service (`src/services/openai_service.py`)

Uses OpenAI Chat Completions and Embeddings APIs with retry, model fallback on 403, and cost tracking.

### Environment

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | Required. API key for OpenAI. |
| `OPENAI_CHAT_MODEL` | Default chat model (e.g. `gpt-4.1`). |
| `OPENAI_FALLBACK_CHAT_MODEL` | Comma-separated fallbacks if default returns 403. |
| `OPENAI_EMBEDDING_MODEL` | Default embedding model (e.g. `text-embedding-3-small`). |
| `OPENAI_FALLBACK_EMBEDDING_MODEL` | Comma-separated fallbacks for embeddings on 403. |

### Entry points

- **`chat_completion(messages, model=None, temperature=0.7)`**  
  Calls `/v1/chat/completions`. Returns `(content: str, cost_usd: float)`. Uses default then fallback models on model access errors; retries on transient errors.

- **`get_embeddings(texts, model=None)`**  
  Calls embeddings API. Returns `(vectors: list[list[float]], cost_usd: float)`. Same fallback and retry behavior.

See docstrings in `openai_service.py` for Args, Returns, and Raises.
