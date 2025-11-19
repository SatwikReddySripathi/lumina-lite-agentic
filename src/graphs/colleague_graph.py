
import os
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import operator

from src.tools.search_tools import search_team_documents, search_for_people
from src.tools.data_tools import (
    query_employee_database,
    get_employee_by_name,
    get_team_members,
    get_location_summary
)


class ColleagueAgentState(TypedDict):
    """State for colleague lookup agent."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    query: str
    search_complete: bool


def create_colleague_agent():
    """
    Create LangGraph agent for colleague lookup.
    
    Agent workflow:
    1. Search team documents to identify people
    2. Query HR database for detailed info
    3. Synthesize results with structured output
    
    Returns:
        Compiled LangGraph agent
    """
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=0.1,  
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    tools = [
        search_team_documents,
        search_for_people,
        query_employee_database,
        get_employee_by_name,
        get_team_members,
        get_location_summary
    ]
    
    llm_with_tools = llm.bind_tools(tools)
    
    system_prompt = """You are a colleague lookup assistant for CVS Health.

Your goal is to help users find information about team members, their roles, and locations.

**Your workflow:**
1. First, use search_team_documents or search_for_people to find names and roles from team documentation
2. Then, use query_employee_database or get_employee_by_name to get detailed info (location, email, etc.)
3. Finally, synthesize the information into a clear, structured response

**Output format:**
- Start with a brief summary
- List each person with: Name, Role, Location, Email (if relevant)
- Include a table if multiple people are found
- Cite your sources (team docs, HR database)

**Important:**
- Always verify names from documents with the HR database
- If location/contact info is requested, you MUST query the employee database
- Be concise but complete"""

    def agent_node(state: ColleagueAgentState):
        """Agent reasoning node."""
        messages = state["messages"]
        
        if len(messages) == 1:
            messages = [SystemMessage(content=system_prompt)] + messages
        
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def should_continue(state: ColleagueAgentState):
        """Determine if agent should continue or finish."""
        messages = state["messages"]
        last_message = messages[-1]
        
        if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
            return "end"
        
        return "continue"
    
    workflow = StateGraph(ColleagueAgentState)
    
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


def run_colleague_lookup(query: str) -> dict:
    """
    Run colleague lookup agent.
    
    Args:
        query: User query (e.g., "Who are the data scientists on Lumina team?")
    
    Returns:
        {
            "answer": str,
            "tool_calls": list of tools used,
            "tokens_used": int
        }
    """
    agent = create_colleague_agent()
    
    result = agent.invoke({
        "messages": [HumanMessage(content=query)],
        "query": query,
        "search_complete": False
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