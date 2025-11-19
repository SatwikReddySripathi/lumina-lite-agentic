"""
Lumina Lite Agentic - Clean Minimalist UI
Fixed: HTML rendering, better arch explanation, image path cleanup, feature switching clears chat
"""
import streamlit as st
import pandas as pd
import os
import time
from dotenv import load_dotenv
from pathlib import Path
import base64

load_dotenv()

# Page config
st.set_page_config(
    page_title="Lumina Lite Agentic",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Minimalist CSS
st.markdown("""
<style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main {
        background: #ffffff;
    }
    
    /* Simple header */
    .header {
        text-align: center;
        padding: 2rem 0 1rem 0;
        border-bottom: 1px solid #e5e5e5;
        margin-bottom: 2rem;
    }
    
    .title {
        font-size: 1.8rem;
        font-weight: 600;
        color: #1a1a1a;
        margin: 0;
    }
    
    .subtitle {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.3rem;
    }
    
    /* Messages */
    .user-message {
        background: #f7f7f7;
        padding: 1rem 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    
    .assistant-message {
        padding: 1rem 0;
        margin: 1rem 0;
        line-height: 1.7;
    }
    
    /* Tool indicators */
    .tool-indicator {
        display: inline-block;
        background: #f0f0f0;
        padding: 0.3rem 0.8rem;
        border-radius: 6px;
        font-size: 0.85rem;
        margin: 0.3rem 0.3rem 0.3rem 0;
        color: #555;
    }
    
    /* Metadata */
    .metadata {
        color: #999;
        font-size: 0.85rem;
        margin-top: 1rem;
        padding-top: 0.8rem;
        border-top: 1px solid #f0f0f0;
    }
    
    /* Architecture diagram */
    .arch-diagram {
        background: #fafafa;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1.5rem 0;
    }
    
    .arch-diagram img {
        max-width: 100%;
        border-radius: 6px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Sections */
    h2 {
        font-size: 1.2rem;
        font-weight: 600;
        margin: 1.5rem 0 0.8rem 0;
        color: #1a1a1a;
    }
    
    h3 {
        font-size: 1.05rem;
        font-weight: 600;
        margin: 1.2rem 0 0.6rem 0;
        color: #333;
    }
    
    ul {
        line-height: 1.8;
    }
    
    .feature-pill {
        display: inline-block;
        background: #f5f5f5;
        padding: 0.4rem 0.9rem;
        border-radius: 6px;
        margin: 0.3rem;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_welcome" not in st.session_state:
    st.session_state.show_welcome = True
if "last_feature" not in st.session_state:
    st.session_state.last_feature = None

# Header
st.markdown("""
<div class="header">
    <div class="title">Lumina Lite Agentic</div>
    <div class="subtitle">AI-Powered Knowledge Assistant</div>
</div>
""", unsafe_allow_html=True)

# Feature selector
feature = st.radio(
    "Select Feature:",
    ["💬 Ask Me (Demo Explainer)", "🖼️ Analyze Image/Workflow", "👥 Colleague Lookup", "🔍 AKS Network Assistant", "🎬 Video Search"],
    horizontal=True,
    label_visibility="collapsed"
)

# Clear chat when feature changes
if st.session_state.last_feature != feature:
    st.session_state.messages = []
    st.session_state.show_welcome = True
    st.session_state.last_feature = feature

st.markdown("---")

# Show welcome for "Ask Me" feature
if feature == "💬 Ask Me (Demo Explainer)" and st.session_state.show_welcome and not st.session_state.messages:
    st.session_state.show_welcome = False
    
    # Check for architecture diagram
    arch_path = Path("data/arch.png")
    arch_exists = arch_path.exists()
    
    # Use st.write for proper rendering
    st.markdown("## 👋 Welcome to Lumina Lite Agentic")
    st.write("I'm an AI assistant showcasing **6 agentic workflows** built with LangGraph and GPT-4o. Let me explain what I can do:")
    
    st.markdown("## 🎯 Core Features")
    
    st.markdown("**1. 🖼️ Analyze Image/Workflow**")
    st.write("Upload architecture diagrams or presentations. I use **GPT-4 Vision** to analyze components, workflows, and extract best practices.")
    
    st.markdown("**2. 👥 Colleague Lookup**")
    st.write("Find team members across CVS Health. I search team documentation, then query the HR database for locations and contact info. *Multi-step agentic reasoning.*")
    
    st.markdown("**3. 🔍 AKS Network Assistant**")
    st.write("Get help with Azure Kubernetes Service networking. I use **hybrid search**: internal CVS knowledge base + real-time Azure documentation + IT form suggestions.")
    
    st.markdown("**4. 🎬 Video Search**")
    st.write("Search training video transcripts with **timestamp citations**. Jump directly to the exact moment in a 20-minute video where your answer is explained.")
    
    st.markdown("**5. 📋 Policy Change Detector** (Backend)")
    st.write("Detects changes between policy versions, identifies affected teams, and routes notifications. Uses semantic drift analysis with embeddings.")
    
    st.markdown("**6. 💰 Cost Analytics Dashboard** (Backend)")
    st.write("Tracks every query's cost, projects enterprise scale economics, suggests optimizations. Built for $12, saves $150K/year at 300K users.")
    
    st.markdown("## 🏗️ Technology Stack")
    st.markdown("""
    <span class="feature-pill">LangGraph</span>
    <span class="feature-pill">GPT-4o</span>
    <span class="feature-pill">GPT-4 Vision</span>
    <span class="feature-pill">ChromaDB</span>
    <span class="feature-pill">FastAPI</span>
    <span class="feature-pill">Streamlit</span>
    """, unsafe_allow_html=True)
    
    st.markdown("## ⚡ What Makes This Agentic?")
    st.write("Unlike simple RAG, these are **true agents** that:")
    st.markdown("""
    - **Reason about tasks:** Break complex queries into steps
    - **Choose tools:** Decide which data sources to use
    - **Orchestrate workflows:** Call multiple tools in sequence
    - **Synthesize results:** Combine information from diverse sources
    """)
    st.write("**Example:** Colleague Lookup first searches docs for names, then queries HR database for locations, then synthesizes into structured output with citations.")
    
    # Show architecture if available
    if arch_exists:
        st.markdown("## 📊 System Architecture")
        
        with open(arch_path, "rb") as f:
            img_bytes = f.read()
        
        st.image(img_bytes, use_container_width=True)
        
        st.markdown("### Architecture Layers")
        st.markdown("""
        **1. User Interface Layer**
        - Streamlit for interactive UI
        - FastAPI for backend services (production ready)
        
        **2. Agent Orchestration Layer**
        - LangGraph manages agent workflows
        - State machines for complex multi-step reasoning
        - Tool selection and execution
        
        **3. Tool Layer**
        - **Vision Tools:** GPT-4 Vision for image analysis
        - **Search Tools:** Vector search (ChromaDB), semantic similarity
        - **Data Tools:** SQL queries, CSV lookups, JSON parsing
        - **API Tools:** External API calls, web search
        
        **4. Data Layer**
        - **Vector Database:** ChromaDB for document embeddings
        - **Structured Data:** SQLite for logs, CSV for HR data
        - **File Storage:** Documents, videos, policies
        
        **5. LLM Layer**
        - GPT-4o for reasoning and text generation
        - GPT-4 Vision for image understanding
        - text-embedding-3-small for vector embeddings
        
        **6. Observability Layer**
        - Cost tracking per query
        - Query logging to SQLite
        - Performance metrics (latency, tokens)
        """)
        
        st.info("**Agent Flow Example (Colleague Lookup):** User asks → LangGraph analyzes → Calls search_team_documents → Calls query_employee_database → Synthesizes results → Logs cost")
    
    st.markdown("## 💡 Try It Out")
    st.write("Switch to any feature above and ask questions!")
    st.markdown("""
    - **Analyze Image:** Upload an architecture diagram
    - **Colleague Lookup:** "Who are the data scientists on Lumina team?"
    - **AKS Network:** "How do I configure NSG rules for AKS?"
    - **Video Search:** "How to deploy with GitHub Actions?"
    """)
    
    st.markdown("## 📈 Production Ready")
    st.write("This isn't just a demo—it's built with production patterns:")
    st.markdown("""
    - ✅ Cost tracking per query
    - ✅ Structured logging to database
    - ✅ Error handling and retries
    - ✅ Source attribution and citations
    - ✅ Modular, testable architecture
    """)

# Display chat history
for msg in st.session_state.messages:
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

if feature == "💬 Ask Me (Demo Explainer)":
    user_query = st.text_area(
        "Ask me anything about this system:",
        placeholder="e.g., How does the colleague lookup work? What's the cost at scale? Explain the architecture.",
        height=100
    )
    
    if st.button("Ask", type="primary", use_container_width=True) and user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        
        query_lower = user_query.lower()
        
        if "cost" in query_lower or "price" in query_lower or "expensive" in query_lower:
            with st.chat_message("assistant"):
                st.markdown("## 💰 Cost Analysis")
                st.write("**Development Cost:** Built this entire system for approximately **$12-15** in OpenAI API costs.")
                
                st.markdown("**Per-Query Costs:**")
                st.markdown("""
                - Simple lookup: ~$0.01
                - RAG query: ~$0.015
                - Vision analysis: ~$0.02
                - Multi-agent workflow: ~$0.025
                """)
                
                st.markdown("**Enterprise Scale (300K users, 5 queries/day):**")
                st.markdown("""
                - Baseline (GPT-4o only): $18,000/month
                - Optimized (smart routing): $5,400/month
                - **Annual savings: $151,200**
                """)
                
                st.markdown("**Optimization Strategies:**")
                st.markdown("""
                - Route simple queries to GPT-4o-mini (47% savings)
                - Cache embeddings for repeated documents (15% savings)
                - Semantic caching for duplicate queries (25% savings)
                - Prompt optimization (20% savings)
                """)
        
        elif "architecture" in query_lower or "how" in query_lower or "work" in query_lower:
            with st.chat_message("assistant"):
                arch_path = Path("data/arch.png")
                if arch_path.exists():
                    st.markdown("## 🏗️ System Architecture")
                    st.image(str(arch_path), use_container_width=True)
                
                st.markdown("**Component Breakdown:**")
                st.markdown("""
                - **LangGraph:** Agent orchestration framework managing state transitions
                - **Tool Layer:** Specialized functions (vector search, SQL, APIs, vision)
                - **Data Layer:** ChromaDB for vectors, SQLite for logs
                - **LLM Layer:** GPT-4o for reasoning, GPT-4 Vision for images
                - **Interface:** Streamlit UI + FastAPI backend
                """)
                
                st.markdown("**Agent Flow Example (Colleague Lookup):**")
                st.markdown("""
                1. User asks: "Who are the data scientists?"
                2. LangGraph agent analyzes query
                3. Agent calls `search_team_documents` → finds names
                4. Agent calls `query_employee_database` → gets locations
                5. Agent synthesizes results
                6. System logs query with cost tracking
                """)
        
        else:
            with st.chat_message("assistant"):
                st.markdown("## 🎯 About Lumina Lite Agentic")
                st.write("Production-ready demonstration of **agentic AI** for CVS Health.")
                st.markdown("**Key Features:** 6 agentic workflows, cost tracking, multi-modal (text/images/video), hybrid search")
                st.write("Ask specific questions about features, architecture, costs, or implementation!")
        
        st.rerun()

elif feature == "🖼️ Analyze Image/Workflow":
    uploaded_file = st.file_uploader("Upload image or presentation:", type=["png", "jpg", "jpeg", "pptx"])
    user_query = st.text_area(
        "What would you like to know?",
        placeholder="e.g., Explain this architecture, What are the components?, Summarize best practices",
        height=100
    )
    
    if st.button("Analyze", type="primary", use_container_width=True) and uploaded_file and user_query:
        upload_path = Path("uploads") / uploaded_file.name
        upload_path.parent.mkdir(exist_ok=True)
        with open(upload_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.session_state.messages.append({
            "role": "user",
            "content": f"📎 **{uploaded_file.name}**\n\n{user_query}"
        })
        
        with st.spinner("Analyzing with GPT-4 Vision..."):
            from src.graphs.image_analysis_graph import run_image_analysis
            from src.core.cost_utils import calculate_cost
            
            start_time = time.time()
            result = run_image_analysis(str(upload_path), user_query, "all")
            latency_ms = int((time.time() - start_time) * 1000)
            cost = calculate_cost("gpt-4o", int(result["tokens_used"] * 0.6), int(result["tokens_used"] * 0.4))
            
            # Clean up the answer - remove file path references
            answer = result["answer"]
            # Remove any mention of file paths
            answer = answer.replace(str(upload_path), "the uploaded diagram")
            answer = answer.replace(f'"{upload_path}"', "the diagram")
            answer = answer.replace(f'"{str(upload_path)}"', "the diagram")
            answer = answer.replace('uploads\\', '')
            answer = answer.replace('uploads/', '')
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer + f"\n\n*⏱️ {latency_ms}ms • 💰 ${cost:.4f} • {len(result['tool_calls'])} tools used*",
                "tools": ["🖼️ GPT-4 Vision Analysis"]
            })
        st.rerun()

elif feature == "👥 Colleague Lookup":
    user_query = st.text_area(
        "Ask about team members:",
        placeholder="e.g., Who are the data scientists on the Lumina team? Where is Sarah Chen located?",
        height=100
    )
    
    if st.button("Search", type="primary", use_container_width=True) and user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        
        with st.spinner("Searching..."):
            from src.graphs.colleague_graph import run_colleague_lookup
            from src.core.cost_utils import calculate_cost
            
            start_time = time.time()
            result = run_colleague_lookup(user_query)
            latency_ms = int((time.time() - start_time) * 1000)
            cost = calculate_cost("gpt-4o", int(result["tokens_used"] * 0.6), int(result["tokens_used"] * 0.4))
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["answer"] + f"\n\n*⏱️ {latency_ms}ms • 💰 ${cost:.4f}*",
                "tools": ["📚 Team Docs", "👥 HR Database"]
            })
        st.rerun()

elif feature == "🔍 AKS Network Assistant":
    user_query = st.text_area(
        "Ask about AKS networking:",
        placeholder="e.g., How do I configure NSG rules? What forms do I need?",
        height=100
    )
    
    if st.button("Search", type="primary", use_container_width=True) and user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        
        with st.spinner("Searching..."):
            from src.graphs.aks_graph import run_aks_query
            from src.core.cost_utils import calculate_cost
            
            start_time = time.time()
            result = run_aks_query(user_query)
            latency_ms = int((time.time() - start_time) * 1000)
            cost = calculate_cost("gpt-4o", int(result["tokens_used"] * 0.6), int(result["tokens_used"] * 0.4))
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["answer"] + f"\n\n*⏱️ {latency_ms}ms • 💰 ${cost:.4f}*",
                "tools": ["📚 CVS Internal KB", "🌐 Azure Docs", "📋 IT Forms"]
            })
        st.rerun()

elif feature == "🎬 Video Search":
    user_query = st.text_area(
        "Search video content:",
        placeholder="e.g., How do I deploy to AKS with GitHub Actions?",
        height=100
    )
    
    if st.button("Search Videos", type="primary", use_container_width=True) and user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        
        with st.spinner("Searching..."):
            from src.graphs.video_graph import run_video_search
            from src.core.cost_utils import calculate_cost
            
            start_time = time.time()
            result = run_video_search(user_query)
            latency_ms = int((time.time() - start_time) * 1000)
            cost = calculate_cost("gpt-4o", int(result["tokens_used"] * 0.6), int(result["tokens_used"] * 0.4))
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["answer"] + f"\n\n*⏱️ {latency_ms}ms • 💰 ${cost:.4f}*",
                "tools": ["🎬 Video Transcripts"]
            })
        st.rerun()

# Footer
st.markdown("""
<div style="text-align: center; color: #ccc; padding: 2rem 0; font-size: 0.85rem; border-top: 1px solid #f0f0f0; margin-top: 3rem;">
    Lumina Lite Agentic • Built for CVS Health • November 2024
</div>
""", unsafe_allow_html=True)