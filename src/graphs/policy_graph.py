import os
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import operator

from src.tools.policy_tools import (
    compare_policy_versions,
    detect_semantic_drift,
    route_notifications,
    summarize_policy_changes
)


class PolicyAgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    old_version: str
    new_version: str


def create_policy_agent():

    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=0.1,  
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    tools = [
        compare_policy_versions,
        detect_semantic_drift,
        route_notifications,
        summarize_policy_changes
    ]
    
    llm_with_tools = llm.bind_tools(tools)
    
    system_prompt = """You are a policy change detection assistant for CVS Health.

**Your workflow:**
1. Compare old and new policy versions to detect changes
2. Summarize the key changes in plain English
3. Route notifications to affected employee groups
4. Provide actionable recommendations

**Output format:**

## Change Detection Summary

[High-level overview of what changed]

## Detailed Changes

**Section: [Name]**
- Added: [specific change]
- Removed: [specific change]
- Modified: [specific change]

**Section: [Name]**
- [changes...]

## Notification Plan

**Critical Priority:**
- [Group name] via [channel] - [reason]

**High Priority:**
- [Group name] via [channel] - [reason]

**Medium Priority:**
- [Group name] via [channel] - [reason]

## Recommendations

1. [Action item for HR team]
2. [Communication strategy suggestion]
3. [Timeline recommendation]

**Important:**
- Focus on changes that impact employees' benefits or obligations
- Use clear, non-technical language
- Highlight financial impacts (e.g., "Company match increased from 3% to 4.5%")
- Be specific about who is affected and how"""

    def agent_node(state: PolicyAgentState):
        messages = state["messages"]
        
        if len(messages) == 1:
            messages = [SystemMessage(content=system_prompt)] + messages
        
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def should_continue(state: PolicyAgentState):
        messages = state["messages"]
        last_message = messages[-1]
        
        if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
            return "end"
        
        return "continue"
    
    workflow = StateGraph(PolicyAgentState)
    
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


def run_policy_detection(old_version: str, new_version: str) -> dict:
    """
    Run policy change detection.
    
    Args:
        old_version: Old policy filename
        new_version: New policy filename
    
    Returns:
        {
            "answer": Formatted change report,
            "tool_calls": Tools used,
            "tokens_used": Total tokens
        }
    """
    agent = create_policy_agent()
    
    query = f"Analyze the policy changes between {old_version} and {new_version}. Identify what changed, who needs to be notified, and provide recommendations."
    
    result = agent.invoke({
        "messages": [HumanMessage(content=query)],
        "old_version": old_version,
        "new_version": new_version
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
        "tokens_used": total_tokens,
        "full_trace": messages
    }