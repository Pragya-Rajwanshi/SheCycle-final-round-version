"""
app.py - Main Entrypoint & Navigation for SheCycle
IEEE WIE HackEarth Hackathon | Theme: Sustainability & Climate
Pilot Location: Meerut, Uttar Pradesh, India
"""

import streamlit as st
import pandas as pd
import os

# 1. Page Configuration (Must be first Streamlit command)
st.set_page_config(
    page_title="SheCycle: Women-Led Smart E-Waste Management",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Database and Module Imports
import db
from services import (
    calculate_environmental_impact,
    REVENUE_SPLIT,
    SCRAP_RATES
)
from modules.ui_common import (
    inject_custom_css,
    t,
    get_status_badge_html
)
from modules.portal_citizen import render_citizen_portal
from modules.portal_shg import render_shg_portal
from modules.portal_admin import render_admin_portal
from modules.portal_roadmap import render_roadmap_page

# 3. Initialize Database on startup
db.init_db()

# 4. Inject High-Polish Brand Theme CSS
inject_custom_css()


# ==========================================
# SIDEBAR NAVIGATION & DEMO CONTROLS
# ==========================================

st.sidebar.markdown(
    """
    <div style="text-align:center; padding:12px 0 6px 0;">
        <span style="font-size:2.4rem;">♻️</span>
        <h2 style="margin:2px 0 0 0; color:#3B2F72; font-weight:800; font-size:1.6rem;">SheCycle</h2>
        <span style="font-size:0.75rem; color:#E8318A; font-weight:700; text-transform:uppercase; letter-spacing:1px;">
            Women-Led Circular Economy
        </span>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("---")

# Portal Navigation
nav_options = [
    "🏠 Home & Impact Hub",
    "👤 Citizen Portal (Request Pickup)",
    "👩‍🦰 Women SHG Partner Portal",
    "🏛️ Municipal Admin Dashboard",
    "🗺️ Pilot Roadmap & Compliance"
]

# Allow programmatically switching page
if "nav_page" not in st.session_state:
    st.session_state["nav_page"] = nav_options[0]

nav_selection = st.sidebar.radio(
    "Select Portal / Role:",
    nav_options,
    index=nav_options.index(st.session_state["nav_page"]) if st.session_state["nav_page"] in nav_options else 0,
    key="main_nav_radio"
)
st.session_state["nav_page"] = nav_selection

# DEMO ASSISTANT PANEL (FOR HACKATHON JUDGES)
st.sidebar.markdown("---")
with st.sidebar.expander("⚡ **Judge Demo Mode (Credentials)**", expanded=True):
    st.markdown(
        """
        <div style="font-size:0.8rem; color:#334155; line-height:1.4;">
            <strong>🏛️ Municipal Admin:</strong><br/>
            • Password: <code>meerut2026</code><br/><br/>
            <strong>👩‍🦰 Approved SHGs (PIN: 1234):</strong><br/>
            • <code>NULM-2024-88</code> (Maa Durga - Urban)<br/>
            • <code>NRLM-1024</code> (Ekta Sakhi - Rural)<br/><br/>
            <strong>⏳ Pending SHG (Approval Test):</strong><br/>
            • <code>NULM-2025-12</code> (Nav Chetna)<br/><br/>
            <strong>🔍 Citizen Tracking:</strong><br/>
            • ID: <code>EW-00001</code> | Last 4: <code>3210</code><br/>
            • ID: <code>EW-00002</code> | Last 4: <code>5678</code>
        </div>
        """,
        unsafe_allow_html=True
    )

# RESET DEMO DATA BUTTON
if st.sidebar.button("🔄 Reset Demo Database", use_container_width=True, help="Wipes and reseeds realistic 60-day Meerut dataset with 28 requests & 4 SHGs."):
    db.init_db(force_reseed=True)
    st.session_state["logged_in_shg_id"] = None
    st.session_state["admin_logged_in"] = False
    st.sidebar.success("Database restored to pristine demo state!")
    st.rerun()

# OFFICIAL GOVERNMENT REFERENCES
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style="font-size:0.75rem; color:#64748B;">
        <strong>Official Registries & Regulators:</strong><br/>
        • <a href="https://nulm.gov.in/" target="_blank">DAY-NULM Portal (Urban)</a><br/>
        • <a href="https://aajeevika.gov.in/" target="_blank">DAY-NRLM Aajeevika (Rural)</a><br/>
        • <a href="https://cpcb.nic.in/e-waste/" target="_blank">CPCB E-Waste EPR Portal</a><br/>
        • <em>Pilot City: Meerut, UP (Nagar Nigam)</em>
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================
# LANDING / HOME PAGE VIEW
# ==========================================

def render_home_page():
    """Renders the high-impact landing page."""
    kpis = db.get_kpi_summary()

    # Hero Banner
    st.markdown(
        """
        <div class="hero-banner">
            <div class="hero-title">♻️ SheCycle</div>
            <div class="hero-tagline">Transforming E-Waste Management into Women-Led Prosperity</div>
            <p style="font-size:0.95rem; max-width:850px; color:#F1F5F9; margin-bottom:12px; line-height:1.5;">
                An inclusive municipal circular-economy platform in Meerut, connecting citizens with verified
                women Self-Help Groups (DAY-NRLM / DAY-NULM) for dignified green livelihoods, safe doorstep e-waste aggregation,
                and verifiable pickup-to-recycler compliance.
            </p>
            <div class="hero-badges">
                <span class="hero-badge">📍 Meerut Municipal Cluster Pilot</span>
                <span class="hero-badge">🌱 IEEE WIE HackEarth 2026 Finalist</span>
                <span class="hero-badge">🛡️ Aligned with DPDP Act 2023 & E-Waste Rules 2022</span>
                <span class="hero-badge">⚖️ 75% Direct Livelihood Share to Women</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 4 LIVE IMPACT COUNTERS FROM DATABASE
    st.markdown("### 🌍 Live City Impact Counters")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        label="Collected E-Waste Tonnage",
        value=f"{kpis['total_kg']} kg",
        help="Verified weight of e-waste safely aggregated by SHGs and diverted from unscientific burning."
    )
    c2.metric(
        label="Active Verified SHGs",
        value=f"{kpis['active_shgs']} Groups",
        delta=f"+{kpis['pending_shgs']} Pending Scrutiny",
        delta_color="inverse",
        help="Government verified women groups actively collecting in Meerut wards."
    )
    c3.metric(
        label="Pickups Completed / Active",
        value=f"{kpis['completed_pickups']} of {kpis['total_requests']}",
        help="Doorstep collections fulfilled through the verified compliance pipeline."
    )
    c4.metric(
        label="Est. Paid to Women SHGs",
        value=f"₹{kpis['total_shg_earnings']:,.0f}",
        help="Net 75% scrap revenue share credited directly to SHG bank accounts via DBT."
    )

    # Extra Environmental Impact Highlights
    st.markdown(
        f"""
        <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:10px; padding:12px 20px; margin:16px 0 28px 0; display:flex; justify-content:space-around; align-items:center; flex-wrap:wrap; gap:16px;">
            <div style="text-align:center;">
                <span style="font-size:1.4rem; font-weight:800; color:#166534;">{kpis['co2_avoided_kg']} kg</span><br/>
                <span style="font-size:0.75rem; color:#15803D; font-weight:600; text-transform:uppercase;">CO₂ Emissions Avoided</span>
            </div>
            <div style="height:35px; width:1px; background:#BBF7D0;"></div>
            <div style="text-align:center;">
                <span style="font-size:1.4rem; font-weight:800; color:#166534;">{kpis['heavy_metals_prevented_g']} g</span><br/>
                <span style="font-size:0.75rem; color:#15803D; font-weight:600; text-transform:uppercase;">Toxic Heavy Metals Diverted</span>
            </div>
            <div style="height:35px; width:1px; background:#BBF7D0;"></div>
            <div style="text-align:center;">
                <span style="font-size:1.4rem; font-weight:800; color:#166534;">{kpis['total_green_credits']}</span><br/>
                <span style="font-size:0.75rem; color:#15803D; font-weight:600; text-transform:uppercase;">Citizen Green Credits Issued</span>
            </div>
            <div style="height:35px; width:1px; background:#BBF7D0;"></div>
            <div style="text-align:center;">
                <span style="font-size:1.4rem; font-weight:800; color:#166534;">~{kpis['trees_equivalent']}</span><br/>
                <span style="font-size:0.75rem; color:#15803D; font-weight:600; text-transform:uppercase;">Tree Carbon Absorption Equivalent</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 4-STEP "HOW IT WORKS" VISUAL PROCESS
    st.markdown("### 🔄 How SheCycle Works: Transparent 4-Stage Lifecycle")

    s1, s2, s3, s4 = st.columns(4)

    with s1:
        st.markdown(
            """
            <div class="she-card she-card-green" style="height:230px;">
                <span style="font-size:1.8rem;">📱</span>
                <h4 style="margin:8px 0 4px 0; color:#0D9488;">1. Citizen Request</h4>
                <p style="font-size:0.85rem; color:#475569; line-height:1.4;">
                    Citizens submit doorstep pickup requests in under 60 seconds with no complex passwords.
                    Data is protected under DPDP Act principles.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with s2:
        st.markdown(
            """
            <div class="she-card she-card-indigo" style="height:230px;">
                <span style="font-size:1.8rem;">👩‍🦰</span>
                <h4 style="margin:8px 0 4px 0; color:#3B2F72;">2. SHG Collection</h4>
                <p style="font-size:0.85rem; color:#475569; line-height:1.4;">
                    Verified women SHGs operating in their own wards accept jobs, verify weight with digital scales, and follow mandatory PPE checklists.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with s3:
        st.markdown(
            """
            <div class="she-card she-card-highlight" style="height:230px;">
                <span style="font-size:1.8rem;">🔬</span>
                <h4 style="margin:8px 0 4px 0; color:#E8318A;">3. Safe Aggregation</h4>
                <p style="font-size:0.85rem; color:#475569; line-height:1.4;">
                    Basic non-hazardous fraction segregation (metals, plastics, boards).
                    Critical lithium batteries remain sealed in fire-retardant containers.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with s4:
        st.markdown(
            """
            <div class="she-card she-card-green" style="height:230px;">
                <span style="font-size:1.8rem;">🚛</span>
                <h4 style="margin:8px 0 4px 0; color:#0D9488;">4. Authorised Recycling</h4>
                <p style="font-size:0.85rem; color:#475569; line-height:1.4;">
                    Aggregated scrap is handed over to CPCB-authorised recyclers under legal challan.
                    75% net value credited directly to SHG bank accounts.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    # ROLE SELECTOR CARDS
    st.markdown("### 🚪 Choose Your Portal")

    r1, r2, r3 = st.columns(3)

    with r1:
        st.markdown(
            """
            <div class="she-card she-card-green">
                <h4 style="margin-top:0; color:#0D9488;">👤 For Citizens</h4>
                <p style="font-size:0.85rem; color:#475569;">
                    Have obsolete phones, chargers, or laptops? Request free doorstep collection, earn Green Credits, and track your request status.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("🚀 Go to Citizen Portal", use_container_width=True, type="primary"):
            st.session_state["nav_page"] = "👤 Citizen Portal (Request Pickup)"
            st.rerun()

    with r2:
        st.markdown(
            """
            <div class="she-card she-card-highlight">
                <h4 style="margin-top:0; color:#E8318A;">👩‍🦰 For Women SHGs</h4>
                <p style="font-size:0.85rem; color:#475569;">
                    DAY-NRLM / NULM registered Self-Help Groups: view open jobs in your ward, record verified collection weights, and track your earnings.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("🤝 Open SHG Portal", use_container_width=True):
            st.session_state["nav_page"] = "👩‍🦰 Women SHG Partner Portal"
            st.rerun()

    with r3:
        st.markdown(
            """
            <div class="she-card she-card-indigo">
                <h4 style="margin-top:0; color:#3B2F72;">🏛️ For Municipal Admin</h4>
                <p style="font-size:0.85rem; color:#475569;">
                    Urban Local Bodies & CPCB officials: scrutinize SHG applications, review real-time tonnage analytics, and download compliance audit trails.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("📊 Access Admin Dashboard", use_container_width=True):
            st.session_state["nav_page"] = "🏛️ Municipal Admin Dashboard"
            st.rerun()


# ==========================================
# ROUTER & DISPATCHER
# ==========================================

if nav_selection == "🏠 Home & Impact Hub":
    render_home_page()
elif nav_selection == "👤 Citizen Portal (Request Pickup)":
    render_citizen_portal()
elif nav_selection == "👩‍🦰 Women SHG Partner Portal":
    render_shg_portal()
elif nav_selection == "🏛️ Municipal Admin Dashboard":
    render_admin_portal()
elif nav_selection == "🗺️ Pilot Roadmap & Compliance":
    render_roadmap_page()
