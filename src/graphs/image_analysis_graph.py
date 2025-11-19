
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import operator
import os

from src.tools.vision_tools import (
    analyze_architecture_diagram,
    compare_architecture_patterns,
    extract_diagram_text
)


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    image_path: str
    focus_areas: str
    analysis_complete: bool


def create_image_analysis_agent():

    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=0.3, 
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    tools = [
        analyze_architecture_diagram,
        compare_architecture_patterns,
        extract_diagram_text
    ]
    
    llm_with_tools = llm.bind_tools(tools)
    
    def agent_node(state: AgentState):
        messages = state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def should_continue(state: AgentState):
        messages = state["messages"]
        last_message = messages[-1]
        
        if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
            return "end"
        
        return "continue"
    
    workflow = StateGraph(AgentState)
    
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(tools))
    
    workflow.set_entry_point("agent")
    
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "tools",
            "end": END
        }
    )
    
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()


def run_image_analysis(
    image_path: str,
    question: str,
    focus_areas: str = "all"
) -> dict:
    """
    Run image analysis agent on an architecture diagram.
    
    Args:
        image_path: Path to diagram image
        question: User's question about the diagram
        focus_areas: What to focus on (all/components/connections/security)
    
    Returns:
        {
            "answer": str,
            "tool_calls": list,
            "tokens_used": int
        }
    """
    agent = create_image_analysis_agent()
    
    initial_message = f"""I have an architecture diagram at: {image_path}

User Question: {question}

Focus Areas: {focus_areas}

Please analyze this diagram and answer the question. Use the available tools:
1. analyze_architecture_diagram - For comprehensive analysis
2. compare_architecture_patterns - For pattern identification
3. extract_diagram_text - For reading labels/text

Start by using the appropriate tool(s) to analyze the diagram."""

    result = agent.invoke({
        "messages": [HumanMessage(content=initial_message)],
        "image_path": image_path,
        "focus_areas": focus_areas,
        "analysis_complete": False
    })
    
    messages = result["messages"]
    tool_calls = []
    total_tokens = 0
    
    for msg in messages:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls.append({
                    "tool": tc["name"],
                    "args": tc["args"]
                })
        if hasattr(msg, "usage_metadata"):
            total_tokens += msg.usage_metadata.get("total_tokens", 0)
    
    final_answer = ""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            if not hasattr(msg, "tool_calls") or not msg.tool_calls:
                final_answer = msg.content
                break
    
    return {
        "answer": final_answer,
        "tool_calls": tool_calls,
        "tokens_used": total_tokens,
        "full_trace": messages
    }