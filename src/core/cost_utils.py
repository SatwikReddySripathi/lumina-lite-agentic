from typing import Dict

MODEL_PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.150, "output": 0.600},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    "text-embedding-3-small": {"input": 0.02, "output": 0.0},
    "text-embedding-3-large": {"input": 0.13, "output": 0.0},
}


def calculate_cost(model: str, tokens_in: int, tokens_out: int) -> float:

    pricing = MODEL_PRICING.get(model, {"input": 2.50, "output": 10.00})  
    cost = (tokens_in * pricing["input"] / 1_000_000) + \
           (tokens_out * pricing["output"] / 1_000_000)
    return round(cost, 6)


def calculate_embedding_cost(model: str, tokens: int) -> float:
    pricing = MODEL_PRICING.get(model, {"input": 0.02, "output": 0.0})
    return round((tokens * pricing["input"] / 1_000_000), 6)


def project_monthly_cost(
    avg_cost_per_query: float,
    queries_per_user_per_day: int,
    num_users: int
) -> Dict[str, float]:
    """
    Project monthly costs at enterprise scale.
    
    Args:
        avg_cost_per_query: Average cost per query in USD
        queries_per_user_per_day: Expected queries per user daily
        num_users: Number of users
    
    Returns:
        {
            "daily_queries": int,
            "monthly_queries": int,
            "monthly_cost_usd": float,
            "cost_per_user_per_month": float,
            "annual_cost_usd": float
        }
    """
    daily_queries = queries_per_user_per_day * num_users
    monthly_queries = daily_queries * 30
    monthly_cost = monthly_queries * avg_cost_per_query
    
    return {
        "daily_queries": daily_queries,
        "monthly_queries": monthly_queries,
        "monthly_cost_usd": round(monthly_cost, 2),
        "cost_per_user_per_month": round(monthly_cost / num_users, 4),
        "annual_cost_usd": round(monthly_cost * 12, 2)
    }


def estimate_token_count(text: str) -> int:

    return len(text) // 4


def get_cheaper_model_recommendation(query_complexity: str) -> str:

    recommendations = {
        "simple": "gpt-4o-mini",     
        "medium": "gpt-4o",          
        "complex": "gpt-4o"           
    }
    return recommendations.get(query_complexity, "gpt-4o")