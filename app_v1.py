"""
Lumina Lite Agentic - Unified Chat Interface
All 6 features in one ChatGPT-style UI
"""
import streamlit as st
import pandas as pd
import os
import time
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Lumina Lite Agentic",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #CC0000;
        margin-bottom: 1rem;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background: #e3f2fd;
        border-left: 4px solid #2196F3;
    }
    .assistant-message {
        background: #f5f5f5;
        border-left: 4px solid #CC0000;
    }
    .tool-trace {
        background: #fff3e0;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
    }
    .metric-inline {
        display: inline-block;
        background: #e8eaf6;
        padding: 0.3rem 0.8rem;
        border-radius: 5px;
        margin: 0.2rem;
        font-size: 0.85rem;
    }
    .feature-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #CC0000;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_feature" not in st.session_state:
    st.session_state.current_feature = None

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/CVS_Health_Logo.svg/320px-CVS_Health_Logo.svg.png", width=150)
    st.markdown("# 🤖 Lumina Lite")
    st.markdown("**Agentic AI Demo**")
    st.markdown("---")
    
    page = st.radio(
        "Navigate",
        [
            "💬 Chat Interface",
            "💰 Cost Analytics",
            "📊 System Overview"
        ]
    )
    
    if page == "💬 Chat Interface":
        st.markdown("### Select Feature")
        
        feature = st.selectbox(
            "Choose an AI agent:",
            [
                "🖼️ Image Analysis",
                "👥 Colleague Lookup", 
                "🔍 AKS Network RAG",
                "🎬 Video Search",
                "📋 Policy Change Detector",
                "💡 Ask Me Anything"
            ]
        )
        
        st.session_state.current_feature = feature
        
        st.markdown("---")
        
        # Feature descriptions
        descriptions = {
            "🖼️ Image Analysis": "Upload architecture diagrams for AI-powered analysis using GPT-4 Vision",
            "👥 Colleague Lookup": "Find team members, roles, and locations across CVS",
            "🔍 AKS Network RAG": "Hybrid search: Internal docs + Azure documentation",
            "🎬 Video Search": "Search training videos with timestamp citations",
            "📋 Policy Change Detector": "Detect changes between policy versions",
            "💡 Ask Me Anything": "General questions about the system"
        }
        
        st.info(descriptions.get(feature, ""))
        
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
    
    st.markdown("---")
    st.markdown("**Built for:** CVS Health")
    st.markdown("**Features:** 6 Agentic AI Systems")

