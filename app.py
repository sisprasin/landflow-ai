import streamlit as st
import asyncio
import os
import pandas as pd
from datetime import datetime
import database
import agents

# Ensure database is initialized and seeded
database.init_db()
database.seed_db()

# Page configuration
st.set_page_config(
    page_title="LandFlow AI — CRM & Multi-Agent Workspace",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium CSS for styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

h1, h2, h3, .title-text {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
}

/* Gradient Dashboard Header */
.dashboard-header {
    background: linear-gradient(135deg, #0d1b2a 0%, #1b263b 100%);
    padding: 0.8rem 1.5rem;
    border-radius: 12px;
    margin-bottom: 1.25rem;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: white;
}

.dashboard-title {
    font-size: 1.8rem;
    font-weight: 700;
    margin: 0;
    background: linear-gradient(to right, #e0e1dd, #778da9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.dashboard-subtitle {
    color: #a3b18a;
    font-size: 0.9rem;
    margin-top: 0.2rem;
    font-weight: 500;
}

/* Metric Cards */
.metric-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 1.25rem;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
    border-color: rgba(255, 255, 255, 0.2);
}

.metric-val {
    font-size: 2.2rem;
    font-weight: 700;
    color: #415a77;
    margin: 0.2rem 0;
}

.metric-label {
    font-size: 0.9rem;
    color: #8d99ae;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
}

/* Kanban Cards */
.kanban-card {
    background-color: #ffffff;
    color: #1e293b !important;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 0.75rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.kanban-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    border-color: #cbd5e1;
}

.kanban-title {
    font-weight: 700;
    font-size: 0.85rem;
    color: #0f172a;
}

.kanban-subtitle {
    font-size: 0.75rem;
    color: #475569 !important;
    margin-top: 0.3rem;
    line-height: 1.35;
}

/* Timeline elements */
.timeline-item {
    border-left: 2px solid #778da9;
    padding-left: 1.2rem;
    position: relative;
    margin-bottom: 1.2rem;
}

.timeline-item::before {
    content: '';
    position: absolute;
    width: 10px;
    height: 10px;
    background-color: #415a77;
    border-radius: 50%;
    left: -6px;
    top: 5px;
}

.timeline-date {
    font-size: 0.8rem;
    color: #8d99ae;
    font-weight: 600;
}

.timeline-type {
    font-weight: 700;
    font-size: 0.9rem;
    color: #415a77;
}

.timeline-text {
    font-size: 0.9rem;
    margin-top: 0.2rem;
}
</style>
""", unsafe_allow_html=True)

# ----------------- SESSION STATE & AUTHENTICATION -----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None

def handle_login(username, password):
    user = database.check_login(username, password)
    if user:
        st.session_state.logged_in = True
        st.session_state.username = user["username"]
        st.session_state.role = user["role"]
        st.success(f"Logged in successfully as {user['username']} ({user['role']})")
        st.rerun()
    else:
        st.error("Invalid username or password.")

def handle_logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.rerun()

# ----------------- LOGIN SCREEN -----------------
if not st.session_state.logged_in:
    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.markdown("<div style='height: 5rem;'></div>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #415a77;'>🏔️ LandFlow AI CRM Login</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #8d99ae;'>Enter your credentials to manage real estate deals & consult AI Agents</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username_input = st.text_input("Username", value="admin")
            password_input = st.text_input("Password", type="password", value="admin123")
            submit_login = st.form_submit_button("Sign In", use_container_width=True)
            
            if submit_login:
                handle_login(username_input, password_input)
                
        st.info("💡 Quick tip: Seed users are `admin` / `admin123` (Admin) and `broker1` / `broker123` (Broker).")
        st.stop()

# ----------------- MAIN LAYOUT -----------------

# Header Section
st.markdown("""
<div class="dashboard-header">
    <h1 class="dashboard-title">🏔️ LandFlow AI</h1>
    <div class="dashboard-subtitle">Indian Real Estate Land CRM with Google ADK Multi-Agent Collaboration</div>
</div>
""", unsafe_allow_html=True)

# Sidebar Info and Controls
with st.sidebar:
    st.markdown(f"""
    <div style="background-color: rgba(65, 90, 119, 0.12); padding: 0.9rem; border-radius: 8px; border: 1px solid rgba(65, 90, 119, 0.25); margin-bottom: 1rem;">
        <div style="font-size: 0.75rem; color: #8d99ae; font-weight: bold; text-transform: uppercase; letter-spacing: 0.05em;">Logged In As</div>
        <div style="font-size: 1.15rem; font-weight: 700; color: #415a77; margin-top: 0.15rem;">👤 {st.session_state.username}</div>
        <div style="font-size: 0.8rem; color: #778da9; font-weight: 600; margin-top: 0.1rem;">Role: {st.session_state.role}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Logout", type="secondary", use_container_width=True):
        handle_logout()
        
    st.markdown("---")
    st.markdown("### 🛠️ ADK & MCP Integration")
    st.markdown("""
    * **Database**: Local SQLite (`landflow.db`)
    * **MCP Server**: FastMCP via subprocess stdio
    * **ADK Version**: Google Antigravity SDK
    * **Gemini LLM**: `gemini-3.5-flash` via ADK
    """)
    
    # Check Gemini or DeepSeek API Key
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    deepseek_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if deepseek_key:
        st.success("✅ DEEPSEEK_API_KEY loaded")
    elif gemini_key:
        st.success("✅ GEMINI_API_KEY loaded")
    else:
        st.error("⚠️ GEMINI_API_KEY / DEEPSEEK_API_KEY is not set in env!")
        st.markdown("Agents cannot execute without a key. Add it to a `.env` file in the project folder:")
        st.code("DEEPSEEK_API_KEY=your_key_here\n# OR\nGEMINI_API_KEY=your_key_here")

# Tab Navigation
tabs = st.tabs([
    "📊 Dashboard", 
    "📋 Client Hub (Buyers & Sellers)", 
    "🏔️ Property Catalog", 
    "⛓️ Deal Pipeline", 
    "🤖 AI Multi-Agent Workspace"
])

# Format currency helper
def format_inr(val):
    if val >= 10000000.0:
        return f"₹{val / 10000000.0:.2f} Cr"
    elif val >= 100000.0:
        return f"₹{val / 100000.0:.2f} Lakh"
    else:
        return f"₹{val:,.2f}"

def get_mock_buyer_insight(buyer_details):
    name = buyer_details.get("name", "Buyer")
    pref_loc = buyer_details.get("preferred_location", "N/A")
    
    score = 80
    intent = "High"
    urgency = "1 Month"
    flexibility = "Somewhat Flexible"
    matches = "Property #1 (Noida), Property #11 (Noida)"
    closing_pct = 75
    timeline = "30 Days"
    risks = "Comparing with developer listings in Noida."
    action = "Schedule site visit for gated plots."
    
    if "Rajesh Kumar" in name:
        score = 92
        intent = "Very High"
        urgency = "14 Days"
        flexibility = "Firm"
        matches = "Property #1 (Noida Sector 150), Property #11 (Noida Sector 150)"
        closing_pct = 87
        timeline = "14 Days"
        risks = "Awaiting final clearance checks on NCR titles."
        action = "Schedule Site Visit"
    elif "Amit Patel" in name:
        score = 88
        intent = "High"
        urgency = "30 Days"
        flexibility = "Flexible"
        matches = "Property #2 (Whitefield Bengaluru), Property #12 (Whitefield Bengaluru)"
        closing_pct = 80
        timeline = "30 Days"
        risks = "Gated community approval validation pending by buyer's legal team."
        action = "Schedule Site Visit"
    elif "Priya Sharma" in name:
        score = 95
        intent = "Very High"
        urgency = "Immediate"
        flexibility = "Somewhat Flexible"
        matches = "Property #3 (ECR Chennai), Property #13 (ECR Chennai)"
        closing_pct = 90
        timeline = "7 Days"
        risks = "Requires CMDA approval verification before signature."
        action = "Draft Sale Agreement"
    elif "Sunita Reddy" in name:
        score = 90
        intent = "Very High"
        urgency = "15 Days"
        flexibility = "Flexible"
        matches = "Property #5 (Gachibowli Hyderabad), Property #15 (Gachibowli Hyderabad)"
        closing_pct = 85
        timeline = "15 Days"
        risks = "Industrial zoning verification pending."
        action = "Coordinate Industrial Permit Check"
        
    return {
        "lead_score": score,
        "buying_intent": intent,
        "urgency": urgency,
        "budget_flexibility": flexibility,
        "preferred_locations": pref_loc,
        "best_matching_properties": matches,
        "likelihood_of_closing": closing_pct,
        "expected_closing_timeline": timeline,
        "potential_risks": risks,
        "recommended_next_action": action
    }

def get_mock_communication_draft(client_type, client_name, comm_type):
    if client_type == "buyer":
        if "Rajesh Kumar" in client_name:
            if "WhatsApp" in comm_type:
                return (
                    "Hi Rajesh, hope you are doing well! This is Neha from LandFlow AI. "
                    "I wanted to follow up on your interest in Noida Sector 150 plots. We have a couple of new premium listings "
                    "under ₹2 Cr that match your requirements. Let me know if we can schedule a quick call today to discuss details. Thanks!"
                )
            elif "Email" in comm_type:
                return (
                    "Subject: Personalized Land Listings in Noida Sector 150 - LandFlow AI\n\n"
                    "Dear Rajesh,\n\n"
                    "I hope this email finds you well.\n\n"
                    "Following up on our recent conversation regarding your search for residential land in Noida Sector 150 with a budget of ₹1.5 Crore. I have reviewed our catalog and identified two listings that meet your exact specifications.\n\n"
                    "Could we schedule a brief 10-minute site visit this Saturday to inspect the plots?\n\n"
                    "Best regards,\nNeha Sen\nLandFlow AI"
                )
            elif "Call" in comm_type:
                return (
                    "**Intro:** Good morning Rajesh, Neha here from LandFlow AI. Hope you're having a good day!\n"
                    "**Purpose:** I'm calling because we just received title clearance on two highly sought-after plots in Noida Sector 150 that fit your ₹1.5 Cr budget.\n"
                    "**Key points to mention:**\n"
                    "- CMDA/RERA registered plots.\n"
                    "- 200 Sq Yards size requirement.\n"
                    "**Close/Call-to-Action:** Would you be open to a site visit this coming Saturday morning?"
                )
            elif "Meeting" in comm_type:
                return (
                    "**Meeting Agenda: Noida Sector 150 Site Visit & Plot Inspection**\n\n"
                    "**Client:** Rajesh Kumar\n"
                    "**Broker:** Neha Sen\n\n"
                    "1. **Property Overview (10 mins):** Review plot layouts and surrounding development updates in Noida Sector 150.\n"
                    "2. **Financial Discussion (15 mins):** Break down of the ₹1.5 Cr pricing, registry fees, and budget flexibility options.\n"
                    "3. **Timeline Review (10 mins):** Outline the expected 14-day documentation and registration steps."
                )
            else: # Negotiation
                return (
                    "**Negotiation Strategy for Rajesh Kumar:**\n\n"
                    "1. **Highlight Plot Scarcity:** Noida Sector 150 is seeing rapid occupancy. Emphasize that these plots are rare listings under ₹2 Cr.\n"
                    "2. **Leverage Cash Readiness:** Note Rajesh's high score and readiness to close in 14 days to request a discount from the seller.\n"
                    "3. **Address Title Checks:** Affirm that all NCR titles have been pre-screened to address his main concern."
                )
        elif "Amit Patel" in client_name:
            if "WhatsApp" in comm_type:
                return (
                    "Hi Amit, hope you are doing well! This is Neha from LandFlow AI. "
                    "I have some updates regarding the plots in Whitefield Bengaluru. We can schedule a site visit this week."
                )
            elif "Email" in comm_type:
                return (
                    "Subject: Whitefield Bengaluru Property Updates - LandFlow AI\n\n"
                    "Dear Amit,\n\n"
                    "I wanted to follow up on your budget of ₹3.0 Cr for Whitefield Bengaluru properties. We have matched you with two premium plots."
                )
            elif "Call" in comm_type:
                return "**Intro:** Hi Amit, Neha here. Just calling to update you on Whitefield listings."
            elif "Meeting" in comm_type:
                return "**Meeting Agenda: Amit Patel Whitefield Plot Review**\n1. Plot layout review\n2. Documentation inspection"
            else:
                return "1. Stand firm on pricing due to prime Gated Community location.\n2. Leverage quick closing speed."
        else:
            if "WhatsApp" in comm_type:
                return f"Hi {client_name}, hope you are doing well! Following up from LandFlow AI regarding matching plots. Let's talk soon!"
            elif "Email" in comm_type:
                return f"Subject: Tailored Land Options - LandFlow AI\n\nDear {client_name},\n\nWe have identified some new land options matching your requirements."
            elif "Call" in comm_type:
                return f"**Intro:** Hello {client_name}, Neha from LandFlow AI calling to discuss properties."
            elif "Meeting" in comm_type:
                return f"**Meeting Agenda for {client_name}**\n1. Review parameters\n2. Next steps"
            else:
                return "1. Emphasize budget fit.\n2. Confirm registration timelines."
    else: # seller
        if "Manoj Srinivasan" in client_name:
            if "WhatsApp" in comm_type:
                return (
                    "Hi Manoj, hope you're doing well. This is Neha from LandFlow AI. "
                    "I have an update regarding your plot in ECR Chennai. We have active buyers interested in this segment. Can we connect briefly to confirm documentation status? Thanks!"
                )
            elif "Email" in comm_type:
                return (
                    "Subject: Documentation Status Update - ECR Chennai Property - LandFlow AI\n\n"
                    "Dear Manoj,\n\n"
                    "I hope this email finds you well.\n\n"
                    "We have received multiple inquiries regarding your ECR Chennai property listed at ₹3.5 Cr. One buyer is highly qualified and ready to negotiate, but is requesting the latest land registry documents.\n\n"
                    "Please let us know when you can share these documents so we can advance the deal.\n\n"
                    "Best regards,\nNeha Sen\nLandFlow AI"
                )
            elif "Call" in comm_type:
                return (
                    "**Intro:** Hi Manoj, Neha from LandFlow AI. Hope you're doing well!\n"
                    "**Purpose:** I'm calling because our buyers are ready to proceed with documentation, but we need to confirm when the land registry documents will be ready.\n"
                    "**Close:** Can I request you to email the copies by tomorrow evening?"
                )
            elif "Meeting" in comm_type:
                return (
                    "**Meeting Agenda: Manoj Srinivasan - ECR Chennai Listing Review**\n\n"
                    "1. **Buyer Feedback (10 mins):** Summary of buyer responses to the ₹3.5 Cr asking price.\n"
                    "2. **Documentation Check (15 mins):** Status of land registry and CMDA clearances.\n"
                    "3. **Next Steps (5 mins):** Schedule site visits for shortlisted buyers."
                )
            else: # Negotiation
                return (
                    "**Negotiation Strategy for Manoj Srinivasan:**\n\n"
                    "1. **Highlight High-Value Buyers:** Mention we have buyers with budget alignment for ECR Chennai.\n"
                    "2. **Firm Price Justification:** Justify the ₹3.5 Cr asking price based on ECR beach access.\n"
                    "3. **Prompt Registry:** Urge swift document preparation to close within the week."
                )
        else:
            if "WhatsApp" in comm_type:
                return f"Hi {client_name}, following up from LandFlow AI regarding your listing. We have updates."
            elif "Email" in comm_type:
                return f"Subject: Listing Performance Update - LandFlow AI\n\nDear {client_name},\n\nWe wanted to share listing interest stats with you."
            elif "Call" in comm_type:
                return f"**Intro:** Hi {client_name}, Neha from LandFlow AI calling regarding your property."
            elif "Meeting" in comm_type:
                return f"**Meeting Agenda for {client_name}**\n1. Review buyer feedback\n2. Price positioning"
            else:
                return "1. Detail market activity in location.\n2. Advise on documentation speed."

# ----------------- TAB 1: DASHBOARD -----------------
with tabs[0]:
    buyers = database.get_all_buyers()
    sellers = database.get_all_sellers()
    properties = database.get_all_properties()
    deals = database.get_all_deals()
    followups = database.get_followups(pending_only=True)
    
    # 1. Today's AI Business Brief Card
    if "ai_brief" not in st.session_state:
        st.session_state.ai_brief = None
        
    if st.session_state.ai_brief is None:
        if not os.environ.get("GEMINI_API_KEY") and not os.environ.get("DEEPSEEK_API_KEY"):
            # Sample brief fallback matching the spec exactly
            st.session_state.ai_brief = (
                "### Today's Summary\n"
                "• **8** follow-ups pending  \n"
                "• **2** high-value buyers have not been contacted  \n"
                "• **3** deals likely to close this week  \n"
                "• **1** seller is waiting for documentation  \n\n"
                "### Priority Actions\n"
                "1. **Call Rajesh Kumar** (Noida Sector 150)  \n"
                "2. **Schedule site visit for Amit Patel** (Whitefield Bengaluru)  \n"
                "3. **Request land registry from Manoj Srinivasan** (ECR Chennai)  \n\n"
                "*(Note: Export GEMINI_API_KEY to retrieve dynamic summaries via ADK.)*"
            )
        else:
            with st.spinner("Generating Today's AI Business Brief..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    st.session_state.ai_brief = loop.run_until_complete(
                        agents.run_dashboard_brief_agent(st.session_state.username)
                    )
                except Exception as e:
                    st.session_state.ai_brief = f"Error generating brief: {str(e)}"
                    
    # Render Today's AI Business Brief
    st.markdown(f"""
    <div style="background-color: rgba(65, 90, 119, 0.08); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(65, 90, 119, 0.25); margin-bottom: 1.5rem; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);">
        <h3 style="margin-top: 0; color: #415a77; font-family: 'Space Grotesk', sans-serif;">📋 Today's AI Business Brief</h3>
        <p style="font-size: 1.15rem; font-weight: bold; color: #334155; margin-bottom: 1rem;">Good Morning, {st.session_state.username}!</p>
        <div style="color: #1e293b;">
    """, unsafe_allow_html=True)
    
    st.markdown(st.session_state.ai_brief)
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Add a refresh button if API key is present
    if os.environ.get("GEMINI_API_KEY") or os.environ.get("DEEPSEEK_API_KEY"):
        if st.button("🔄 Regenerate AI Business Brief", key="refresh_brief_btn"):
            st.session_state.ai_brief = None
            st.rerun()

    st.markdown("---")
    
    # 2. Visual AI Business Metrics Grid
    st.markdown("### 📈 AI Business Metrics")
    metrics = database.get_ai_dashboard_metrics()
    
    m_row1_cols = st.columns(4)
    m_row2_cols = st.columns(4)
    
    with m_row1_cols[0]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">💰 Revenue Potential</div>
            <div class="metric-val" style="color: #2a9d8f;">{format_inr(metrics['revenue_potential'])}</div>
            <span style="background-color: #2a9d8f; color: white; padding: 0.15rem 0.5rem; border-radius: 20px; font-size: 0.75rem; font-weight: bold;">Active Pipelines</span>
        </div>
        """, unsafe_allow_html=True)
        
    with m_row1_cols[1]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📅 Deals Closing This Week</div>
            <div class="metric-val" style="color: #e9c46a;">{metrics['deals_closing_this_week']}</div>
            <span style="background-color: #e9c46a; color: #264653; padding: 0.15rem 0.5rem; border-radius: 20px; font-size: 0.75rem; font-weight: bold;">Registration/Docs</span>
        </div>
        """, unsafe_allow_html=True)
        
    with m_row1_cols[2]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">💎 Average Deal Value</div>
            <div class="metric-val" style="color: #457b9d;">{format_inr(metrics['avg_deal_value'])}</div>
            <span style="background-color: #457b9d; color: white; padding: 0.15rem 0.5rem; border-radius: 20px; font-size: 0.75rem; font-weight: bold;">Per Land Transaction</span>
        </div>
        """, unsafe_allow_html=True)
        
    with m_row1_cols[3]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⏱️ Avg Time to Close</div>
            <div class="metric-val" style="color: #457b9d;">{metrics['avg_time_to_close']}</div>
            <span style="background-color: #e2e8f0; color: #1e293b; padding: 0.15rem 0.5rem; border-radius: 20px; font-size: 0.75rem; font-weight: bold;">Lead to Registration</span>
        </div>
        """, unsafe_allow_html=True)
        
    with m_row2_cols[0]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🔄 Conversion Rate</div>
            <div class="metric-val" style="color: #7209b7;">{metrics['conversion_rate']:.1f}%</div>
            <span style="background-color: #7209b7; color: white; padding: 0.15rem 0.5rem; border-radius: 20px; font-size: 0.75rem; font-weight: bold;">Closed Won Ratio</span>
        </div>
        """, unsafe_allow_html=True)
        
    with m_row2_cols[1]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🏆 Top Broker</div>
            <div class="metric-val" style="font-size: 1.3rem; padding: 0.4rem 0; color: #f4a261;">👑 {metrics['top_broker']}</div>
            <span style="background-color: #f4a261; color: white; padding: 0.15rem 0.5rem; border-radius: 20px; font-size: 0.75rem; font-weight: bold;">Highest Deal Count</span>
        </div>
        """, unsafe_allow_html=True)
        
    with m_row2_cols[2]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🔥 Hot Locations</div>
            <div class="metric-val" style="font-size: 0.9rem; padding: 0.65rem 0; color: #264653;">📍 {metrics['hot_locations']}</div>
            <span style="background-color: #264653; color: white; padding: 0.15rem 0.5rem; border-radius: 20px; font-size: 0.75rem; font-weight: bold;">High Demand Areas</span>
        </div>
        """, unsafe_allow_html=True)
        
    with m_row2_cols[3]:
        risk_color = "#e63946" if metrics['deals_at_risk'] > 0 else "#2a9d8f"
        risk_label = "Needs Immediate Action" if metrics['deals_at_risk'] > 0 else "System Clean"
        st.markdown(f"""
        <div class="metric-card" style="border: 1px solid {risk_color};">
            <div class="metric-label">⚠️ Deals at Risk</div>
            <div class="metric-val" style="color: {risk_color};">{metrics['deals_at_risk']}</div>
            <span style="background-color: {risk_color}; color: white; padding: 0.15rem 0.5rem; border-radius: 20px; font-size: 0.75rem; font-weight: bold;">{risk_label}</span>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # 3. Charts and Timeline
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.markdown("### 🗺️ Properties by Location")
        if properties:
            df_props = pd.DataFrame(properties)
            loc_counts = df_props['location'].value_counts()
            st.bar_chart(loc_counts)
        else:
            st.info("No properties found to visualize.")
            
    with chart_col2:
        st.markdown("### 📈 Pipeline Deal Distribution")
        if deals:
            df_deals = pd.DataFrame(deals)
            stage_counts = df_deals['stage'].value_counts()
            st.bar_chart(stage_counts)
        else:
            st.info("No deals in pipeline.")
            
    st.markdown("---")
    st.markdown("### 🕒 Recent Client Activities")
    # Fetch recent logs across database
    conn = database.get_db_connection()
    recent_logs = conn.execute("""
        SELECT a.*, 
               CASE WHEN a.client_type = 'buyer' THEN b.name ELSE s.name END as client_name
        FROM activity_logs a
        LEFT JOIN buyers b ON a.client_type = 'buyer' AND a.client_id = b.id
        LEFT JOIN sellers s ON a.client_type = 'seller' AND a.client_id = s.id
        ORDER BY a.created_at DESC LIMIT 6
    """).fetchall()
    conn.close()
    
    if recent_logs:
        for log in recent_logs:
            log_dict = dict(log)
            st.markdown(f"""
            <div class="timeline-item">
                <span class="timeline-date">{log_dict['created_at']}</span> | 
                <span class="timeline-type">{log_dict['activity_type']}</span> - 
                <strong>{log_dict['client_name']} ({log_dict['client_type'].capitalize()})</strong>
                <div class="timeline-text">{log_dict['note']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent activities recorded.")

# ----------------- TAB 2: CLIENT HUB -----------------
with tabs[1]:
    sub_tab = st.radio("Select Directory", ["Buyers", "Sellers"], horizontal=True)
    
    if sub_tab == "Buyers":
        st.subheader("📋 Buyer Profiles")
        buyer_list = database.get_all_buyers()
        
        # Add new buyer form
        with st.expander("➕ Register New Buyer Inquiry"):
            with st.form("add_buyer_form"):
                b_name = st.text_input("Full Name")
                b_phone = st.text_input("Phone Number")
                b_email = st.text_input("Email")
                b_budget = st.number_input("Budget (in INR)", min_value=0.0, step=500000.0, format="%.2f")
                b_loc = st.text_input("Preferred Location (e.g. Noida Sector 150)")
                b_size = st.text_input("Land Size Requirement (e.g. 200 Sq Yards)")
                b_notes = st.text_area("Inquiry Notes")
                b_status = st.selectbox("Status", ["Active", "Negotiating", "Closed", "Lost"])
                
                submit_b = st.form_submit_button("Save Buyer")
                if submit_b:
                    if b_name.strip() == "":
                        st.error("Name is required.")
                    else:
                        bid = database.add_buyer(b_name, b_phone, b_email, b_budget, b_loc, b_size, b_notes, b_status)
                        # Add activity log
                        database.add_activity("buyer", bid, "Note", f"Inquiry registered. Budget: {format_inr(b_budget)} in {b_loc}.")
                        st.success(f"Buyer {b_name} successfully registered with ID {bid}!")
                        st.rerun()
                        
        if buyer_list:
            df_b = pd.DataFrame(buyer_list)
            # Reformat budget column for display
            df_b['Formatted Budget'] = df_b['budget'].apply(format_inr)
            
            # Display Table
            st.dataframe(
                df_b[['id', 'name', 'phone', 'email', 'Formatted Budget', 'preferred_location', 'land_size_requirement', 'status']],
                use_container_width=True,
                hide_index=True
            )
            
            # Selection for detail view / editing
            st.markdown("### Inspect Buyer & View Activity Timeline")
            selected_buyer_id = st.selectbox("Select Buyer to Inspect", [b['id'] for b in buyer_list], format_func=lambda bid: next(b['name'] for b in buyer_list if b['id'] == bid))
            
            if selected_buyer_id:
                buyer_details = database.get_buyer(selected_buyer_id)
                col_left, col_right = st.columns(2)
                
                with col_left:
                    st.markdown(f"#### Profile: {buyer_details['name']}")
                    st.write(f"**Phone:** {buyer_details['phone']}")
                    st.write(f"**Email:** {buyer_details['email']}")
                    st.write(f"**Budget:** {format_inr(buyer_details['budget'])}")
                    st.write(f"**Preferred Location:** {buyer_details['preferred_location']}")
                    st.write(f"**Size Requirement:** {buyer_details['land_size_requirement']}")
                    st.write(f"**Current Status:** `{buyer_details['status']}`")
                    st.info(f"**Initial Note:** {buyer_details['notes']}")
                    
                    # Delete action (Admin only)
                    if st.session_state.role == "Admin":
                        if st.button("❌ Delete Buyer Record", key="del_buyer_btn"):
                            database.delete_buyer(selected_buyer_id)
                            st.warning("Buyer profile deleted.")
                            st.rerun()
                    else:
                        st.button("❌ Delete Buyer Record (Admin Only)", disabled=True)
                        
                    st.markdown("---")
                    
                    # Collapsible section for AI Insights
                    with st.expander("🤖 AI Insights", expanded=False):
                        insight_key = f"buyer_insights_{buyer_details['id']}"
                        if insight_key not in st.session_state:
                            st.session_state[insight_key] = None
                            
                        if st.session_state[insight_key] is None:
                            buyer_text = (
                                f"Name: {buyer_details['name']}\n"
                                f"Phone: {buyer_details['phone']}\n"
                                f"Email: {buyer_details['email']}\n"
                                f"Budget: {buyer_details['budget']} Rupees\n"
                                f"Preferred Location: {buyer_details['preferred_location']}\n"
                                f"Requirement: {buyer_details['land_size_requirement']}\n"
                                f"Initial Notes: {buyer_details['notes']}\n"
                            )
                            recent_acts = database.get_activities("buyer", buyer_details['id'])
                            if recent_acts:
                                buyer_text += "Recent Activities:\n" + "\n".join(f"- {a['activity_type']}: {a['note']}" for a in recent_acts)
                                
                            if not os.environ.get("GEMINI_API_KEY") and not os.environ.get("DEEPSEEK_API_KEY"):
                                st.session_state[insight_key] = get_mock_buyer_insight(buyer_details)
                            else:
                                with st.spinner("Lead Qualification Agent is generating structured insights..."):
                                    try:
                                        loop = asyncio.new_event_loop()
                                        asyncio.set_event_loop(loop)
                                        data = loop.run_until_complete(agents.run_buyer_insight_agent(buyer_text))
                                        if data:
                                            st.session_state[insight_key] = data
                                        else:
                                            st.session_state[insight_key] = get_mock_buyer_insight(buyer_details)
                                    except Exception as e:
                                        st.warning(f"Failed to generate live insights: {e}. Loading mock fallback.")
                                        st.session_state[insight_key] = get_mock_buyer_insight(buyer_details)
                                        
                        insights = st.session_state[insight_key]
                        if insights:
                            st.markdown("##### 📈 Intent & Likelihood")
                            cols_i1, cols_i2 = st.columns(2)
                            
                            with cols_i1:
                                score_val = insights.get("lead_score", 0)
                                score_color = "#2a9d8f" if score_val >= 80 else ("#e9c46a" if score_val >= 50 else "#e63946")
                                st.markdown(f"""
                                <div style="background-color: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 0.8rem; text-align: center; margin-bottom: 0.5rem;">
                                    <div style="font-size: 0.75rem; color: #8d99ae; font-weight: bold; text-transform: uppercase;">Lead Score</div>
                                    <div style="font-size: 1.8rem; font-weight: 800; color: {score_color};">{score_val}</div>
                                    <div style="font-size: 0.75rem; color: #666; margin-top: 0.2rem;">Intent: <strong>{insights.get('buying_intent', 'N/A')}</strong></div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                            with cols_i2:
                                closing_pct = insights.get("likelihood_of_closing", 0)
                                closing_color = "#2a9d8f" if closing_pct >= 80 else ("#e9c46a" if closing_pct >= 50 else "#e63946")
                                st.markdown(f"""
                                <div style="background-color: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 0.8rem; text-align: center; margin-bottom: 0.5rem;">
                                    <div style="font-size: 0.75rem; color: #8d99ae; font-weight: bold; text-transform: uppercase;">Closing Likelihood</div>
                                    <div style="font-size: 1.8rem; font-weight: 800; color: {closing_color};">{closing_pct}%</div>
                                    <div style="font-size: 0.75rem; color: #666; margin-top: 0.2rem;">Target: <strong>{insights.get('expected_closing_timeline', 'N/A')}</strong></div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                            st.markdown(f"⏱️ **Urgency:** `{insights.get('urgency', 'N/A')}`")
                            st.markdown(f"💵 **Budget Flexibility:** `{insights.get('budget_flexibility', 'Firm')}`")
                            st.markdown(f"📍 **Preferred Locations:** `{insights.get('preferred_locations', 'N/A')}`")
                            st.markdown(f"🎯 **Best Matches:** `{insights.get('best_matching_properties', 'N/A')}`")
                            st.markdown(f"⚠️ **Potential Risks:** *{insights.get('potential_risks', 'None')}*")
                            
                            st.markdown(f"""
                            <div style="background-color: rgba(65, 90, 119, 0.1); border: 1px solid rgba(65, 90, 119, 0.25); border-radius: 8px; padding: 0.8rem; margin-top: 0.8rem;">
                                <strong style="font-size: 0.8rem; color: #415a77; text-transform: uppercase;">Suggested Next Action</strong>
                                <div style="font-size: 1.05rem; font-weight: 700; color: #1b263b; margin-top: 0.15rem;">👉 {insights.get('recommended_next_action', 'N/A')}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if os.environ.get("GEMINI_API_KEY") or os.environ.get("DEEPSEEK_API_KEY"):
                                if st.button("🔄 Refresh Insights", key=f"refresh_insights_{buyer_details['id']}"):
                                    st.session_state[insight_key] = None
                                    st.rerun()
                                    
                    st.markdown("---")
                    
                    # Collapsible section for AI Communication Assistant
                    with st.expander("📬 AI Communication Assistant", expanded=False):
                        comm_tabs = st.tabs(["💬 WhatsApp", "📧 Email", "📞 Call Script", "🤝 Meeting Agenda", "⚖️ Negotiation Talking Points"])
                        comm_types = ["WhatsApp Message", "Email", "Call Script", "Meeting Agenda", "Negotiation Talking Points"]
                        
                        for idx, tab in enumerate(comm_tabs):
                            with tab:
                                comm_type = comm_types[idx]
                                comm_key = f"comm_buyer_{buyer_details['id']}_{comm_type}"
                                if comm_key not in st.session_state:
                                    st.session_state[comm_key] = None
                                    
                                if st.session_state[comm_key] is None:
                                    if not os.environ.get("GEMINI_API_KEY") and not os.environ.get("DEEPSEEK_API_KEY"):
                                        st.session_state[comm_key] = get_mock_communication_draft("buyer", buyer_details['name'], comm_type)
                                    else:
                                        with st.spinner(f"Generating personalized {comm_type}..."):
                                            try:
                                                loop = asyncio.new_event_loop()
                                                asyncio.set_event_loop(loop)
                                                st.session_state[comm_key] = loop.run_until_complete(
                                                    agents.run_followup_generator_agent("buyer", buyer_details['id'], comm_type)
                                                )
                                            except Exception as e:
                                                st.session_state[comm_key] = f"Error: {e}\n\nFallback:\n{get_mock_communication_draft('buyer', buyer_details['name'], comm_type)}"
                                
                                st.markdown(f"**Personalized {comm_type} Draft:**")
                                st.code(st.session_state[comm_key], language="markdown")
                                
                                if st.button(f"🔄 Regenerate {comm_type}", key=f"regen_buyer_{buyer_details['id']}_{idx}"):
                                    st.session_state[comm_key] = None
                                    st.rerun()
                        
                with col_right:
                    st.markdown("#### Activity Timeline & Actions")
                    
                    # Activity timeline additions
                    with st.form("add_buyer_activity_form"):
                        act_type = st.selectbox("Log Activity", ["Call", "Meeting", "Site Visit", "Note"])
                        act_note = st.text_area("Activity Details")
                        submit_act = st.form_submit_button("Post to Timeline")
                        if submit_act and act_note.strip():
                            database.add_activity("buyer", selected_buyer_id, act_type, act_note)
                            st.success("Activity logged.")
                            st.rerun()
                            
                    # List activities
                    acts = database.get_activities("buyer", selected_buyer_id)
                    if acts:
                        for a in acts:
                            st.markdown(f"""
                            <div class="timeline-item">
                                <span class="timeline-date">{a['created_at']}</span> | 
                                <span class="timeline-type">{a['activity_type']}</span>
                                <div class="timeline-text">{a['note']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No timeline logs yet.")
        else:
            st.info("No buyers registered yet.")

    elif sub_tab == "Sellers":
        st.subheader("📋 Seller Profiles")
        seller_list = database.get_all_sellers()
        
        # Add new seller form
        with st.expander("➕ Register New Seller Property Listing"):
            with st.form("add_seller_form"):
                s_name = st.text_input("Full Name")
                s_phone = st.text_input("Phone Number")
                s_email = st.text_input("Email")
                s_price = st.number_input("Asking Price (in INR)", min_value=0.0, step=500000.0, format="%.2f")
                s_loc = st.text_input("Property Location (e.g. Whitefield Bengaluru)")
                s_area = st.text_input("Land Area (e.g. 2400 Sq Ft)")
                s_notes = st.text_area("Listing Notes")
                s_status = st.selectbox("Status", ["Active", "Sold", "Inactive"])
                
                submit_s = st.form_submit_button("Save Seller")
                if submit_s:
                    if s_name.strip() == "":
                        st.error("Name is required.")
                    else:
                        sid = database.add_seller(s_name, s_phone, s_email, s_loc, s_area, s_price, s_notes, s_status)
                        # Auto register in property database
                        pid = database.add_property(s_name, s_loc, s_area, s_price, s_notes, "Available" if s_status == "Active" else "Sold")
                        # Add activity log
                        database.add_activity("seller", sid, "Note", f"Seller listing registered. Land: {s_area} in {s_loc} (Auto Property ID: {pid}).")
                        st.success(f"Seller {s_name} successfully registered with ID {sid}!")
                        st.rerun()
                        
        if seller_list:
            df_s = pd.DataFrame(seller_list)
            # Reformat asking price column for display
            df_s['Formatted Asking Price'] = df_s['asking_price'].apply(format_inr)
            
            # Display Table
            st.dataframe(
                df_s[['id', 'name', 'phone', 'email', 'Formatted Asking Price', 'property_location', 'land_area', 'status']],
                use_container_width=True,
                hide_index=True
            )
            
            # Selection for detail view / editing
            st.markdown("### Inspect Seller & View Activity Timeline")
            selected_seller_id = st.selectbox("Select Seller to Inspect", [s['id'] for s in seller_list], format_func=lambda sid: next(s['name'] for s in seller_list if s['id'] == sid))
            
            if selected_seller_id:
                seller_details = database.get_seller(selected_seller_id)
                col_left, col_right = st.columns(2)
                
                with col_left:
                    st.markdown(f"#### Profile: {seller_details['name']}")
                    st.write(f"**Phone:** {seller_details['phone']}")
                    st.write(f"**Email:** {seller_details['email']}")
                    st.write(f"**Asking Price:** {format_inr(seller_details['asking_price'])}")
                    st.write(f"**Property Location:** {seller_details['property_location']}")
                    st.write(f"**Land Area:** {seller_details['land_area']}")
                    st.write(f"**Current Status:** `{seller_details['status']}`")
                    st.info(f"**Initial Note:** {seller_details['notes']}")
                    
                    # Delete action (Admin only)
                    if st.session_state.role == "Admin":
                        if st.button("❌ Delete Seller Record", key="del_seller_btn"):
                            database.delete_seller(selected_seller_id)
                            st.warning("Seller profile deleted.")
                            st.rerun()
                    else:
                        st.button("❌ Delete Seller Record (Admin Only)", disabled=True)
                        
                    st.markdown("---")
                    
                    # Collapsible section for AI Communication Assistant
                    with st.expander("📬 AI Communication Assistant", expanded=False):
                        comm_tabs = st.tabs(["💬 WhatsApp", "📧 Email", "📞 Call Script", "🤝 Meeting Agenda", "⚖️ Negotiation Talking Points"])
                        comm_types = ["WhatsApp Message", "Email", "Call Script", "Meeting Agenda", "Negotiation Talking Points"]
                        
                        for idx, tab in enumerate(comm_tabs):
                            with tab:
                                comm_type = comm_types[idx]
                                comm_key = f"comm_seller_{seller_details['id']}_{comm_type}"
                                if comm_key not in st.session_state:
                                    st.session_state[comm_key] = None
                                    
                                if st.session_state[comm_key] is None:
                                    if not os.environ.get("GEMINI_API_KEY") and not os.environ.get("DEEPSEEK_API_KEY"):
                                        st.session_state[comm_key] = get_mock_communication_draft("seller", seller_details['name'], comm_type)
                                    else:
                                        with st.spinner(f"Generating personalized {comm_type}..."):
                                            try:
                                                loop = asyncio.new_event_loop()
                                                asyncio.set_event_loop(loop)
                                                st.session_state[comm_key] = loop.run_until_complete(
                                                    agents.run_followup_generator_agent("seller", seller_details['id'], comm_type)
                                                )
                                            except Exception as e:
                                                st.session_state[comm_key] = f"Error: {e}\n\nFallback:\n{get_mock_communication_draft('seller', seller_details['name'], comm_type)}"
                                
                                st.markdown(f"**Personalized {comm_type} Draft:**")
                                st.code(st.session_state[comm_key], language="markdown")
                                
                                if st.button(f"🔄 Regenerate {comm_type}", key=f"regen_seller_{seller_details['id']}_{idx}"):
                                    st.session_state[comm_key] = None
                                    st.rerun()
                        
                with col_right:
                    st.markdown("#### Activity Timeline & Actions")
                    
                    # Activity timeline additions
                    with st.form("add_seller_activity_form"):
                        act_type = st.selectbox("Log Activity", ["Call", "Meeting", "Site Visit", "Note"])
                        act_note = st.text_area("Activity Details")
                        submit_act = st.form_submit_button("Post to Timeline")
                        if submit_act and act_note.strip():
                            database.add_activity("seller", selected_seller_id, act_type, act_note)
                            st.success("Activity logged.")
                            st.rerun()
                            
                    # List activities
                    acts = database.get_activities("seller", selected_seller_id)
                    if acts:
                        for a in acts:
                            st.markdown(f"""
                            <div class="timeline-item">
                                <span class="timeline-date">{a['created_at']}</span> | 
                                <span class="timeline-type">{a['activity_type']}</span>
                                <div class="timeline-text">{a['note']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No timeline logs yet.")
        else:
            st.info("No sellers registered yet.")

# ----------------- TAB 3: PROPERTY CATALOG -----------------
with tabs[2]:
    st.subheader("🏔️ Available Lands & Properties")
    
    props = database.get_all_properties()
    
    # Filter Section
    with st.expander("🔍 Search & Filter Properties", expanded=True):
        f_cols = st.columns(3)
        with f_cols[0]:
            f_loc = st.text_input("Filter Location", "")
        with f_cols[1]:
            f_max_price = st.number_input("Max Budget (INR)", min_value=0.0, step=1000000.0, value=0.0)
        with f_cols[2]:
            f_status = st.selectbox("Property Status", ["All", "Available", "Sold"])
            
    filtered_props = props
    if f_loc:
        filtered_props = [p for p in filtered_props if f_loc.lower() in p['location'].lower()]
    if f_max_price > 0.0:
        filtered_props = [p for p in filtered_props if p['price'] <= f_max_price]
    if f_status != "All":
        filtered_props = [p for p in filtered_props if p['status'] == f_status]
        
    # Create Property Grid
    if filtered_props:
        grid_cols = st.columns(2)
        for i, p in enumerate(filtered_props):
            col_target = grid_cols[i % 2]
            with col_target:
                status_color = "green" if p['status'] == "Available" else "red"
                st.markdown(f"""
                <div style="background-color: rgba(255,255,255,0.05); padding: 1.25rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 1rem;">
                    <h4>📍 {p['location']}</h4>
                    <p style="font-size: 1.1rem; color: #415a77; font-weight: bold; margin: 0.2rem 0;">Price: {format_inr(p['price'])} | Area: {p['area']}</p>
                    <p style="color: grey; font-size: 0.85rem; margin-bottom: 0.5rem;">Owner: {p['owner']} | Property ID: #{p['id']}</p>
                    <p style="font-size: 0.9rem; margin-bottom: 0.5rem;">{p['description']}</p>
                    <span style="background-color: {status_color}; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: bold;">{p['status']}</span>
                </div>
                """, unsafe_allow_html=True)
                st.write("")
    else:
        st.info("No properties matching the filters.")

# ----------------- TAB 4: KANBAN DEAL PIPELINE -----------------
with tabs[3]:
    st.subheader("⛓️ Deal Pipeline")
    
    stages = ["New Lead", "Contacted", "Site Visit", "Negotiation", "Documentation", "Registration", "Closed"]
    deal_list = database.get_all_deals()
    
    # Register New Deal Form
    with st.expander("➕ Register New Deal Flow"):
        with st.form("register_deal_form"):
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                buyer_opt = database.get_all_buyers()
                select_buyer = st.selectbox("Buyer", [b['id'] for b in buyer_opt], format_func=lambda bid: next(b['name'] for b in buyer_opt if b['id'] == bid))
                
                seller_opt = database.get_all_sellers()
                select_seller = st.selectbox("Seller", [s['id'] for s in seller_opt], format_func=lambda sid: next(s['name'] for s in seller_opt if s['id'] == sid))
            with col_d2:
                prop_opt = database.get_all_properties()
                select_prop = st.selectbox("Property ID", [p['id'] for p in prop_opt], format_func=lambda pid: f"Property #{pid} ({next(p['location'] for p in prop_opt if p['id'] == pid)})")
                
                select_broker = st.selectbox("Handling Broker", ["Rohan Sharma", "Aarav Kapoor", "Neha Sen"])
                select_stage = st.selectbox("Initial Pipeline Stage", stages)
                
            submit_deal = st.form_submit_button("Launch Deal")
            if submit_deal:
                did = database.add_deal(select_buyer, select_seller, select_prop, select_broker, select_stage)
                st.success(f"Deal successfully launched under ID #{did}!")
                st.rerun()
                
    # Kanban display
    st.markdown("#### Click Deal Dropdown to Update Pipeline Stage in Real-time")
    
    kanban_cols = st.columns(len(stages))
    
    for idx, stage in enumerate(stages):
        with kanban_cols[idx]:
            st.markdown(f"""
            <div style="background-color: rgba(65, 90, 119, 0.1); padding: 0.5rem; border-radius: 8px; text-align: center; border-bottom: 3px solid #415a77; margin-bottom: 1rem;">
                <strong style="color: #415a77; font-size: 0.85rem;">{stage.upper()}</strong>
            </div>
            """, unsafe_allow_html=True)
            
            stage_deals = [d for d in deal_list if d['stage'] == stage]
            
            if stage_deals:
                for deal in stage_deals:
                    with st.container():
                        st.markdown(f"""
                        <div class="kanban-card">
                            <div class="kanban-title">🤝 Deal #{deal['id']}</div>
                            <div class="kanban-subtitle">
                                <strong>Buyer:</strong> {deal['buyer_name']}<br/>
                                <strong>Seller:</strong> {deal['seller_name']}<br/>
                                <strong>Loc:</strong> {deal['property_location']}<br/>
                                <strong>Price:</strong> {format_inr(deal['property_price'] or 0.0)}<br/>
                                <strong>Agent:</strong> {deal['broker_name']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Stage update dropdown
                        new_stage = st.selectbox(
                            "Move to:",
                            stages,
                            index=stages.index(stage),
                            key=f"deal_stage_{deal['id']}",
                            label_visibility="collapsed"
                        )
                        if new_stage != stage:
                            database.update_deal_stage_db(deal['id'], new_stage)
                            st.toast(f"Deal #{deal['id']} moved to {new_stage}!")
                            st.rerun()
            else:
                st.markdown("<p style='text-align: center; color: grey; font-size: 0.8rem; margin: 1rem 0;'>No deals</p>", unsafe_allow_html=True)

# ----------------- TAB 5: AI COMMAND CENTER -----------------
with tabs[4]:
    st.subheader("🤖 AI Command Center")
    st.markdown("Ask natural language commands to consult the multi-agent network. The Orchestrator Agent will automatically coordinate specialized agents and access real-time database tools.")

    # Quick action helper buttons
    st.markdown("##### 💡 Suggested Prompts")
    q_cols1 = st.columns(4)
    q_cols2 = st.columns(4)
    
    suggested_prompt = ""
    
    with q_cols1[0]:
        if st.button("🔍 Gurgaon Land under 2 Cr", use_container_width=True):
            suggested_prompt = "Find buyers interested in Gurgaon under ₹2 Crore."
    with q_cols1[1]:
        if st.button("🎯 Match Buyers & Properties", use_container_width=True):
            suggested_prompt = "Match buyers with suitable properties."
    with q_cols1[2]:
        if st.button("⚠️ Deals needing attention today", use_container_width=True):
            suggested_prompt = "Which deals need my attention today?"
    with q_cols1[3]:
        if st.button("🕒 Buyers with pending follow-ups", use_container_width=True):
            suggested_prompt = "Show buyers with pending follow-ups."
            
    with q_cols2[0]:
        if st.button("💰 Which properties are overpriced?", use_container_width=True):
            suggested_prompt = "Which properties are overpriced?"
    with q_cols2[1]:
        if st.button("📊 Summarize today's business", use_container_width=True):
            suggested_prompt = "Summarize today's business."
    with q_cols2[2]:
        if st.button("💤 Show inactive clients", use_container_width=True):
            suggested_prompt = "Show inactive clients."
    with q_cols2[3]:
        if st.button("📈 Deals likely to close this week", use_container_width=True):
            suggested_prompt = "Which deals are most likely to close this week?"

    # We store the selected suggested prompt in session state to populate the text area
    if "prompt_input" not in st.session_state:
        st.session_state.prompt_input = ""
        
    if suggested_prompt:
        st.session_state.prompt_input = suggested_prompt
        
    user_query = st.text_area(
        "Enter your command for the AI Command Center:",
        value=st.session_state.prompt_input,
        placeholder="e.g. Find buyers for the ECR Chennai property.",
        height=100
    )
    
    # We clear the input button click state or handle running
    if st.button("💬 Send Command", type="primary", use_container_width=True):
        if not user_query.strip():
            st.warning("Please enter a command.")
        elif not os.environ.get("GEMINI_API_KEY") and not os.environ.get("DEEPSEEK_API_KEY"):
            st.error("Cannot run without GEMINI_API_KEY or DEEPSEEK_API_KEY. Please set the key.")
        else:
            with st.spinner("Orchestrator Agent is analyzing query and routing to sub-agents..."):
                try:
                    # Clear logs before run
                    database.clear_tool_logs()
                    
                    # Execute orchestrator
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    response_text = loop.run_until_complete(agents.run_orchestrator_agent(user_query))
                    
                    # Retrieve metrics
                    agents_used = list(dict.fromkeys(agents.called_agents)) # remove duplicates
                    mcp_tools_used = database.get_recent_tool_calls()
                    
                    st.markdown("---")
                    st.markdown("### 📑 AI Command Center Execution Report")
                    
                    # Render user message
                    st.markdown(f"""
                    <div style="background-color: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 1rem;">
                        <strong>User:</strong> {user_query}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Render audit trail
                    audit_cols = st.columns(2)
                    with audit_cols[0]:
                        st.markdown("#### 🤖 Agents Engaged")
                        if agents_used:
                            for agent_name in agents_used:
                                st.markdown(f"- ✅ **{agent_name}**")
                        else:
                            st.markdown("*No sub-agents called. Answered by Orchestrator directly.*")
                            
                    with audit_cols[1]:
                        st.markdown("#### 🔌 MCP Tools Invoked")
                        if mcp_tools_used:
                            for tool_name in mcp_tools_used:
                                st.markdown(f"- 🛠️ `mcp_server.{tool_name}()`")
                        else:
                            st.markdown("*No database tools accessed.*")
                            
                    st.markdown("---")
                    st.markdown("#### 💬 AI Response")
                    st.markdown(response_text)
                    
                except Exception as e:
                    st.error(f"Orchestration execution failed: {e}")

