
import streamlit as st
import pandas as pd
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
    page_icon="L",
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
    
    [data-testid="stSidebar"] {
        background: #f7f7f7;
    }
    
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
    st.markdown("# Lumina Lite")
    st.markdown("---")
    
    if st.button("+ New Chat", use_container_width=True, type="primary"):
        thread_id = f"thread_{len(st.session_state.threads)}_{int(time.time())}"
        st.session_state.threads[thread_id] = {
            "feature": "Ask Me",
            "messages": [],
            "created": datetime.now().strftime("%H:%M"),
            "title": "New conversation"
        }
        st.session_state.current_thread_id = thread_id
        st.session_state.current_feature = "Ask Me"
        st.rerun()
    
    st.markdown("### Features")
    
    features = [
        ("Ask Me", "Ask Me"),
        ("Analyze Image", "Analyze Image"),
        ("Colleague Lookup", "Colleague Lookup"),
        ("AKS Network", "AKS Network"),
        ("Video Search", "Video Search"),
        ("Performance Metrics", "Performance Metrics")
    ]
    
    for icon, name in features:
        if st.button(name, use_container_width=True, key=f"feat_{name}"):
            thread_id = f"thread_{len(st.session_state.threads)}_{int(time.time())}"
            st.session_state.threads[thread_id] = {
                "feature": name,
                "messages": [],
                "created": datetime.now().strftime("%H:%M"),
                "title": name
            }
            st.session_state.current_thread_id = thread_id
            st.session_state.current_feature = name
            st.rerun()
    
    st.markdown("---")
    st.markdown("### Recent Threads")
    
    if st.session_state.threads:
        for thread_id, thread_data in list(st.session_state.threads.items())[-10:]:
            thread_label = f"{thread_data['title']} ({thread_data['created']})"
            if st.button(thread_label, key=f"thread_{thread_id}", use_container_width=True):
                st.session_state.current_thread_id = thread_id
                st.session_state.current_feature = thread_data['feature']
                st.rerun()

# Main area
if st.session_state.current_thread_id is None:
    st.markdown('<div class="header"><div class="title">Welcome to Lumina Lite Agentic</div></div>', unsafe_allow_html=True)
    
    st.markdown("## Get Started")
    st.write("Select a feature from the sidebar to begin:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Ask Me")
        st.write("Learn about the system, features, and architecture")
        
        st.markdown("### Analyze Image")
        st.write("Upload diagrams for GPT-4 Vision analysis")
        
        st.markdown("### Colleague Lookup")
        st.write("Find team members with multi-tool RAG")
    
    with col2:
        st.markdown("### AKS Network")
        st.write("Hybrid search: internal KB + Azure docs")
        
        st.markdown("### Video Search")
        st.write("Search videos with timestamp citations")
        
        st.markdown("### Performance Metrics")
        st.write("View system performance and cost analytics")
    
    arch_path = Path("data/arch.png")
    if arch_path.exists():
        st.markdown("---")
        st.markdown("## System Architecture")
        st.image(str(arch_path), use_container_width=True)

