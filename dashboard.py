import streamlit as st
import json
from datetime import datetime
from dotenv import load_dotenv
from langgraph_builder import LangGraphBuilder

load_dotenv()

st.set_page_config(page_title="Lead Gen Dashboard", page_icon="🚀", layout="wide")

st.title("🚀 LangGraph Lead Generation Dashboard")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Controls")
    if st.button("🔄 Run Workflow", type="primary"):
        with st.spinner("Running workflow..."):
            builder = LangGraphBuilder(config_path="config/workflow.json")
            result = builder.execute()
            st.session_state['result'] = result
            st.success("✅ Workflow completed!")
    
    st.markdown("---")
    st.markdown("### 📊 Workflow Status")
    if 'result' in st.session_state:
        st.success("✅ Data loaded")
    else:
        st.info("👉 Click 'Run Workflow' to start")

# Main content
if 'result' in st.session_state:
    result = st.session_state['result']
    outputs = result.get('outputs', {})
    
    # Metrics
    feedback = outputs.get('feedback_trainer', {})
    metrics = feedback.get('metrics', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Open Rate", f"{metrics.get('open_rate', 0):.1%}")
    with col2:
        st.metric("👆 Click Rate", f"{metrics.get('click_rate', 0):.1%}")
    with col3:
        st.metric("💬 Reply Rate", f"{metrics.get('reply_rate', 0):.1%}")
    with col4:
        st.metric("📅 Meeting Rate", f"{metrics.get('meeting_rate', 0):.1%}")
    
    st.markdown("---")
    
    # Leads
    st.header("👥 Top Ranked Leads")
    ranked_leads = outputs.get('scoring', {}).get('ranked_leads', [])
    
    if ranked_leads:
        for lead in ranked_leads[:5]:
            with st.expander(f"🏢 {lead.get('company', 'Unknown')} - {lead.get('contact', 'Unknown')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Email:** {lead.get('email', 'N/A')}")
                    st.write(f"**Role:** {lead.get('role', 'N/A')}")
                with col2:
                    st.write(f"**Score:** {lead.get('score', 0):.2f}")
                    st.write(f"**Technologies:** {', '.join(lead.get('technologies', [])[:3])}")
    else:
        st.info("No leads found. Check API configuration.")
    
    # Emails
    st.markdown("---")
    st.header("✉️ Generated Emails")
    messages = outputs.get('outreach_content', {}).get('messages', [])
    
    if messages:
        for msg in messages[:3]:
            with st.container():
                st.subheader(f"📨 {msg.get('subject', 'No Subject')}")
                st.write(msg.get('email_body', 'No content'))
                st.caption(f"To: {msg.get('email', 'N/A')}")
                st.markdown("---")
    
    # Recommendations
    st.header("💡 AI Recommendations")
    recommendations = feedback.get('recommendations', [])
    
    for rec in recommendations:
        st.info(rec.get('recommendation', ''))

else:
    st.info("👈 Click 'Run Workflow' in the sidebar to get started!")