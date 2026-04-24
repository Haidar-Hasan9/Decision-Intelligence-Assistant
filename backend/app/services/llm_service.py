import logging
import time
from groq import Groq
from app.config import settings as cfg

logger = logging.getLogger(__name__)

def get_llm_client():
    return Groq(api_key=cfg.GROQ_API_KEY)

def generate_answer_with_rag(query: str, context: str):
    """
    Generate answer using RAG context.
    Returns dict with answer, latency, cost (approximate).
    """
    client = get_llm_client()
    prompt = f"""You are a customer support assistant. Use the following past tickets to answer the user's question.
Past tickets:
{context}

User question: {query}
Answer:"""
    start_time = time.time()
    completion = client.chat.completions.create(
        model=cfg.LLM_MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=500
    )
    latency = (time.time() - start_time) * 1000  # ms
    # Approximate cost: Groq charges per token, but we'll use a rough estimate (e.g., $0.001/1K tokens)
    # Real implementation would use token counts from response.
    token_count = completion.usage.total_tokens
    cost = (token_count / 1000) * 0.001  # hypothetical
    return {
        "answer": completion.choices[0].message.content,
        "latency_ms": round(latency, 2),
        "cost_usd": round(cost, 6)
    }

def generate_answer_no_rag(query: str):
    """
    Generate answer without context.
    """
    client = get_llm_client()
    start_time = time.time()
    completion = client.chat.completions.create(
        model=cfg.LLM_MODEL_NAME,
        messages=[{"role": "user", "content": query}],
        temperature=0.3,
        max_tokens=500
    )
    latency = (time.time() - start_time) * 1000
    token_count = completion.usage.total_tokens
    cost = (token_count / 1000) * 0.001
    return {
        "answer": completion.choices[0].message.content,
        "latency_ms": round(latency, 2),
        "cost_usd": round(cost, 6)
    }

def predict_priority_zero_shot(query: str):
    """
    Use LLM to classify urgency. Returns dict with priority (0/1) and confidence.
    We'll use structured output via a simple prompt.
    """
    client = get_llm_client()
    prompt = f"""Classify the following support ticket as "urgent" or "normal". Respond with only the word "urgent" or "normal".
Ticket: {query}
Classification:"""
    start_time = time.time()
    completion = client.chat.completions.create(
        model=cfg.LLM_MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=5
    )
    latency = (time.time() - start_time) * 1000
    classification = completion.choices[0].message.content.strip().lower()
    priority = 1 if "urgent" in classification else 0
    # For confidence, we can use the token probability of the output token (not always available in simple API)
    # We'll return a placeholder
    return {
        "priority": priority,
        "confidence": 0.9,  # placeholder; in real code, extract logprob
        "latency_ms": round(latency, 2),
        "cost_usd": 0.0   # cost of the short prompt
    }