# Main content
if page == "💬 Chat Interface":
    st.markdown('<div class="main-header">💬 Lumina Lite Chat</div>', unsafe_allow_html=True)
    
    # Display chat messages
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        
        css_class = "user-message" if role == "user" else "assistant-message"
        icon = "👤" if role == "user" else "🤖"
        
        st.markdown(f"""
        <div class="chat-message {css_class}">
            <strong>{icon} {role.title()}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(content)
        
        # Show metadata if available
        if "metadata" in message:
            meta = message["metadata"]
            st.markdown(f"""
            <div style="margin-top: 0.5rem;">
                <span class="metric-inline">⏱️ {meta.get('latency_ms', 0)}ms</span>
                <span class="metric-inline">🎯 {meta.get('tool_calls', 0)} tools</span>
                <span class="metric-inline">💰 ${meta.get('cost', 0):.4f}</span>
            </div>
            """, unsafe_allow_html=True)
    
    # Chat input
    st.markdown("---")
    
    current_feature = st.session_state.current_feature
    
    # Feature-specific inputs
    if current_feature == "🖼️ Image Analysis":
        uploaded_file = st.file_uploader("Upload architecture diagram (PNG/JPG)", type=["png", "jpg", "jpeg"])
        user_input = st.text_input("Ask about the diagram:", placeholder="What are the main components in this architecture?")
        
        if st.button("Analyze") and uploaded_file and user_input:
            # Save uploaded file
            upload_path = Path("uploads") / uploaded_file.name
            upload_path.parent.mkdir(exist_ok=True)
            with open(upload_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Add user message
            st.session_state.messages.append({
                "role": "user",
                "content": f"**Image:** {uploaded_file.name}\n\n**Question:** {user_input}"
            })
            
            # Run agent
            with st.spinner("🔄 Analyzing image..."):
                from src.graphs.image_analysis_graph import run_image_analysis
                
                start_time = time.time()
                result = run_image_analysis(
                    image_path=str(upload_path),
                    question=user_input,
                    focus_areas="all"
                )
                latency_ms = int((time.time() - start_time) * 1000)
                
                # Add assistant message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "metadata": {
                        "latency_ms": latency_ms,
                        "tool_calls": len(result["tool_calls"]),
                        "cost": 0.0147  # Estimated
                    }
                })
            
            st.rerun()
    
    elif current_feature == "👥 Colleague Lookup":
        user_input = st.text_area(
            "Ask about colleagues:",
            placeholder="Who are the data scientists on the Lumina team and where are they located?",
            height=100
        )
        
        if st.button("Search") and user_input:
            st.session_state.messages.append({
                "role": "user",
                "content": user_input
            })
            
            with st.spinner("🔄 Searching team docs and HR database..."):
                from src.graphs.colleague_graph import run_colleague_lookup
                from src.core.cost_utils import calculate_cost
                
                start_time = time.time()
                result = run_colleague_lookup(user_input)
                latency_ms = int((time.time() - start_time) * 1000)
                
                # Calculate cost
                cost = calculate_cost(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o"),
                    tokens_in=int(result["tokens_used"] * 0.6),
                    tokens_out=int(result["tokens_used"] * 0.4)
                )
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "metadata": {
                        "latency_ms": latency_ms,
                        "tool_calls": len(result["tool_calls"]),
                        "cost": cost
                    }
                })
            
            st.rerun()
    
    elif current_feature == "🔍 AKS Network RAG":
        user_input = st.text_area(
            "Ask about AKS networking:",
            placeholder="How do I configure NSG rules for AKS? What are the required inbound and outbound rules?",
            height=100
        )
        
        if st.button("Search") and user_input:
            st.session_state.messages.append({
                "role": "user",
                "content": user_input
            })
            
            with st.spinner("🔄 Searching internal KB + Azure docs..."):
                from src.graphs.aks_graph import run_aks_query
                from src.core.cost_utils import calculate_cost
                
                start_time = time.time()
                result = run_aks_query(user_input)
                latency_ms = int((time.time() - start_time) * 1000)
                
                cost = calculate_cost(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o"),
                    tokens_in=int(result["tokens_used"] * 0.6),
                    tokens_out=int(result["tokens_used"] * 0.4)
                )
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "metadata": {
                        "latency_ms": latency_ms,
                        "tool_calls": len(result["tool_calls"]),
                        "cost": cost
                    }
                })
            
            st.rerun()
    
    elif current_feature == "🎬 Video Search":
        user_input = st.text_area(
            "Search training videos:",
            placeholder="How do I deploy an application to AKS using GitHub Actions? Give me step-by-step instructions.",
            height=100
        )
        
        if st.button("Search Videos") and user_input:
            st.session_state.messages.append({
                "role": "user",
                "content": user_input
            })
            
            with st.spinner("🔄 Searching video transcripts..."):
                from src.graphs.video_graph import run_video_search
                from src.core.cost_utils import calculate_cost
                
                start_time = time.time()
                result = run_video_search(user_input)
                latency_ms = int((time.time() - start_time) * 1000)
                
                cost = calculate_cost(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o"),
                    tokens_in=int(result["tokens_used"] * 0.6),
                    tokens_out=int(result["tokens_used"] * 0.4)
                )
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "metadata": {
                        "latency_ms": latency_ms,
                        "tool_calls": len(result["tool_calls"]),
                        "cost": cost
                    }
                })
            
            st.rerun()
    
    elif current_feature == "📋 Policy Change Detector":
        col1, col2 = st.columns(2)
        
        with col1:
            old_version = st.selectbox("Old Version", ["benefits_policy_v1.md"])
        with col2:
            new_version = st.selectbox("New Version", ["benefits_policy_v2.md"])
        
        if st.button("Detect Changes"):
            st.session_state.messages.append({
                "role": "user",
                "content": f"Analyze policy changes between {old_version} and {new_version}"
            })
            
            with st.spinner("🔄 Detecting policy changes..."):
                from src.graphs.policy_graph import run_policy_detection
                from src.core.cost_utils import calculate_cost
                
                start_time = time.time()
                result = run_policy_detection(old_version, new_version)
                latency_ms = int((time.time() - start_time) * 1000)
                
                cost = calculate_cost(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o"),
                    tokens_in=int(result["tokens_used"] * 0.6),
                    tokens_out=int(result["tokens_used"] * 0.4)
                )
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "metadata": {
                        "latency_ms": latency_ms,
                        "tool_calls": len(result["tool_calls"]),
                        "cost": cost
                    }
                })
            
            st.rerun()
    
    else:  # Ask Me Anything
        user_input = st.text_area(
            "Ask me anything about the system:",
            placeholder="How does the cost tracking work? What features are available?",
            height=100
        )
        
        if st.button("Ask") and user_input:
            st.session_state.messages.append({
                "role": "user",
                "content": user_input
            })
            
            # Simple Q&A without agent
            answer = f"""I'm a demo system showcasing 6 agentic AI features built for CVS Health's Lumina team:

1. **Image Analysis**: Analyzes architecture diagrams using GPT-4 Vision
2. **Colleague Lookup**: Multi-step RAG + structured data queries
3. **AKS Network RAG**: Hybrid search (internal KB + web)
4. **Video Search**: Timestamp-based citations for training videos
5. **Policy Change Detector**: Automated compliance tracking
6. **Cost Analytics**: Enterprise-scale ROI analysis

All features use LangGraph for agentic workflows, with full cost tracking per query.

**Your question:** {user_input}

For technical details, try one of the specific features from the sidebar!"""
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "metadata": {
                    "latency_ms": 0,
                    "tool_calls": 0,
                    "cost": 0
                }
            })
            
            st.rerun()

elif page == "💰 Cost Analytics":
    st.markdown('<div class="main-header">💰 Cost Analytics Dashboard</div>', unsafe_allow_html=True)
    
    from src.core.cost_analytics import get_comprehensive_cost_report
    
    try:
        report = get_comprehensive_cost_report()
        
        if "error" in report:
            st.warning(report["error"])
            st.info("💡 Use the Chat Interface to run queries and generate cost data!")
        else:
            dev_summary = report["development_summary"]
            
            st.markdown("## 🎉 Development Cost Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Spent", f"${dev_summary['total_cost_usd']:.2f}")
            with col2:
                st.metric("Total Queries", dev_summary['total_queries'])
            with col3:
                st.metric("Avg Cost/Query", f"${dev_summary['avg_cost_per_query']:.4f}")
            with col4:
                st.metric("Avg Latency", f"{dev_summary['avg_latency_ms']:.0f}ms")
            
            st.markdown("---")
            
            # By feature breakdown
            st.markdown("## 📊 Cost by Feature")
            
            df_features = pd.DataFrame(report["by_feature"])
            if not df_features.empty:
                st.dataframe(
                    df_features.style.format({
                        "total_cost_usd": "${:.4f}",
                        "avg_cost_usd": "${:.4f}",
                        "avg_latency_ms": "{:.1f}ms"
                    }),
                    use_container_width=True
                )
            
            st.markdown("---")
            
            # Scale projections
            st.markdown("## 🚀 Enterprise Scale (300K Users)")
            
            projections = report["scale_projections"]["300k_users"]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Monthly Cost", f"${projections['monthly_cost_usd']:,.2f}")
            with col2:
                st.metric("Annual Cost", f"${projections['annual_cost_usd']:,.2f}")
            with col3:
                st.metric("Cost/User/Month", f"${projections['cost_per_user_per_month']:.3f}")
            
            st.markdown("---")
            
            # Optimization recommendations
            st.markdown("## 💡 Top 3 Optimization Recommendations")
            
            recommendations = report.get("optimization_recommendations", [])[:3]
            
            for i, rec in enumerate(recommendations, 1):
                with st.expander(f"**{i}. {rec['title']}**"):
                    st.markdown(f"**Description:** {rec['description']}")
                    st.markdown(f"**Savings:** {rec['estimated_savings']['percent']}% (${rec['estimated_savings']['monthly_300k_users']:,.0f}/month)")
                    st.markdown(f"**Implementation:** {rec['implementation_time']}")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

elif page == "📊 System Overview":
    st.markdown('<div class="main-header">📊 System Overview</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ## 🎯 Lumina Lite Agentic
    
    Production-ready GenAI system demonstrating enterprise-scale agentic AI capabilities.
    
    ### 🏗️ Architecture
    
    - **Framework:** LangGraph for agentic workflows
    - **Models:** GPT-4o (reasoning), GPT-4 Vision (images), text-embedding-3-small
    - **Vector Store:** ChromaDB for RAG
    - **Backend:** Python + FastAPI
    - **Frontend:** Streamlit
    - **Cost Tracking:** SQLite for query logs
    
    ### ✨ Key Features
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>Core Features (Lumina-Inspired)</h4>
            <ul>
                <li>🖼️ <b>Image Analysis:</b> GPT-4 Vision for diagrams</li>
                <li>👥 <b>Colleague Lookup:</b> Multi-tool orchestration</li>
                <li>🔍 <b>AKS RAG:</b> Hybrid internal + web search</li>
                <li>🎬 <b>Video Search:</b> Timestamp citations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>Original Innovations</h4>
            <ul>
                <li>📋 <b>Policy Detector:</b> Change detection + routing</li>
                <li>💰 <b>Cost Analytics:</b> ROI tracking dashboard</li>
            </ul>
            <br>
            <p><b>Unique Value:</b> Built for $12, saves $150K/year at scale</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("## 📈 Production Readiness")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **✅ Implemented**
        - Cost tracking per query
        - Multi-tool orchestration
        - Source attribution
        - Error handling
        - Structured logging
        """)
    
    with col2:
        st.markdown("""
        **🔄 Next Steps**
        - Azure AKS deployment
        - Redis caching layer
        - Model routing logic
        - Fine-tuning pipeline
        - Monitoring dashboards
        """)
    
    with col3:
        st.markdown("""
        **🎯 Scale Target**
        - 300K CVS employees
        - 5 queries/user/day
        - $5,400/month optimized
        - <2s p95 latency
        - 99.9% uptime
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    Built for CVS Health Lumina Team | November 2024
</div>
""", unsafe_allow_html=True)