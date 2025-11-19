import os
import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, Optional
from src.core.cost_utils import calculate_cost

LOG_DB_PATH = os.getenv("LOG_DB_PATH", "./logs/queries.db")


def init_db():
    os.makedirs(os.path.dirname(LOG_DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(LOG_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            feature TEXT NOT NULL,
            model TEXT NOT NULL,
            prompt_tokens INTEGER NOT NULL,
            completion_tokens INTEGER NOT NULL,
            total_tokens INTEGER NOT NULL,
            cost_usd REAL NOT NULL,
            latency_ms INTEGER,
            success BOOLEAN NOT NULL,
            error_message TEXT,
            metadata TEXT
        )
    """)
    
    conn.commit()
    conn.close()


def log_query(
    feature: str,
    model: str,
    usage: Dict[str, int],
    latency_ms: int,
    success: bool = True,
    error_message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Log a query with cost tracking.
    
    Args:
        feature: Feature name (e.g., 'file_upload', 'colleague_lookup')
        model: Model used
        usage: Token usage dict with 'prompt_tokens', 'completion_tokens'
        latency_ms: Query latency in milliseconds
        success: Whether query succeeded
        error_message: Error details if failed
        metadata: Additional metadata (tools called, etc.)
    """
    cost = calculate_cost(
        model=model,
        tokens_in=usage.get("prompt_tokens", 0),
        tokens_out=usage.get("completion_tokens", 0)
    )
    
    conn = sqlite3.connect(LOG_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO queries (
            timestamp, feature, model, prompt_tokens, completion_tokens,
            total_tokens, cost_usd, latency_ms, success, error_message, metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.utcnow().isoformat(),
        feature,
        model,
        usage.get("prompt_tokens", 0),
        usage.get("completion_tokens", 0),
        usage.get("total_tokens", 0),
        cost,
        latency_ms,
        success,
        error_message,
        json.dumps(metadata) if metadata else None
    ))
    
    conn.commit()
    conn.close()


def get_cost_summary(feature: Optional[str] = None) -> Dict[str, Any]:
    """
    Get cost summary for all queries or a specific feature.
    
    Args:
        feature: Optional feature name to filter by
    
    Returns:
        {
            "total_queries": int,
            "total_cost_usd": float,
            "avg_cost_per_query": float,
            "total_tokens": int,
            "success_rate": float,
            "by_feature": {...} if feature is None
        }
    """
    conn = sqlite3.connect(LOG_DB_PATH)
    cursor = conn.cursor()
    
    if feature:
        cursor.execute("""
            SELECT COUNT(*), SUM(cost_usd), SUM(total_tokens),
                   SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END)
            FROM queries WHERE feature = ?
        """, (feature,))
    else:
        cursor.execute("""
            SELECT COUNT(*), SUM(cost_usd), SUM(total_tokens),
                   SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END)
            FROM queries
        """)
    
    result = cursor.fetchone()
    total_queries, total_cost, total_tokens, successful = result
    
    summary = {
        "total_queries": total_queries or 0,
        "total_cost_usd": round(total_cost or 0, 4),
        "avg_cost_per_query": round((total_cost or 0) / max(total_queries, 1), 6),
        "total_tokens": total_tokens or 0,
        "success_rate": round((successful or 0) / max(total_queries, 1), 3)
    }
    
    if not feature:
        cursor.execute("""
            SELECT feature, COUNT(*), SUM(cost_usd), AVG(latency_ms)
            FROM queries
            GROUP BY feature
        """)
        by_feature = {}
        for row in cursor.fetchall():
            feat, count, cost, avg_latency = row
            by_feature[feat] = {
                "queries": count,
                "cost_usd": round(cost or 0, 4),
                "avg_latency_ms": round(avg_latency or 0, 1)
            }
        summary["by_feature"] = by_feature
    
    conn.close()
    return summary