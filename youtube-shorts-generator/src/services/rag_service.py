"""
RAG: ChromaDB (local), topic research, embeddings storage, similarity search.
"""
from typing import List, Optional, Tuple
import os

def _chroma_client():
    import chromadb
    from chromadb.config import Settings
    return chromadb.PersistentClient(path="./chroma_db", settings=Settings(anonymized_telemetry=False))


def get_or_create_collection(name: str = "topics"):
    """Get or create a Chroma collection for topics/embeddings."""
    client = _chroma_client()
    return client.get_or_create_collection(name=name, metadata={"description": "Topic embeddings"})


def add_embeddings(ids: List[str], embeddings: List[List[float]], metadatas: Optional[List[dict]] = None) -> None:
    """Store embeddings in Chroma."""
    coll = get_or_create_collection()
    coll.add(ids=ids, embeddings=embeddings, metadatas=metadatas or [])


def similarity_search(
    query_embedding: List[float],
    n_results: int = 5,
    collection_name: str = "topics",
) -> List[Tuple[str, float, Optional[dict]]]:
    """Return list of (id, distance, metadata). Lower distance = more similar."""
    client = _chroma_client()
    coll = client.get_or_create_collection(name=collection_name)
    r = coll.query(query_embeddings=[query_embedding], n_results=n_results, include=["metadatas"])
    ids = r["ids"][0] if r["ids"] else []
    dists = r["distances"][0] if r.get("distances") else []
    metas = (r.get("metadatas") or [[]])[0] if r.get("metadatas") else []
    return list(zip(ids, dists, metas))


def query_topics(query_text: str, n: int = 5) -> List[dict]:
    """Get topic ideas similar to query. Uses OpenAI embeddings + Chroma. Returns list of {id, score, metadata}."""
    from src.services.openai_service import get_embeddings
    emb, _ = get_embeddings([query_text])
    if not emb:
        return []
    results = similarity_search(emb[0], n_results=n)
    return [{"id": rid, "distance": d, "metadata": m} for rid, d, m in results]
