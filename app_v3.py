"""
Lumina Lite Agentic - Claude-Style Interface
Sidebar navigation with threaded conversations
"""
import streamlit as st
import os
import time
from dotenv import load_dotenv
from pathlib import Path
import base64
from datetime import datetime

load_dotenv()

# Page config
st.set_page_config(
    page_title="Lumina Lite Agentic",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main {
        background: #ffffff;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: #f7f7f7;
    }
    
    /* Header */
    .header {
        padding: 1.5rem 0 1rem 0;
        border-bottom: 1px solid #e5e5e5;
        margin-bottom: 2rem;
    }
    
    .title {
        font-size: 1.6rem;
        font-weight: 600;
        color: #1a1a1a;
    }
    
    /* Messages */
    .user-message {
        background: #f7f7f7;
        padding: 1rem 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    
    .tool-indicator {
        display: inline-block;
        background: #f0f0f0;
        padding: 0.3rem 0.8rem;
        border-radius: 6px;
        font-size: 0.85rem;
        margin: 0.3rem 0.3rem 0.3rem 0;
        color: #555;
    }
    
    .metadata {
        color: #999;
        font-size: 0.85rem;
        margin-top: 1rem;
        padding-top: 0.8rem;
        border-top: 1px solid #f0f0f0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "threads" not in st.session_state:
    st.session_state.threads = {}
if "current_thread_id" not in st.session_state:
    st.session_state.current_thread_id = None
if "current_feature" not in st.session_state:
    st.session_state.current_feature = None

# Sidebar
with st.sidebar:
    st.markdown("# 🤖 Lumina Lite")
    st.markdown("---")
    
    # New Chat button
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        # Create new thread
        thread_id = f"thread_{len(st.session_state.threads)}_{int(time.time())}"
        st.session_state.threads[thread_id] = {
            "feature": "💬 Ask Me",
            "messages": [],
            "created": datetime.now().strftime("%H:%M"),
            "title": "New conversation"
        }
        st.session_state.current_thread_id = thread_id
        st.session_state.current_feature = "💬 Ask Me"
        st.rerun()
    
    st.markdown("### Features")
    
    # Feature selector as buttons
    features = [
        ("💬", "Ask Me"),
        ("🖼️", "Analyze Image"),
        ("👥", "Colleague Lookup"),
        ("🔍", "AKS Network"),
        ("🎬", "Video Search")
    ]
    
    for icon, name in features:
        full_name = f"{icon} {name}"
        if st.button(f"{icon} {name}", use_container_width=True, key=f"feat_{name}"):
            # Create new thread for this feature
            thread_id = f"thread_{len(st.session_state.threads)}_{int(time.time())}"
            st.session_state.threads[thread_id] = {
                "feature": full_name,
                "messages": [],
                "created": datetime.now().strftime("%H:%M"),
                "title": name
            }
            st.session_state.current_thread_id = thread_id
            st.session_state.current_feature = full_name
            st.rerun()
    
    st.markdown("---")
    st.markdown("### Recent Threads")
    
    # Show recent threads
    if st.session_state.threads:
        for thread_id, thread_data in list(st.session_state.threads.items())[-10:]:
            thread_label = f"{thread_data['title']} ({thread_data['created']})"
            if st.button(thread_label, key=f"thread_{thread_id}", use_container_width=True):
                st.session_state.current_thread_id = thread_id
                st.session_state.current_feature = thread_data['feature']
                st.rerun()

# Main area
if st.session_state.current_thread_id is None:
    # Show welcome screen
    st.markdown('<div class="header"><div class="title">Welcome to Lumina Lite Agentic</div></div>', unsafe_allow_html=True)
    
    st.markdown("## 👋 Get Started")
    st.write("Select a feature from the sidebar to begin:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💬 Ask Me")
        st.write("Learn about the system, features, and architecture")
        
        st.markdown("### 🖼️ Analyze Image")
        st.write("Upload diagrams for GPT-4 Vision analysis")
        
        st.markdown("### 👥 Colleague Lookup")
        st.write("Find team members with multi-tool RAG")
    
    with col2:
        st.markdown("### 🔍 AKS Network")
        st.write("Hybrid search: internal KB + Azure docs")
        
        st.markdown("### 🎬 Video Search")
        st.write("Search videos with timestamp citations")
    
    # Show architecture if available
    arch_path = Path("data/arch.png")
    if arch_path.exists():
        st.markdown("---")
        st.markdown("## 📊 System Architecture")
        st.image(str(arch_path), use_container_width=True)

else:
    # Get current thread
    thread = st.session_state.threads[st.session_state.current_thread_id]
    current_feature = thread["feature"]
    
    # Header
    st.markdown(f'<div class="header"><div class="title">{current_feature}</div></div>', unsafe_allow_html=True)
    
    # Show welcome for Ask Me feature
    if current_feature == "💬 Ask Me" and len(thread["messages"]) == 0:
        st.markdown("## 👋 Welcome to Lumina Lite Agentic")
        st.write("I can answer questions about this system. Try asking:")
        
        example_questions = [
            "How does the colleague lookup agent work?",
            "What's the cost at enterprise scale?",
            "Explain the system architecture",
            "How do I analyze an image/workflow?",
            "What features are available?"
        ]
        
        for q in example_questions:
            st.markdown(f"- *{q}*")
        
        # Show architecture
        arch_path = Path("data/arch.png")
        if arch_path.exists():
            st.markdown("---")
            st.markdown("## 📊 System Architecture")
            st.image(str(arch_path), use_container_width=True)
            
            st.markdown("""
            **Architecture Layers:**
            - **UI Layer:** Streamlit interface + FastAPI backend
            - **Agent Orchestration:** LangGraph manages workflows
            - **Tool Layer:** Vision, search, data query tools
            - **Data Layer:** ChromaDB vectors, SQLite logs
            - **LLM Layer:** GPT-4o + GPT-4 Vision
            """)
    
    # Display messages
    for msg in thread["messages"]:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
        else:
            with st.chat_message("assistant"):
                if "tools" in msg:
                    tools_html = " ".join([f'<span class="tool-indicator">{t}</span>' for t in msg["tools"]])
                    st.markdown(tools_html, unsafe_allow_html=True)
                st.write(msg["content"])
    
    # Input area
    st.markdown("---")
    
    if "💬 Ask Me" in current_feature:
        user_query = st.text_area(
            "Ask me anything:",
            placeholder="e.g., How does image analysis work? What's the cost at scale?",
            height=100,
            key=f"input_{st.session_state.current_thread_id}"
        )
        
        if st.button("Ask", type="primary", use_container_width=True) and user_query:
            # Add user message
            thread["messages"].append({"role": "user", "content": user_query})
            
            # Generate response based on query
            query_lower = user_query.lower()
            
            if "image" in query_lower or "analyze" in query_lower or "workflow" in query_lower:
                response = """
**🖼️ Analyzing Images/Workflows**

To analyze an image or workflow:

1. **Click "🖼️ Analyze Image"** in the sidebar
2. **Upload your file** (PNG, JPG, or PPTX)
3. **Ask a question** like:
   - "Explain this architecture"
   - "What are the main components?"
   - "Summarize the best practices"

**How it works:**
- Uses **GPT-4 Vision** to understand diagrams
- Identifies components, connections, patterns
- Extracts text and annotations
- Provides structured analysis

**Example use cases:**
- Architecture diagrams
- Workflow flowcharts
- System designs
- Presentation slides
                """
            
            elif "cost" in query_lower or "price" in query_lower:
                response = """
**💰 Cost Analysis**

**Development Cost:** $12-15 total

**Per-Query Costs:**
- Simple lookup: ~$0.01
- RAG query: ~$0.015
- Vision analysis: ~$0.02
- Multi-agent: ~$0.025

**Enterprise Scale (300K users):**
- Baseline: $18,000/month
- Optimized: $5,400/month
- **Savings: $151,200/year**

**Optimizations:**
- Smart model routing (47% savings)
- Embedding cache (15% savings)
- Semantic caching (25% savings)
                """
            
            elif "colleague" in query_lower or "lookup" in query_lower:
                response = """
**👥 Colleague Lookup Agent**

**What it does:**
Find team members across CVS Health (300K employees)

**How it works:**
1. Search team documentation (vector search)
2. Query HR database (structured data)
3. Synthesize results with citations

**Example queries:**
- "Who are the data scientists on Lumina team?"
- "Where is Sarah Chen located?"
- "List all engineers in Boston"

**Why it's agentic:**
- Agent decides which tools to call
- Multi-step reasoning
- Combines unstructured + structured data
                """
            
            elif "aks" in query_lower or "network" in query_lower:
                response = """
**🔍 AKS Network Assistant**

**What it does:**
Get help with Azure Kubernetes networking

**Hybrid Search:**
1. **Internal CVS KB** - Company-specific procedures
2. **Azure Documentation** - Microsoft best practices
3. **IT Forms** - ServiceNow tickets to file

**Output format:**
- Section 1: CVS internal policies
- Section 2: Azure recommendations
- Section 3: Comparison & recommendations
- Section 4: Required IT forms

**Example:** NSG rules have CVS-specific priority ordering (100, 200, 300) that differs from Azure's flexible approach.
                """
            
            elif "video" in query_lower:
                response = """
**🎬 Video Search**

**What it does:**
Search training videos with timestamp citations

**How it works:**
1. Semantic search over transcripts
2. Extract step-by-step instructions
3. Link each step to exact timestamp

**Example output:**
- **Step 1:** Set up credentials (at 01:15)
- **Step 2:** Create workflow (at 02:15)
- **Step 3:** Deploy (at 06:25)

**Value:** Jump directly to the relevant moment instead of watching entire 20-min video.
                """
            
            elif "architecture" in query_lower or "how" in query_lower or "work" in query_lower:
                arch_path = Path("data/arch.png")
                if arch_path.exists():
                    response = "**🏗️ System Architecture**\n\nSee diagram above. Key layers:\n\n"
                    response += """
**1. UI Layer:** Streamlit + FastAPI

**2. Agent Orchestration:** LangGraph manages state machines

**3. Tool Layer:**
- Vision tools (GPT-4 Vision)
- Search tools (vector + semantic)
- Data tools (SQL, CSV queries)
- API tools (web search)

**4. Data Layer:**
- ChromaDB for embeddings
- SQLite for logs
- File storage

**5. LLM Layer:**
- GPT-4o for reasoning
- GPT-4 Vision for images
- text-embedding-3-small

**Agent Flow:**
User query → LangGraph → Tool selection → Execution → Synthesis → Response
                    """
                else:
                    response = "**🏗️ System Architecture**\n\nBuilt with LangGraph, GPT-4o, ChromaDB, and Streamlit. Uses agentic workflows for multi-tool orchestration."
            
            elif "feature" in query_lower:
                response = """
**🎯 Available Features**

**1. 💬 Ask Me** - System explainer (you're here!)

**2. 🖼️ Analyze Image** - GPT-4 Vision for diagrams

**3. 👥 Colleague Lookup** - Multi-step RAG

**4. 🔍 AKS Network** - Hybrid search (internal + web)

**5. 🎬 Video Search** - Timestamp citations

**6. 📋 Policy Detector** (Backend) - Change detection

**7. 💰 Cost Analytics** (Backend) - ROI tracking

Click any feature in the sidebar to start a new conversation!
                """
            
            else:
                response = f"""
I can help you understand this system! I'm knowledgeable about:

- **Features:** What each agent does and how it works
- **Architecture:** System design and component interactions
- **Costs:** Development and enterprise scale economics
- **Usage:** How to use each feature

**Popular questions:**
- How does [feature name] work?
- What's the cost at scale?
- Explain the architecture
- How do I analyze an image?

What would you like to know?
                """
            
            thread["messages"].append({
                "role": "assistant",
                "content": response
            })
            st.rerun()
    
    elif "🖼️" in current_feature:
        uploaded_file = st.file_uploader("Upload image or presentation:", type=["png", "jpg", "jpeg", "pptx"], key=f"upload_{st.session_state.current_thread_id}")
        user_query = st.text_area("What would you like to know?", height=100, key=f"q_{st.session_state.current_thread_id}")
        
        if st.button("Analyze", type="primary") and uploaded_file and user_query:
            upload_path = Path("uploads") / uploaded_file.name
            upload_path.parent.mkdir(exist_ok=True)
            with open(upload_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            thread["messages"].append({"role": "user", "content": f"📎 **{uploaded_file.name}**\n\n{user_query}"})
            
            with st.spinner("Analyzing..."):
                from src.graphs.image_analysis_graph import run_image_analysis
                from src.core.cost_utils import calculate_cost
                
                start_time = time.time()
                result = run_image_analysis(str(upload_path), user_query, "all")
                latency_ms = int((time.time() - start_time) * 1000)
                cost = calculate_cost("gpt-4o", int(result["tokens_used"] * 0.6), int(result["tokens_used"] * 0.4))
                
                answer = result["answer"].replace(str(upload_path), "the diagram").replace('uploads\\', '').replace('uploads/', '')
                
                thread["messages"].append({
                    "role": "assistant",
                    "content": answer + f"\n\n*⏱️ {latency_ms}ms • 💰 ${cost:.4f}*",
                    "tools": ["🖼️ GPT-4 Vision"]
                })
            st.rerun()
    
    elif "👥" in current_feature:
        user_query = st.text_area("Ask about team members:", height=100, key=f"q_{st.session_state.current_thread_id}")
        
        if st.button("Search", type="primary") and user_query:
            thread["messages"].append({"role": "user", "content": user_query})
            
            with st.spinner("Searching..."):
                from src.graphs.colleague_graph import run_colleague_lookup
                from src.core.cost_utils import calculate_cost
                
                start_time = time.time()
                result = run_colleague_lookup(user_query)
                latency_ms = int((time.time() - start_time) * 1000)
                cost = calculate_cost("gpt-4o", int(result["tokens_used"] * 0.6), int(result["tokens_used"] * 0.4))
                
                thread["messages"].append({
                    "role": "assistant",
                    "content": result["answer"] + f"\n\n*⏱️ {latency_ms}ms • 💰 ${cost:.4f}*",
                    "tools": ["📚 Team Docs", "👥 HR Database"]
                })
            st.rerun()
    
    elif "🔍" in current_feature:
        user_query = st.text_area("Ask about AKS:", height=100, key=f"q_{st.session_state.current_thread_id}")
        
        if st.button("Search", type="primary") and user_query:
            thread["messages"].append({"role": "user", "content": user_query})
            
            with st.spinner("Searching..."):
                from src.graphs.aks_graph import run_aks_query
                from src.core.cost_utils import calculate_cost
                
                start_time = time.time()
                result = run_aks_query(user_query)
                latency_ms = int((time.time() - start_time) * 1000)
                cost = calculate_cost("gpt-4o", int(result["tokens_used"] * 0.6), int(result["tokens_used"] * 0.4))
                
                thread["messages"].append({
                    "role": "assistant",
                    "content": result["answer"] + f"\n\n*⏱️ {latency_ms}ms • 💰 ${cost:.4f}*",
                    "tools": ["📚 CVS KB", "🌐 Azure Docs", "📋 IT Forms"]
                })
            st.rerun()
    
    elif "🎬" in current_feature:
        user_query = st.text_area("Search videos:", height=100, key=f"q_{st.session_state.current_thread_id}")
        
        if st.button("Search Videos", type="primary") and user_query:
            thread["messages"].append({"role": "user", "content": user_query})
            
            with st.spinner("Searching..."):
                from src.graphs.video_graph import run_video_search
                from src.core.cost_utils import calculate_cost
                
                start_time = time.time()
                result = run_video_search(user_query)
                latency_ms = int((time.time() - start_time) * 1000)
                cost = calculate_cost("gpt-4o", int(result["tokens_used"] * 0.6), int(result["tokens_used"] * 0.4))
                
                thread["messages"].append({
                    "role": "assistant",
                    "content": result["answer"] + f"\n\n*⏱️ {latency_ms}ms • 💰 ${cost:.4f}*",
                    "tools": ["🎬 Transcripts"]
                })
            st.rerun()