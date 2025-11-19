import os
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import operator

from src.tools.askme_tools import explain_with_architecture_diagram, get_performance_metrics


class AskMeAgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    query: str


def create_askme_agent():

    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    tools = [
        explain_with_architecture_diagram,
        get_performance_metrics
    ]
    
    llm_with_tools = llm.bind_tools(tools)
    
    system_prompt = """You are an AI assistant explaining the Lumina Lite Agentic system.

**You have access to these tools:**

1. **explain_with_architecture_diagram** - ALWAYS use this when users ask about:
   - "How does [feature] work?"
   - "Explain [agent] workflow"
   - "Show me the architecture"
   - "What's the flow for [feature]?"
   - Any question about system design, workflows, or agent behavior
   
   This tool has access to 7 architecture diagrams:
   - Main system architecture (all 6 agents)
   - Feature 1: Image Analysis Agent workflow
   - Feature 2: Colleague Lookup Agent workflow
   - Feature 3: AKS Network Agent workflow (hybrid RAG)
   - Feature 4: Video Search Agent workflow
   - Feature 5: Policy Change Detector workflow
   - Feature 6: Cost Analytics Agent workflow
   
   The tool will automatically select the most relevant diagram(s) based on the question.

2. **get_performance_metrics** - Use when users ask about:
   - "What are the metrics?"
   - "Performance stats"
   - "Cost breakdown"
   - "Latency data"
   - "How fast is [feature]?"

**Decision Logic:**
- Question about HOW something works → use explain_with_architecture_diagram
- Question about architecture/design/workflow → use explain_with_architecture_diagram
- Question about performance/cost/metrics → use get_performance_metrics
- General questions → answer directly

**System Knowledge:**
6 agentic workflows: Image Analysis, Colleague Lookup, AKS Network, Video Search, Policy Change, Cost Analytics.
Built with LangGraph + GPT-4o. Cost: $12 dev, $5.4K/month at 300K users (optimized).

IMPORTANT: When explaining workflows, ALWAYS use the diagram tool so users can see the visual flow."""

    def agent_node(state: AskMeAgentState):
        messages = state["messages"]
        
        if len(messages) == 1:
            messages = [SystemMessage(content=system_prompt)] + messages
        
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def should_continue(state: AskMeAgentState):
        messages = state["messages"]
        last_message = messages[-1]
        
        if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
            return "end"
        
        return "continue"
    
    workflow = StateGraph(AskMeAgentState)
    
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


def run_askme_query(query: str) -> dict:
    """
    Run Ask Me query with diagram access.
    
    Args:
        query: User question about the system
    
    Returns:
        Answer with optional diagrams and metrics
    """
    agent = create_askme_agent()
    
    result = agent.invoke({
        "messages": [HumanMessage(content=query)],
        "query": query
    })
    
    messages = result["messages"]
    
    tool_calls = []
    diagrams_used = []
    total_tokens = 0
    
    for msg in messages:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls.append({
                    "tool": tc["name"],
                    "args": tc["args"]
                })
        
        if hasattr(msg, "content") and isinstance(msg.content, str):
            if "diagrams_used" in msg.content:
                try:
                    import json
                    if msg.content.startswith("{"):
                        result_data = json.loads(msg.content)
                        diagrams_used.extend(result_data.get("diagrams_used", []))
                except:
                    pass
        
        if hasattr(msg, "usage_metadata") and msg.usage_metadata:
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
        "diagrams_used": diagrams_used,
        "tokens_used": total_tokens,
        "full_trace": messages
    }