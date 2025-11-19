import os
import time
from pathlib import Path
from dotenv import load_dotenv
from src.graphs.image_analysis_graph import run_image_analysis
from src.core.logging_utils import init_db, log_query
from src.core.cost_utils import calculate_cost

load_dotenv()


def test_image_agent():
    """Test the image analysis agent with a sample architecture diagram."""
    
    print("\n" + "="*80)
    print(" Testing Image Analysis Agent (Feature 1)")
    print("="*80)
    
    init_db()
    
    data_dir = Path("data")
    sample_images = list(data_dir.glob("*.png")) + list(data_dir.glob("*.jpg"))
    
    if not sample_images:
        print("\n No sample images found in data/ folder")
        print("Please add an architecture diagram (PNG or JPG) to the data/ folder")
        return
    
    image_path = str(sample_images[0])
    print(f"\n Using image: {image_path}")
    
    test_cases = [
        {
            "question": "Can you provide a comprehensive analysis of this architecture? What are the main components and how do they interact?",
            "focus": "all"
        },
        {
            "question": "What architectural patterns are being used in this diagram? Is this a good design for scale?",
            "focus": "all"
        },
        {
            "question": "What are the security considerations in this architecture?",
            "focus": "security"
        }
    ]
    
    test = test_cases[0]
    
    print(f"\n Question: {test['question']}")
    print(f" Focus: {test['focus']}")
    print("\n Running agent...")
    
    start_time = time.time()
    
    try:
        result = run_image_analysis(
            image_path=image_path,
            question=test['question'],
            focus_areas=test['focus']
        )
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        print("\n" + "="*80)
        print(" TOOL TRACE:")
        print("="*80)
        
        for i, tool_call in enumerate(result["tool_calls"], 1):
            print(f"\n{i}. Tool: {tool_call['tool']}")
            print(f"   Args: {tool_call['args']}")
        
        print("\n" + "="*80)
        print(" FINAL ANSWER:")
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
        print(f"   Latency: {latency_ms}ms")
        print(f"   Tool Calls: {len(result['tool_calls'])}")
        print(f"   Tokens Used: {total_tokens}")
        print(f"   Estimated Cost: ${cost:.4f}")
        
        log_query(
            feature="image_analysis",
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            usage={
                "prompt_tokens": estimated_input,
                "completion_tokens": estimated_output,
                "total_tokens": total_tokens
            },
            latency_ms=latency_ms,
            success=True,
            metadata={
                "image_path": image_path,
                "tool_calls": len(result["tool_calls"]),
                "focus_areas": test['focus']
            }
        )
        
        print("\n Test completed successfully!")
        print("\n To test other questions, modify the test_cases list in this script")
        
    except Exception as e:
        print(f"\n Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_image_agent()