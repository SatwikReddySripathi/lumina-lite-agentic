import base64
from pathlib import Path
from typing import Dict, Any
from langchain_core.tools import tool
from src.core.llm import call_llm_with_vision


def encode_image(image_path: str) -> str:
    """
    Encode image to base64 for API submission.
    
    Args:
        image_path: Path to image file
    
    Returns:
        Base64 encoded string
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


@tool
def analyze_architecture_diagram(image_path: str, focus_areas: str = "all") -> Dict[str, Any]:
    """
    Analyze an architecture diagram using GPT-4 Vision.
    
    Args:
        image_path: Path to the architecture diagram image
        focus_areas: What to focus on: 'all', 'components', 'connections', 'best_practices', 'security'
    
    Returns:
        Structured analysis of the diagram
    """
    base64_image = encode_image(image_path)
    
    ext = Path(image_path).suffix.lower()
    media_type = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"
    
    focus_prompts = {
        "all": "Provide a comprehensive analysis of this architecture diagram.",
        "components": "Identify and describe all components in this architecture diagram.",
        "connections": "Describe how the components are connected and communicate.",
        "best_practices": "Evaluate this architecture against cloud best practices.",
        "security": "Analyze the security aspects of this architecture."
    }
    
    prompt = f"""Analyze this architecture diagram and provide a detailed technical analysis.

Focus: {focus_prompts.get(focus_areas, focus_prompts['all'])}

Provide your analysis in the following structure:

## Overview
Brief description of what this architecture represents.

## Components Identified
List each component/service visible in the diagram with:
- Name/Type
- Purpose
- Technology/Service used

## Architecture Flow
Describe how data/requests flow through the system.

## Connections & Integration
Explain how components communicate (APIs, message queues, direct connections, etc.).

## Best Practices Observed
List architectural best practices being followed.

## Potential Improvements
Suggest 2-3 improvements or considerations.

## Security Considerations
Note any security-related aspects (if visible).

Be specific and reference exact components you see in the diagram."""

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{media_type};base64,{base64_image}",
                        "detail": "high"  
                    }
                }
            ]
        }
    ]
    
    response = call_llm_with_vision(messages=messages, max_tokens=2000)
    
    return {
        "analysis": response["content"],
        "image_path": image_path,
        "focus_areas": focus_areas,
        "tokens_used": response["usage"]["total_tokens"],
        "model": response["model"]
    }


@tool
def compare_architecture_patterns(image_path: str) -> Dict[str, Any]:
    """
    Compare the architecture in the diagram against known patterns.
    
    Args:
        image_path: Path to architecture diagram
    
    Returns:
        Pattern analysis and recommendations
    """
    base64_image = encode_image(image_path)
    ext = Path(image_path).suffix.lower()
    media_type = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"
    
    prompt = """Analyze this architecture diagram and identify which architectural patterns are being used:

1. **Pattern Identification**: Which common patterns do you see?
   - Microservices
   - Event-driven
   - Layered/N-tier
   - Hub-and-spoke
   - Gateway/API Gateway pattern
   - CQRS (if applicable)
   - Circuit breaker (if visible)

2. **Pattern Effectiveness**: How well are these patterns implemented?

3. **Alternative Patterns**: What other patterns could improve this architecture?

4. **Scale Considerations**: How would this architecture handle:
   - High traffic (100K+ requests/sec)
   - Geographic distribution
   - Failover scenarios

Be specific and reference what you see in the diagram."""

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{media_type};base64,{base64_image}",
                        "detail": "high"
                    }
                }
            ]
        }
    ]
    
    response = call_llm_with_vision(messages=messages, max_tokens=1500)
    
    return {
        "pattern_analysis": response["content"],
        "tokens_used": response["usage"]["total_tokens"]
    }


@tool
def extract_diagram_text(image_path: str) -> Dict[str, Any]:
    """
    Extract and identify text labels from architecture diagram.
    
    Args:
        image_path: Path to diagram
    
    Returns:
        All text/labels found in the diagram
    """
    base64_image = encode_image(image_path)
    ext = Path(image_path).suffix.lower()
    media_type = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"
    
    prompt = """Extract ALL text labels, component names, and annotations from this diagram.

List them in a structured format:

**Component Names:**
- [List all service/component names]

**Annotations/Labels:**
- [List all text labels, protocols, ports, etc.]

**Data Flow Labels:**
- [List any labels on arrows/connections]

Be thorough - capture every piece of text visible in the diagram."""

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{media_type};base64,{base64_image}",
                        "detail": "high"
                    }
                }
            ]
        }
    ]
    
    response = call_llm_with_vision(messages=messages, max_tokens=1000)
    
    return {
        "extracted_text": response["content"],
        "tokens_used": response["usage"]["total_tokens"]
    }