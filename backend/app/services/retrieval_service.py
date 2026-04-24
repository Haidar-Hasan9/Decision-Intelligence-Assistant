import logging
from functools import lru_cache
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from app.config import settings as cfg

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def get_embedding_model():
    """Load and cache the embedding model."""
    return SentenceTransformer(cfg.EMBEDDING_MODEL_NAME)

@lru_cache(maxsize=1)
def get_chroma_collection():
    """Load and cache the Chroma collection."""
    client = chromadb.PersistentClient(path=cfg.CHROMA_PERSIST_DIR)
    return client.get_collection(name="tweets")

def retrieve_tickets(query: str, top_k: int = 5):
    """
    Retrieve top_k similar tickets from Chroma.
    Returns a list of dicts: { 'id': ..., 'document': ..., 'similarity': ... }
    """
    model = get_embedding_model()
    collection = get_chroma_collection()
    query_embedding = model.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=top_k)
    # results['ids'], results['documents'], results['distances'] (Chroma returns distances)
    # Convert distances to similarity (optional)
    tickets = []
    for id, doc, dist in zip(results['ids'][0], results['documents'][0], results['distances'][0]):
        tickets.append({
            "id": id,
            "document": doc,
            "distance": dist,
            "similarity": 1.0 - dist  # if cosine distance is used by Chroma
        })
    return tickets