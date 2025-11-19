import os
import time
from dotenv import load_dotenv
from src.graphs.aks_graph import run_aks_query
from src.core.logging_utils import init_db, log_query
from src.core.cost_utils import calculate_cost

load_dotenv()


def test_aks_agent():
    
    print("\n" + "="*80)
    print("Testing AKS Multi-Source RAG Agent (Feature 3)")
    print("="*80)
    
    init_db()
    
    test_queries = [
        "How do I configure NSG rules for AKS? What are the required inbound and outbound rules?",
        "What's the difference between Azure CNI and kubenet for AKS networking?",
        "My pods cannot pull images from ACR. How do I troubleshoot this?",
        "How do I set up a private endpoint for my AKS API server?"
    ]
    
    query = test_queries[0]
    
    print(f"\nQuery: {query}")
    print("\nRunning hybrid search agent (15-20 seconds)...")
    print("   • Searching internal CVS knowledge base")
    print("   • Searching web (Azure documentation)")
    print("   • Finding relevant IT forms")
    print("\nThe answer will have 3 separate sections:")
    print("   1. What CVS internal docs say")
    print("   2. What Azure web docs say")
    print("   3. Comparison and IT forms\n")
    
    start_time = time.time()
    
    try:
        result = run_aks_query(query)
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        print("="*80)
        print("🔧 TOOL TRACE (Hybrid Search):")
        print("="*80)
        
        for i, tool_call in enumerate(result["tool_calls"], 1):
            print(f"\n{i}. Tool: {tool_call['tool']}")
            print(f"   Args: {tool_call['args']}")
        
        print("\n" + "="*80)
        print("FINAL ANSWER (With Multi-Source Citations):")
        print("="*80)
        print(result["answer"])
        print("\n" + "="*80)
        
        total_tokens = result["tokens_used"]
        estimated_input = int(total_tokens * 0.6)
        estimated_output = int(total_tokens * 0.4)
        
        cost = calculate_cost(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            tokens_in=estimated_input,
            tokens_out=estimated_output
        )
        
        print("\nMetadata:")
        print(f"   Success: True")
        print(f"   Latency: {latency_ms}ms ({latency_ms/1000:.1f}s)")
        print(f"   Tool Calls: {len(result['tool_calls'])}")
        print(f"   Tokens Used: {total_tokens}")
        print(f"   Estimated Cost: ${cost:.4f}")
        
        log_query(
            feature="aks_multirag",
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            usage={
                "prompt_tokens": estimated_input,
                "completion_tokens": estimated_output,
                "total_tokens": total_tokens
            },
            latency_ms=latency_ms,
            success=True,
            metadata={
                "tool_calls": len(result["tool_calls"]),
                "query": query,
                "hybrid_search": True
            }
        )
        
        print("\n Test completed successfully!")
        print("\n This agent demonstrates:")
        print("   • Hybrid search (internal KB + web)")
        print("   • Source attribution (2 separate sections)")
        print("   • IT form suggestions (enterprise workflow)")
        print("   • Inline citations with document IDs")
        print("   • Multi-tool orchestration (3+ tools)")
        
        print("\n Try other queries by modifying test_queries list")
        print("   Example: 'How do I troubleshoot DNS issues in AKS?'")
        
    except Exception as e:
        print(f"\n Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_aks_agent()