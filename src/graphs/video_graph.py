import os
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import operator

from src.tools.video_tools import (
    search_video_transcripts,
    get_video_summary,
    search_by_speaker
)


class VideoAgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    query: str


def create_video_agent():

    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=0.3,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    tools = [
        search_video_transcripts,
        get_video_summary,
        search_by_speaker
    ]
    
    llm_with_tools = llm.bind_tools(tools)
    
    system_prompt = """You are a video content assistant for CVS Health's training library.

**Your task:**
Help users find relevant information in video transcripts with exact timestamps.

**Workflow:**
1. Use search_video_transcripts to find relevant segments
2. Extract step-by-step instructions from the transcript text
3. Include EXACT timestamps for each step
4. Create "video cards" with clickable links

**Output format:**

## Answer
[Brief summary of what you found]

## Step-by-Step Instructions
1. **[Step title]** (at [timestamp])
   - [Detailed instruction from transcript]
   - Video: [title]
   
2. **[Next step]** (at [timestamp])
   - [Instruction]
   - Video: [title]

## Video References

**[Video Title]**
- Speaker: [name]
- Duration: [time]
- [Watch Video]([url])
- Relevant Timestamps:
  - [00:00] - [description]
  - [00:00] - [description]

**Important:**
- ALWAYS include exact timestamps in format [MM:SS]
- Link timestamps to video URLs like: [url]?t=[seconds]
- Create a "video card" for each unique video found
- Extract actionable steps, not just descriptions"""

    def agent_node(state: VideoAgentState):
        messages = state["messages"]
        
        if len(messages) == 1:
            messages = [SystemMessage(content=system_prompt)] + messages
        
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def should_continue(state: VideoAgentState):
        messages = state["messages"]
        last_message = messages[-1]
        
        if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
            return "end"
        
        return "continue"
    
    workflow = StateGraph(VideoAgentState)
    
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


def run_video_search(query: str) -> dict:
    
    agent = create_video_agent()
    
    result = agent.invoke({
        "messages": [HumanMessage(content=query)],
        "query": query
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