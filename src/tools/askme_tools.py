import os
from pathlib import Path
from typing import Dict, Any, List
from langchain_core.tools import tool
from src.core.llm import call_llm_with_vision
import base64


def _encode_image(image_path: str) -> str:
    """Encode image to base64."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')


def _find_relevant_diagrams(query: str) -> List[Path]:
    """Find relevant architecture diagrams based on query."""
    diagrams_dir = Path("diagrams")
    
    if not diagrams_dir.exists():
        return []
    
    query_lower = query.lower()
    relevant = []
    
    keyword_map = {
        # Feature-specific
        "image analysis": ["feature1_image_analysis.png"],
        "vision": ["feature1_image_analysis.png"],
        "analyze image": ["feature1_image_analysis.png"],
        "gpt-4 vision": ["feature1_image_analysis.png"],
        
        "colleague lookup": ["feature2_colleague_lookup.png"],
        "colleague agent": ["feature2_colleague_lookup.png"],
        "find team": ["feature2_colleague_lookup.png"],
        "multi-step": ["feature2_colleague_lookup.png"],
        
        "aks network": ["feature3_aks_network.png"],
        "aks agent": ["feature3_aks_network.png"],
        "hybrid rag": ["feature3_aks_network.png"],
        "hybrid search": ["feature3_aks_network.png"],
        "dual source": ["feature3_aks_network.png"],
        
        "video search": ["feature4_video_search.png"],
        "video agent": ["feature4_video_search.png"],
        "timestamp": ["feature4_video_search.png"],
        "transcript": ["feature4_video_search.png"],
        
        "policy change": ["feature5_policy_change.png"],
        "policy agent": ["feature5_policy_change.png"],
        "policy detector": ["feature5_policy_change.png"],
        "semantic drift": ["feature5_policy_change.png"],
        
        "cost analytics": ["feature6_cost_analytics.png"],
        "cost agent": ["feature6_cost_analytics.png"],
        "cost tracking": ["feature6_cost_analytics.png"],
        "optimization": ["feature6_cost_analytics.png"],
        
        # General/system-wide
        "main architecture": ["main_architecture.png"],
        "overall system": ["main_architecture.png"],
        "all agents": ["main_architecture.png"],
        "system design": ["main_architecture.png"],
        "langgraph": ["main_architecture.png"],
    }
    
    for keyword, filenames in keyword_map.items():
        if keyword in query_lower:
            for filename in filenames:
                diagram_path = diagrams_dir / filename
                if diagram_path.exists() and diagram_path not in relevant:
                    relevant.append(diagram_path)
    
    if "how does" in query_lower or "how do" in query_lower or "workflow" in query_lower:
        feature_keywords = {
            "image": "feature1_image_analysis.png",
            "colleague": "feature2_colleague_lookup.png",
            "aks": "feature3_aks_network.png",
            "video": "feature4_video_search.png",
            "policy": "feature5_policy_change.png",
            "cost": "feature6_cost_analytics.png"
        }
        
        for keyword, filename in feature_keywords.items():
            if keyword in query_lower:
                diagram_path = diagrams_dir / filename
                if diagram_path.exists() and diagram_path not in relevant:
                    relevant.append(diagram_path)
    
    if not relevant and any(word in query_lower for word in ["architecture", "system", "structure", "design", "layers"]):
        main_arch = diagrams_dir / "main_architecture.png"
        if main_arch.exists():
            relevant.append(main_arch)
    
    return relevant[:3]  


@tool
def explain_with_architecture_diagram(question: str) -> Dict[str, Any]:
    """
    Explain system features using architecture diagrams.
    
    Args:
        question: User question about the system
    
    Returns:
        Answer with diagram context
    """
    relevant_diagrams = _find_relevant_diagrams(question)
    
    if not relevant_diagrams:
        return {
            "answer": "No architecture diagrams found. Please ensure diagrams are in the 'diagrams/' folder.",
            "diagrams_used": []
        }
    
    diagram_contents = []
    for diagram_path in relevant_diagrams:
        diagram_contents.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{_encode_image(str(diagram_path))}",
                "detail": "high"
            }
        })
    
    prompt = f"""You are explaining the Lumina Lite Agentic system using architecture diagrams.

User Question: {question}

Architecture diagrams have been provided showing the system design and workflows.

**Instructions:**
1. **Reference the diagram(s)** - Say things like "As shown in the diagram...", "Following the arrows...", "The green connections indicate..."
2. **Describe the flow** - Explain what happens step-by-step using the visual flow in the diagram
3. **Identify components** - Point out specific boxes, layers, or elements visible
4. **Explain interactions** - Describe how components connect (follow the colored arrows)
5. **Be specific** - Reference colors, positions, layers from the actual diagram

**Example good response:**
"The Colleague Lookup Agent workflow, shown in the diagram with green arrows, follows a multi-step process. Starting from the user query at the top, the agent first calls the search_team_documents tool (first green box), which queries ChromaDB. Then, following the second green arrow, it calls query_employee_database to get location data from the CSV. These results flow (orange arrows) into the Agent Synthesis component, which combines them into the final structured answer."

**Your task:**
Answer the user's question by walking through the relevant diagram(s). Make it visual and specific."""

    content = [{"type": "text", "text": prompt}] + diagram_contents
    
    messages = [
        {
            "role": "user",
            "content": content
        }
    ]
    
    response = call_llm_with_vision(messages=messages, max_tokens=1500)
    
    return {
        "answer": response["content"],
        "diagrams_used": [str(p.name) for p in relevant_diagrams],
        "tokens_used": response["usage"]["total_tokens"]
    }


@tool
def get_performance_metrics() -> Dict[str, Any]:
    """
    Get consolidated performance metrics across all features.
    
    Returns:
        Performance data from query logs
    """
    from src.core.logging_utils import get_cost_summary
    import sqlite3
    from pathlib import Path
    
    log_db = Path("./logs/queries.db")
    
    if not log_db.exists():
        return {
            "error": "No metrics available. Run some queries first to generate data."
        }
    
    overall = get_cost_summary()
    
    conn = sqlite3.connect(log_db)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            feature,
            COUNT(*) as total_queries,
            AVG(latency_ms) as avg_latency,
            MIN(latency_ms) as min_latency,
            MAX(latency_ms) as max_latency,
            AVG(total_tokens) as avg_tokens,
            AVG(cost_usd) as avg_cost,
            SUM(cost_usd) as total_cost,
            SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate
        FROM queries
        GROUP BY feature
    """)
    
    features = []
    for row in cursor.fetchall():
        feature, queries, avg_lat, min_lat, max_lat, avg_tok, avg_cost, total_cost, success = row
        features.append({
            "feature": feature,
            "total_queries": queries,
            "avg_latency_ms": round(avg_lat or 0, 1),
            "min_latency_ms": round(min_lat or 0, 1),
            "max_latency_ms": round(max_lat or 0, 1),
            "avg_tokens": round(avg_tok or 0, 0),
            "avg_cost_usd": round(avg_cost or 0, 6),
            "total_cost_usd": round(total_cost or 0, 4),
            "success_rate": round(success or 0, 1)
        })
    
    conn.close()
    
    return {
        "overall": overall,
        "by_feature": features
    }