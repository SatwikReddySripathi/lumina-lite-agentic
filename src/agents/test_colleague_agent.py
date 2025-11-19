import os
import time
from dotenv import load_dotenv
from src.graphs.colleague_graph import run_colleague_lookup
from src.core.logging_utils import init_db, log_query
from src.core.cost_utils import calculate_cost

load_dotenv()


def test_colleague_agent():
    """Test the colleague lookup agent with sample queries."""
    
    print("\n" + "="*80)
    print("Testing Colleague Lookup Agent (Feature 2)")
    print("="*80)
    
    init_db()
    
    test_queries = [
        "Who are the data scientists on the Lumina team and where are they located?",
        "Can you find Sarah Chen and tell me her role and location?",
        "List all members of the Digital Workplace AI team with their locations",
        "Who works in Boston on the Lumina team?"
    ]
    
    query = test_queries[0]
    
    print(f"\n Query: {query}")
    print("\n Running agent (this may take 10-15 seconds)...\n")
    
    start_time = time.time()
    
    try:
        result = run_colleague_lookup(query)
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        print("="*80)
        print("TOOL TRACE (Multi-Step Reasoning):")
        print("="*80)
        
        for i, tool_call in enumerate(result["tool_calls"], 1):
            print(f"\n{i}. Tool: {tool_call['tool']}")
            print(f"   Args: {tool_call['args']}")
        
        print("\n" + "="*80)
        print("FINAL ANSWER:")
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
            feature="colleague_lookup",
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
        print("   • Multi-step reasoning (search docs → query database)")
        print("   • Tool orchestration (RAG + structured data)")
        print("   • Enterprise use case (finding colleagues across 300K employees)")
        
        print("\n Try other test queries by modifying test_queries list")
        
    except Exception as e:
        print(f"\n Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_colleague_agent()