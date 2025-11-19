import os
import time
from dotenv import load_dotenv
from src.graphs.video_graph import run_video_search
from src.core.logging_utils import init_db, log_query
from src.core.cost_utils import calculate_cost

load_dotenv()


def test_video_agent():
    
    print("\n" + "="*80)
    print("Testing Video Search Agent (Feature 4)")
    print("="*80)
    
    init_db()
    
    test_queries = [
        "How do I deploy an application to AKS using GitHub Actions? Give me step-by-step instructions.",
        "What are the common troubleshooting steps for ImagePullBackOff errors in Kubernetes?",
        "How do I implement health checks and rollback strategies for AKS deployments?",
        "What security best practices should I follow for AKS deployments?"
    ]
    
    query = test_queries[0]
    
    print(f"\n Query: {query}")
    print("\n Running video search agent (10-15 seconds)...")
    print("   • Searching video transcripts semantically")
    print("   • Extracting timestamps for each step")
    print("   • Creating playable video citations\n")
    
    start_time = time.time()
    
    try:
        result = run_video_search(query)
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        print("="*80)
        print("🔧 TOOL TRACE:")
        print("="*80)
        
        for i, tool_call in enumerate(result["tool_calls"], 1):
            print(f"\n{i}. Tool: {tool_call['tool']}")
            print(f"   Args: {tool_call['args']}")
        
        print("\n" + "="*80)
        print(" FINAL ANSWER (With Timestamp Citations):")
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
        
        print("\n Metadata:")
        print(f"   Success: True")
        print(f"   Latency: {latency_ms}ms ({latency_ms/1000:.1f}s)")
        print(f"   Tool Calls: {len(result['tool_calls'])}")
        print(f"   Tokens Used: {total_tokens}")
        print(f"   Estimated Cost: ${cost:.4f}")
        
        log_query(
            feature="video_search",
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
                "query": query
            }
        )
        
        print("\n Test completed successfully!")
        print("\n This agent demonstrates:")
        print("   • Semantic search over video transcripts")
        print("   • Timestamp-based citations")
        print("   • Playable video links with exact moments")
        print("   • Step-by-step instruction extraction")
        print("   • Enterprise use case: 1000s of training videos")
        
        print("\n Try other queries:")
        for i, q in enumerate(test_queries[1:], 2):
            print(f"   {i}. {q}")
        
    except Exception as e:
        print(f"\n Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_video_agent()