else:
    thread = st.session_state.threads[st.session_state.current_thread_id]
    current_feature = thread["feature"]
    
    st.markdown(f'<div class="header"><div class="title">{current_feature}</div></div>', unsafe_allow_html=True)
    
    if current_feature == "Ask Me" and len(thread["messages"]) == 0:
        st.markdown("## Welcome to Lumina Lite Agentic")
        st.write("I can answer questions about this system. Try asking:")
        
        example_questions = [
            "How does the colleague lookup agent work?",
            "Explain the AKS network workflow",
            "Show me the system architecture",
            "What's the cost at enterprise scale?",
            "How does video search extract timestamps?"
        ]
        
        for q in example_questions:
            st.markdown(f"- *{q}*")
        
        arch_path = Path("diagrams/main_architecture.png")
        if arch_path.exists():
            st.markdown("---")
            st.markdown("## System Architecture")
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
                if "image_path" in msg and msg["image_path"]:
                    image_path = Path(msg["image_path"])
                    if image_path.exists():
                        st.image(str(image_path), caption=msg.get("filename", "Uploaded image"), use_container_width=True)
                st.write(msg["content"])
        else:
            with st.chat_message("assistant"):
                if "tools" in msg and msg["tools"]:
                    tools_html = " ".join([f'<span class="tool-indicator">{t}</span>' for t in msg["tools"]])
                    st.markdown(tools_html, unsafe_allow_html=True)
                
                # Display diagrams if stored in message
                if "diagrams_displayed" in msg and msg["diagrams_displayed"]:
                    for diagram_info in msg["diagrams_displayed"]:
                        caption, path = diagram_info
                        st.image(path, caption=caption, use_container_width=True)
                
                st.write(msg["content"])
    
    st.markdown("---")
    
    if "Ask Me" in current_feature:
        with st.form(key=f"ask_form_{st.session_state.current_thread_id}", clear_on_submit=True):
            user_query = st.text_area(
                "Ask me anything:",
                placeholder="e.g., How does the colleague lookup work? Explain the AKS workflow.",
                height=100,
                key=f"input_{st.session_state.current_thread_id}"
            )
            
            submitted = st.form_submit_button("Ask", type="primary", use_container_width=True)
        
        if submitted and user_query:
            thread["messages"].append({"role": "user", "content": user_query})
            
            if thread["title"] == "Ask Me":
                thread["title"] = f"Ask Me: {user_query[:40]}..." if len(user_query) > 40 else f"Ask Me: {user_query}"
            
            query_lower = user_query.lower()
            diagrams_dir = Path("diagrams")
            diagrams_to_display = []
            
            # Smart keyword detection for diagrams
            if "colleague" in query_lower or "lookup" in query_lower:
                diag = diagrams_dir / "feature2_colleague_lookup.png"
                if diag.exists():
                    diagrams_to_display.append(("Colleague Lookup Agent Workflow", str(diag)))
            
            if "aks" in query_lower or ("network" in query_lower and "azure" in query_lower) or "hybrid" in query_lower:
                diag = diagrams_dir / "feature3_aks_network.png"
                if diag.exists():
                    diagrams_to_display.append(("AKS Network Agent - Hybrid RAG", str(diag)))
            
            if "video" in query_lower and ("search" in query_lower or "transcript" in query_lower or "timestamp" in query_lower):
                diag = diagrams_dir / "feature4_video_search.png"
                if diag.exists():
                    diagrams_to_display.append(("Video Search Agent Workflow", str(diag)))
            
            if ("image" in query_lower and "analysis" in query_lower) or "vision" in query_lower:
                diag = diagrams_dir / "feature1_image_analysis.png"
                if diag.exists():
                    diagrams_to_display.append(("Image Analysis Agent Workflow", str(diag)))
            
            if "policy" in query_lower and ("change" in query_lower or "detect" in query_lower):
                diag = diagrams_dir / "feature5_policy_change.png"
                if diag.exists():
                    diagrams_to_display.append(("Policy Change Detector Workflow", str(diag)))
            
            if "cost" in query_lower and ("analytics" in query_lower or "tracking" in query_lower or "optimization" in query_lower):
                diag = diagrams_dir / "feature6_cost_analytics.png"
                if diag.exists():
                    diagrams_to_display.append(("Cost Analytics Workflow", str(diag)))
            
            if ("architecture" in query_lower or "system" in query_lower or "all agents" in query_lower or "overall" in query_lower) and not diagrams_to_display:
                diag = diagrams_dir / "main_architecture.png"
                if diag.exists():
                    diagrams_to_display.append(("Complete System Architecture", str(diag)))
            
            with st.spinner("Thinking..."):
                from src.core.llm import call_llm
                from src.core.cost_utils import calculate_cost
                
                diagram_context = ""
                if diagrams_to_display:
                    diagram_context = "\n\nA workflow diagram will be displayed with your answer. Reference it by saying 'As shown in the diagram...' and explain the specific flow."
                
                system_context = f"""You are explaining the Lumina Lite Agentic system.

**System:** 6 agentic AI workflows built with LangGraph and GPT-4o.

**Features:**
- Image Analysis: GPT-4 Vision for diagrams
- Colleague Lookup: Multi-step (search docs → query HR → synthesize)
- AKS Network: Hybrid RAG (CVS KB + Azure docs + IT forms)
- Video Search: Timestamp-based citations
- Policy Change: Semantic drift detection
- Cost Analytics: $12 dev cost, $5.4K/month at 300K users

Answer concisely and professionally.{diagram_context}"""

                messages = [
                    {"role": "system", "content": system_context},
                    {"role": "user", "content": user_query}
                ]
                
                for msg in thread["messages"][-4:]:
                    if msg["role"] == "user":
                        messages.append({"role": "user", "content": msg["content"]})
                
                start_time = time.time()
                result = call_llm(messages, temperature=0.7, max_tokens=1000)
                latency_ms = int((time.time() - start_time) * 1000)
                
                cost = calculate_cost(
                    model="gpt-4o",
                    tokens_in=result["usage"]["prompt_tokens"],
                    tokens_out=result["usage"]["completion_tokens"]
                )
                
                response = result["content"] + f"\n\n*{latency_ms}ms • ${cost:.4f}*"
                
                tools_used = ["Architecture Diagrams"] if diagrams_to_display else []
                
                thread["messages"].append({
                    "role": "assistant",
                    "content": response,
                    "tools": tools_used if tools_used else None,
                    "diagrams_displayed": diagrams_to_display
                })
            
            # Show diagrams after spinner completes
            if diagrams_to_display:
                for caption, path in diagrams_to_display:
                    st.image(path, caption=caption, use_container_width=True)
            
            st.rerun()
    
    elif "Analyze Image" in current_feature:
        with st.form(key=f"image_form_{st.session_state.current_thread_id}", clear_on_submit=True):
            uploaded_file = st.file_uploader("Upload image or presentation:", type=["png", "jpg", "jpeg", "pptx"], key=f"upload_{st.session_state.current_thread_id}")
            user_query = st.text_area("What would you like to know?", height=100, key=f"q_{st.session_state.current_thread_id}", placeholder="Explain this architecture, identify components, summarize best practices")
            submitted = st.form_submit_button("Analyze", type="primary", use_container_width=True)
        
        if submitted and uploaded_file and user_query:
            upload_path = Path("uploads") / uploaded_file.name
            upload_path.parent.mkdir(exist_ok=True)
            
            with open(upload_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            thread["messages"].append({
                "role": "user", 
                "content": user_query,
                "image_path": str(upload_path),
                "filename": uploaded_file.name
            })
            
            if thread["title"] == "Analyze Image":
                thread["title"] = f"Image: {uploaded_file.name}"
            
            with st.spinner("Analyzing with GPT-4 Vision..."):
                from src.graphs.image_analysis_graph import run_image_analysis
                from src.core.cost_utils import calculate_cost
                
                start_time = time.time()
                result = run_image_analysis(str(upload_path), user_query, "all")
                latency_ms = int((time.time() - start_time) * 1000)
                cost = calculate_cost("gpt-4o", int(result["tokens_used"] * 0.6), int(result["tokens_used"] * 0.4))
                
                answer = result["answer"].replace(str(upload_path), "the diagram").replace('uploads\\', '').replace('uploads/', '')
                
                thread["messages"].append({
                    "role": "assistant",
                    "content": answer + f"\n\n*{latency_ms}ms • ${cost:.4f}*",
                    "tools": ["GPT-4 Vision"]
                })
            st.rerun()
    
    elif "Colleague Lookup" in current_feature:
        with st.form(key=f"colleague_form_{st.session_state.current_thread_id}", clear_on_submit=True):
            user_query = st.text_area("Ask about team members:", height=100, key=f"q_{st.session_state.current_thread_id}", placeholder="Who are the data scientists? Where is Sarah Chen located?")
            submitted = st.form_submit_button("Search", type="primary", use_container_width=True)
        
        if submitted and user_query:
            thread["messages"].append({"role": "user", "content": user_query})
            
            if thread["title"] == "Colleague Lookup":
                thread["title"] = f"Lookup: {user_query[:40]}..." if len(user_query) > 40 else f"Lookup: {user_query}"
            
            with st.spinner("Searching team docs and HR database..."):
                from src.graphs.colleague_graph import run_colleague_lookup
                from src.core.cost_utils import calculate_cost
                
                start_time = time.time()
                result = run_colleague_lookup(user_query)
                latency_ms = int((time.time() - start_time) * 1000)
                cost = calculate_cost("gpt-4o", int(result["tokens_used"] * 0.6), int(result["tokens_used"] * 0.4))
                
                thread["messages"].append({
                    "role": "assistant",
                    "content": result["answer"] + f"\n\n*{latency_ms}ms • ${cost:.4f}*",
                    "tools": ["Team Docs", "HR Database"]
                })
            st.rerun()
    
    elif "AKS Network" in current_feature:
        with st.form(key=f"aks_form_{st.session_state.current_thread_id}", clear_on_submit=True):
            user_query = st.text_area("Ask about AKS networking:", height=100, key=f"q_{st.session_state.current_thread_id}", placeholder="How to configure NSG rules? What forms do I need?")
            submitted = st.form_submit_button("Search", type="primary", use_container_width=True)
        
        if submitted and user_query:
            thread["messages"].append({"role": "user", "content": user_query})
            
            if thread["title"] == "AKS Network":
                thread["title"] = f"AKS: {user_query[:40]}..." if len(user_query) > 40 else f"AKS: {user_query}"
            
            with st.spinner("Searching internal KB and Azure docs..."):
                from src.graphs.aks_graph import run_aks_query
                from src.core.cost_utils import calculate_cost
                
                start_time = time.time()
                result = run_aks_query(user_query)
                latency_ms = int((time.time() - start_time) * 1000)
                cost = calculate_cost("gpt-4o", int(result["tokens_used"] * 0.6), int(result["tokens_used"] * 0.4))
                
                thread["messages"].append({
                    "role": "assistant",
                    "content": result["answer"] + f"\n\n*{latency_ms}ms • ${cost:.4f}*",
                    "tools": ["CVS KB", "Azure Docs", "IT Forms"]
                })
            st.rerun()
    
    elif "Video Search" in current_feature:
        with st.form(key=f"video_form_{st.session_state.current_thread_id}", clear_on_submit=True):
            user_query = st.text_area("Search video content:", height=100, key=f"q_{st.session_state.current_thread_id}", placeholder="How to deploy with GitHub Actions?")
            submitted = st.form_submit_button("Search Videos", type="primary", use_container_width=True)
        
        if submitted and user_query:
            thread["messages"].append({"role": "user", "content": user_query})
            
            if thread["title"] == "Video Search":
                thread["title"] = f"Video: {user_query[:40]}..." if len(user_query) > 40 else f"Video: {user_query}"
            
            with st.spinner("Searching video transcripts..."):
                from src.graphs.video_graph import run_video_search
                from src.core.cost_utils import calculate_cost
                
                start_time = time.time()
                result = run_video_search(user_query)
                latency_ms = int((time.time() - start_time) * 1000)
                cost = calculate_cost("gpt-4o", int(result["tokens_used"] * 0.6), int(result["tokens_used"] * 0.4))
                
                thread["messages"].append({
                    "role": "assistant",
                    "content": result["answer"] + f"\n\n*{latency_ms}ms • ${cost:.4f}*",
                    "tools": ["Transcripts"]
                })
            st.rerun()
    
    elif "Performance Metrics" in current_feature:
        st.markdown("## Performance Metrics Dashboard")
        
        try:
            # Import the raw function, not the tool
            from src.core.logging_utils import get_cost_summary
            import sqlite3
            from pathlib import Path
            
            log_db = Path("./logs/queries.db")
            
            if not log_db.exists():
                st.warning("No metrics available. Run some queries first to generate data.")
                st.info("Try using Colleague Lookup, AKS Network, or Video Search features to generate metrics.")
            else:
                # Get overall summary
                overall = get_cost_summary()
                
                st.markdown("### Overall Statistics")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Queries", overall["total_queries"])
                with col2:
                    st.metric("Total Cost", f"${overall['total_cost_usd']:.2f}")
                with col3:
                    st.metric("Avg Cost/Query", f"${overall['avg_cost_per_query']:.4f}")
                with col4:
                    st.metric("Success Rate", f"{overall['success_rate']*100:.1f}%")
                
                st.markdown("---")
                
                # Get detailed metrics per feature
                conn = sqlite3.connect(log_db)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        feature,
                        COUNT(*) as total_queries,
                        AVG(latency_ms) as avg_latency,
                        MIN(latency_ms) as min_latency,
                        MAX(latency_ms) as max_latency,
                        AVG(total_tokens) as avg_tokens,
                        AVG(cost_usd) as avg_cost,
                        SUM(cost_usd) as total_cost,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate
                    FROM queries
                    GROUP BY feature
                """)
                
                features_data = []
                for row in cursor.fetchall():
                    feature, queries, avg_lat, min_lat, max_lat, avg_tok, avg_cost, total_cost, success = row
                    features_data.append({
                        "feature": feature,
                        "total_queries": queries,
                        "avg_latency_ms": round(avg_lat or 0, 1),
                        "min_latency_ms": round(min_lat or 0, 1),
                        "max_latency_ms": round(max_lat or 0, 1),
                        "avg_tokens": round(avg_tok or 0, 0),
                        "avg_cost_usd": round(avg_cost or 0, 6),
                        "total_cost_usd": round(total_cost or 0, 4),
                        "success_rate": round(success or 0, 1)
                    })
                
                conn.close()
                
                st.markdown("### Performance by Feature")
                
                df = pd.DataFrame(features_data)
                
                if not df.empty:
                    st.dataframe(
                        df,
                        use_container_width=True,
                        column_config={
                            "feature": "Feature",
                            "total_queries": "Queries",
                            "avg_latency_ms": st.column_config.NumberColumn("Avg Latency (ms)", format="%.1f"),
                            "min_latency_ms": st.column_config.NumberColumn("Min (ms)", format="%.1f"),
                            "max_latency_ms": st.column_config.NumberColumn("Max (ms)", format="%.1f"),
                            "avg_tokens": st.column_config.NumberColumn("Avg Tokens", format="%.0f"),
                            "avg_cost_usd": st.column_config.NumberColumn("Avg Cost", format="$%.6f"),
                            "total_cost_usd": st.column_config.NumberColumn("Total Cost", format="$%.4f"),
                            "success_rate": st.column_config.NumberColumn("Success Rate (%)", format="%.1f")
                        }
                    )
                    
                    st.markdown("---")
                    st.markdown("### Visualizations")
                    
                    import plotly.express as px
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig = px.bar(
                            df,
                            x="feature",
                            y="total_cost_usd",
                            title="Total Cost by Feature",
                            labels={"total_cost_usd": "Cost (USD)", "feature": "Feature"},
                            color="total_cost_usd",
                            color_continuous_scale="Reds"
                        )
                        fig.update_layout(showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        fig2 = px.bar(
                            df,
                            x="feature",
                            y="avg_latency_ms",
                            title="Average Latency by Feature",
                            labels={"avg_latency_ms": "Latency (ms)", "feature": "Feature"},
                            color="avg_latency_ms",
                            color_continuous_scale="Blues"
                        )
                        fig2.update_layout(showlegend=False)
                        st.plotly_chart(fig2, use_container_width=True)
                    
                    st.markdown("---")
                    st.markdown("### Enterprise Scale Projections")
                    
                    avg_cost = overall["avg_cost_per_query"]
                    
                    from src.core.cost_utils import project_monthly_cost
                    
                    scales = {
                        "1K Users": project_monthly_cost(avg_cost, 5, 1000),
                        "10K Users": project_monthly_cost(avg_cost, 5, 10000),
                        "50K Users": project_monthly_cost(avg_cost, 5, 50000),
                        "300K Users (CVS)": project_monthly_cost(avg_cost, 5, 300000)
                    }
                    
                    scale_df = pd.DataFrame([
                        {
                            "Scale": name,
                            "Monthly Queries": f"{data['monthly_queries']:,}",
                            "Monthly Cost": f"${data['monthly_cost_usd']:,.2f}",
                            "Annual Cost": f"${data['annual_cost_usd']:,.2f}",
                            "Cost/User/Month": f"${data['cost_per_user_per_month']:.3f}"
                        }
                        for name, data in scales.items()
                    ])
                    
                    st.dataframe(scale_df, use_container_width=True)
                    
                    baseline_annual = scales['300K Users (CVS)']['annual_cost_usd']
                    optimized_annual = baseline_annual * 0.3
                    savings = baseline_annual - optimized_annual
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Baseline (300K users)", f"${baseline_annual:,.0f}/year")
                    with col2:
                        st.metric("Optimized", f"${optimized_annual:,.0f}/year")
                    with col3:
                        st.metric("Annual Savings", f"${savings:,.0f}")
                else:
                    st.info("No feature-level data yet. Run queries to populate metrics.")
        
        except Exception as e:
            st.error(f"Error loading metrics: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

st.markdown("""
<div style="text-align: center; color: #ccc; padding: 2rem 0; font-size: 0.85rem; border-top: 1px solid #f0f0f0; margin-top: 3rem;">
    Lumina Lite Agentic • Built for CVS Health • November 2024
</div>
""", unsafe_allow_html=True)