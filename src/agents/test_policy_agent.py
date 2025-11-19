import os
import time
from dotenv import load_dotenv
from src.graphs.policy_graph import run_policy_detection
from src.core.logging_utils import init_db, log_query
from src.core.cost_utils import calculate_cost

load_dotenv()


def test_policy_agent():
    
    print("\n" + "="*80)
    print(" Testing Policy Change Detector Agent (Feature 5)")
    print("="*80)
    
    init_db()
    
    print("\n Comparing policy versions:")
    print("   • Old: benefits_policy_v1.md (January 2024)")
    print("   • New: benefits_policy_v2.md (November 2024)")
    print("\n Running change detection agent (10-15 seconds)...")
    print("   • Detecting text-level changes")
    print("   • Analyzing semantic drift")
    print("   • Routing notifications to affected groups\n")
    
    start_time = time.time()
    
    try:
        result = run_policy_detection(
            old_version="benefits_policy_v1.md",
            new_version="benefits_policy_v2.md"
        )
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        print("="*80)
        print(" TOOL TRACE:")
        print("="*80)
        
        for i, tool_call in enumerate(result["tool_calls"], 1):
            print(f"\n{i}. Tool: {tool_call['tool']}")
            args_str = str(tool_call['args'])
            if len(args_str) > 100:
                args_str = args_str[:100] + "..."
            print(f"   Args: {args_str}")
        
        print("\n" + "="*80)
        print(" POLICY CHANGE REPORT:")
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
            feature="policy_change_detection",
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
                "old_version": "benefits_policy_v1.md",
                "new_version": "benefits_policy_v2.md"
            }
        )
        
        print("\n Test completed successfully!")
        print("\n This agent demonstrates:")
        print("   • Automated policy change detection")
        print("   • Semantic drift analysis using embeddings")
        print("   • Intelligent notification routing")
        print("   • Graph-based workflow (detect → analyze → route)")
        print("   • Enterprise use case: Keeping 300K employees compliant")
        
    except Exception as e:
        print(f"\n Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_policy_agent()