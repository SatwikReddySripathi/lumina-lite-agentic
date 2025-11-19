import os
from typing import TypedDict, Annotated, Sequence, List
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import operator

from src.tools.aks_tools import (
    search_internal_aks_kb,
    search_web_for_aks_info,
    suggest_it_forms
)


class SourceReference(BaseModel):
    title: str = Field(description="Title or document ID")
    details: str = Field(description="Brief description or URL")


class DualSourceAnswer(BaseModel):
    
    internal_explanation: str = Field(
        description="Detailed explanation based ONLY on CVS internal documentation. 2-3 paragraphs. Include specific procedures, priority numbers, CVS policies. Use [Internal: DOC-ID] citations."
    )
    internal_sources: List[SourceReference] = Field(
        description="List of internal document references used"
    )
    
    web_explanation: str = Field(
        description="Detailed explanation based ONLY on Azure web documentation. 2-3 paragraphs. Include Microsoft best practices, Azure features. Use [Web: URL] citations."
    )
    web_sources: List[SourceReference] = Field(
        description="List of web references used (with URLs)"
    )
    
    comparison: str = Field(
        description="Compare the two sources. Note similarities and differences. Provide unified recommendation that follows CVS policy."
    )
    
    it_forms: List[str] = Field(
        description="List of relevant IT forms with IDs, names, and when to use them"
    )


class AKSAgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    query: str
    structured_answer: DualSourceAnswer


def create_aks_agent():

    llm_tools = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=0.2,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    llm_structured = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=0.2,
        api_key=os.getenv("OPENAI_API_KEY")
    ).with_structured_output(DualSourceAnswer)
    
    tools = [
        search_internal_aks_kb,
        search_web_for_aks_info,
        suggest_it_forms
    ]
    
    llm_with_tools = llm_tools.bind_tools(tools)
    
    search_prompt = """You are gathering information about AKS networking for CVS Health.

Your task: Search BOTH internal CVS docs AND Azure web documentation.

1. Call search_internal_aks_kb to get CVS-specific information
2. Call search_web_for_aks_info to get Azure best practices
3. Call suggest_it_forms to find relevant forms

After calling all tools, I will format the answer with proper source separation."""

    synthesis_prompt = """You have gathered information from multiple sources. Now create a DUAL-SOURCE answer.

CRITICAL INSTRUCTIONS:

1. **internal_explanation**: Write 2-3 paragraphs explaining ONLY what CVS internal docs say
   - Include specific priority numbers, CVS policies, internal procedures
   - Use inline citations like [Internal: NET-AKS-001]
   - DO NOT include any Azure web information here

2. **web_explanation**: Write 2-3 paragraphs explaining ONLY what Azure docs say
   - Include Microsoft best practices, Azure features
   - Use inline citations like [Web: microsoft.com/...]
   - DO NOT include any CVS internal information here

3. **comparison**: Compare the two sources
   - What's the same?
   - What's different?
   - Which should be followed and why?

4. **it_forms**: List relevant forms with format: "FORM-ID: Name - When to use (SLA: X days)"

REMEMBER: Keep internal and web information completely separate in their respective fields."""

    def search_node(state: AKSAgentState):
        """Search using tools."""
        messages = state["messages"]
        
        if len(messages) == 1:
            messages = [SystemMessage(content=search_prompt)] + messages
        
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def should_continue_search(state: AKSAgentState):
        """Check if we need more tool calls."""
        messages = state["messages"]
        last_message = messages[-1]
        
        if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
            return "synthesize"
        
        return "tools"
    
    def synthesis_node(state: AKSAgentState):
        """Synthesize with structured output."""
        messages = state["messages"]
        
        context_parts = []
        for msg in messages:
            if hasattr(msg, "content") and msg.content:
                context_parts.append(str(msg.content))
        
        full_context = "\n\n".join(context_parts)
        
        synthesis_message = f"""{synthesis_prompt}

USER QUERY: {state['query']}

INFORMATION GATHERED:
{full_context}

Now create the structured dual-source answer."""
        
        structured_answer = llm_structured.invoke([
            SystemMessage(content=synthesis_message)
        ])
        
        return {
            "structured_answer": structured_answer,
            "messages": [AIMessage(content="Synthesis complete")]
        }
    
    workflow = StateGraph(AKSAgentState)
    
    workflow.add_node("search", search_node)
    workflow.add_node("tools", ToolNode(tools))
    workflow.add_node("synthesize", synthesis_node)
    
    workflow.set_entry_point("search")
    
    workflow.add_conditional_edges(
        "search",
        should_continue_search,
        {
            "tools": "tools",
            "synthesize": "synthesize"
        }
    )
    
    workflow.add_edge("tools", "search")
    workflow.add_edge("synthesize", END)
    
    return workflow.compile()


def format_structured_answer(answer: DualSourceAnswer) -> str:
    """Format structured answer into readable markdown."""
    
    output = []
    
    output.append("## From CVS Internal Knowledge Base\n")
    output.append(answer.internal_explanation)
    output.append("\n\n**Internal Sources Used:**")
    for src in answer.internal_sources:
        output.append(f"- {src.title}: {src.details}")
    
    output.append("\n\n---\n")
    
    output.append("## From Azure Documentation (Web)\n")
    output.append(answer.web_explanation)
    output.append("\n\n**Web Sources Used:**")
    for src in answer.web_sources:
        output.append(f"- {src.title}: {src.details}")
    
    output.append("\n\n---\n")
    
    output.append("## Key Differences & Recommendations\n")
    output.append(answer.comparison)
    
    output.append("\n\n---\n")
    
    output.append("## Required IT Forms\n")
    if answer.it_forms:
        for form in answer.it_forms:
            output.append(f"- {form}")
    else:
        output.append("- No specific forms required for this query")
    
    return "\n".join(output)


def run_aks_query(query: str) -> dict:
    """
    Run AKS query with enforced dual-source format.
    """
    agent = create_aks_agent()
    
    result = agent.invoke({
        "messages": [HumanMessage(content=query)],
        "query": query,
        "structured_answer": None
    })
    
    messages = result["messages"]
    structured_answer = result.get("structured_answer")
    
    tool_calls = []
    total_tokens = 0
    
    for msg in messages:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls.append({
                    "tool": tc["name"],
                    "args": tc["args"]
                })
        
        if hasattr(msg, "usage_metadata") and msg.usage_metadata:
            total_tokens += msg.usage_metadata.get("total_tokens", 0)
    
    if structured_answer:
        formatted_answer = format_structured_answer(structured_answer)
    else:
        formatted_answer = "Error: No structured answer generated"
    
    return {
        "answer": formatted_answer,
        "structured_data": structured_answer,
        "tool_calls": tool_calls,
        "tokens_used": total_tokens,
        "full_trace": messages
    }