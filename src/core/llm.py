import os
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")


def call_llm(
    messages: list,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 2000,
    **kwargs
) -> Dict[str, Any]:
    """
    Call OpenAI LLM and return response with usage metadata.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        model: Model name (default: from env)
        temperature: Sampling temperature
        max_tokens: Max response tokens
        **kwargs: Additional OpenAI API params
    
    Returns:
        {
            "content": str,
            "usage": {
                "prompt_tokens": int,
                "completion_tokens": int,
                "total_tokens": int
            },
            "model": str
        }
    """
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )
    
    return {
        "content": response.choices[0].message.content,
        "usage": {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        },
        "model": model,
        "finish_reason": response.choices[0].finish_reason
    }


def get_embeddings(texts: list[str], model: str = EMBEDDING_MODEL) -> list[list[float]]:
    """
    Get embeddings for a list of texts.
    
    Args:
        texts: List of strings to embed
        model: Embedding model name
    
    Returns:
        List of embedding vectors
    """
    response = client.embeddings.create(
        model=model,
        input=texts
    )
    return [data.embedding for data in response.data]


def call_llm_with_vision(
    messages: list,
    model: str = "gpt-4o",
    max_tokens: int = 1000
) -> Dict[str, Any]:
    """
    Call OpenAI Vision API for image analysis.
    
    Args:
        messages: Messages with image content
        model: Vision-capable model
        max_tokens: Max response tokens
    
    Returns:
        Same format as call_llm()
    """
    return call_llm(messages=messages, model=model, max_tokens=max_tokens)