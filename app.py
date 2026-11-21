"""
app.py - Main Entrypoint & Navigation for SheCycle
IEEE WIE HackEarth Hackathon | Theme: Sustainability & Climate
Pilot Location: Meerut, Uttar Pradesh, India
Team: Zero Toxic (Pragya Rajwanshi, Rohit Kumar)
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
    get_status_badge_html,
    render_html,
    go_to
)
from modules.portal_citizen import render_citizen_portal
from modules.portal_shg import render_shg_portal
from modules.portal_admin import render_admin_portal
from modules.portal_roadmap import render_roadmap_page
from modules.portal_help import render_help_page

# 3. Initialize Database on startup
db.init_db()

# 4. Initialize & Inject Theme (Light / Dark Mode)
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False

# ==========================================
# SIDEBAR CONTROLS & NAVIGATION
# ==========================================

# Dark Mode Toggle at top of sidebar
dark_mode = st.sidebar.toggle(
    "🌙 Dark Mode",
    value=st.session_state["dark_mode"],
    key="dark_mode_toggle"
)
st.session_state["dark_mode"] = dark_mode
inject_custom_css(dark_mode=dark_mode)

# Sidebar Branding
render_html(
    """
    <div style="text-align:center; padding:10px 0 8px 0;">
        <span style="font-size:2.3rem;">♻️</span>
        <h2 style="margin:2px 0 0 0; color:var(--primary); font-weight:800; font-size:1.6rem; letter-spacing:-0.02em;">SheCycle</h2>
        <span style="font-size:0.75rem; color:var(--accent); font-weight:700; text-transform:uppercase; letter-spacing:1.2px;">
            Women-Led Circular Economy
        </span>
    </div>
    """
)

st.sidebar.markdown("---")

# Portal Navigation Options
nav_options = [
    "🏠 Home & Impact Hub",
    "👤 Citizen Portal (Request Pickup)",
    "👩‍🦰 Women SHG Partner Portal",
    "🏛️ Municipal Admin Dashboard",
    "🗺️ Pilot Roadmap & Compliance",
    "❓ Help & Guide"
]

if "main_nav_radio" not in st.session_state:
    st.session_state["main_nav_radio"] = nav_options[0]

nav_selection = st.sidebar.radio(
    "Select Portal / Role:",
    nav_options,
    key="main_nav_radio"
)
st.session_state["nav_page"] = nav_selection

# DEMO ASSISTANT PANEL (FOR HACKATHON JUDGES)
st.sidebar.markdown("---")
with st.sidebar.expander("⚡ **Judge Demo Mode (Credentials)**", expanded=True):
    render_html(
        """
        <div style="font-size:0.8rem; color:var(--muted); line-height:1.5;">
            <strong style="color:var(--text);">🏛️ Municipal Admin:</strong><br/>
            • Password: <code>meerut2026</code><br/><br/>
            <strong style="color:var(--text);">👩‍🦰 Approved SHGs (PIN: 1234):</strong><br/>
            • <code>NULM-2024-88</code> (Maa Durga - Urban)<br/>
            • <code>NRLM-1024</code> (Ekta Sakhi - Rural)<br/><br/>
            <strong style="color:var(--text);">⏳ Pending SHG (Approval Test):</strong><br/>
            • <code>NULM-2025-12</code> (Nav Chetna)<br/><br/>
            <strong style="color:var(--text);">🔍 Citizen Tracking:</strong><br/>
            • ID: <code>EW-00001</code> | Last 4: <code>3210</code><br/>
            • ID: <code>EW-00002</code> | Last 4: <code>5678</code>
        </div>
        """
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
render_html(
    """
    <div style="font-size:0.75rem; color:var(--muted); line-height:1.5;">
        <strong style="color:var(--text);">Official Registries & Regulators:</strong><br/>
        • <a href="https://nulm.gov.in/" target="_blank" style="color:var(--primary); font-weight:600; text-decoration:none;">DAY-NULM Portal (Urban)</a><br/>
        • <a href="https://aajeevika.gov.in/" target="_blank" style="color:var(--primary); font-weight:600; text-decoration:none;">DAY-NRLM Aajeevika (Rural)</a><br/>
        • <a href="https://cpcb.nic.in/e-waste/" target="_blank" style="color:var(--primary); font-weight:600; text-decoration:none;">CPCB E-Waste EPR Portal</a><br/>
        • <em>Pilot City: Meerut, UP (Nagar Nigam)</em>
    </div>
    """
)


# ==========================================
# LANDING / HOME PAGE VIEW
# ==========================================

def render_home_page():
    """Renders the high-impact landing page."""
    kpis = db.get_kpi_summary()

    # Hero Banner
    render_html(
        """
        <div class="hero-banner">
            <div class="hero-title">♻️ SheCycle</div>
            <div class="hero-tagline">Transforming Waste Management into Women-Led Prosperity</div>
            <p style="font-size:0.98rem; max-width:860px; color:#F1EDFA; margin-bottom:16px; line-height:1.55;">
                An inclusive municipal circular-economy platform in Meerut, connecting citizens with verified
                women Self-Help Groups (DAY-NRLM / DAY-NULM) for dignified green livelihoods, safe doorstep e-waste aggregation,
                and verifiable pickup-to-recycler statutory compliance.
            </p>
            <div class="hero-badges">
                <span class="hero-badge">📍 Meerut Municipal Cluster Pilot</span>
                <span class="hero-badge">🌱 IEEE WIE HackEarth 2026 Finalist</span>
                <span class="hero-badge">🛡️ DPDP Act 2023 & E-Waste Rules 2022 Aligned</span>
                <span class="hero-badge">⚖️ 75% Direct Livelihood Share to Women</span>
            </div>
        </div>
        """
    )

    # Call-to-Action Buttons with go_to on_click callbacks
    col_cta1, col_cta2, col_cta_spacer = st.columns([1.6, 1.6, 1.8])
    with col_cta1:
        st.button(
            "🚀 Request a Doorstep Pickup",
            key="hero_cta_citizen",
            type="primary",
            use_container_width=True,
            on_click=go_to,
            args=("👤 Citizen Portal (Request Pickup)",)
        )
    with col_cta2:
        st.button(
            "⚡ Judge Quick Tour & Guide",
            key="hero_cta_guide",
            use_container_width=True,
            on_click=go_to,
            args=("❓ Help & Guide",)
        )

    st.write("")

    # 4 LIVE IMPACT COUNTERS FROM DATABASE
    st.markdown("### 🌍 Live City Impact Counters")
    st.caption("Real-time metrics aggregated from the Meerut municipal e-waste database.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        label="Collected E-Waste Tonnage",
        value=f"{kpis['total_kg']} kg",
        help="Verified weight of e-waste safely collected by SHGs and diverted from unscientific burning."
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
        help="Doorstep collections fulfilled through the verified 6-stage compliance pipeline."
    )
    c4.metric(
        label="Est. Paid to Women SHGs",
        value=f"₹{kpis['total_shg_earnings']:,.0f}",
        help="Net 75% scrap revenue share credited directly to SHG bank accounts via Direct Bank Transfer (DBT)."
    )

    # Extra Environmental Impact Highlights
    render_html(
        f"""
        <div style="background:var(--surface); border:1px solid var(--border); border-left:5px solid var(--success); border-radius:14px; padding:18px 24px; margin:20px 0 32px 0; display:flex; justify-content:space-around; align-items:center; flex-wrap:wrap; gap:16px; box-shadow: 0 4px 16px var(--shadow);">
            <div style="text-align:center;">
                <span style="font-size:1.6rem; font-weight:800; color:var(--success);">{kpis['co2_avoided_kg']} kg</span><br/>
                <span style="font-size:0.75rem; color:var(--muted); font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">CO₂ Emissions Avoided</span>
            </div>
            <div style="height:36px; width:1px; background:var(--border);"></div>
            <div style="text-align:center;">
                <span style="font-size:1.6rem; font-weight:800; color:var(--success);">{kpis['heavy_metals_prevented_g']} g</span><br/>
                <span style="font-size:0.75rem; color:var(--muted); font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">Toxic Metals Diverted</span>
            </div>
            <div style="height:36px; width:1px; background:var(--border);"></div>
            <div style="text-align:center;">
                <span style="font-size:1.6rem; font-weight:800; color:var(--success);">{kpis['total_green_credits']}</span><br/>
                <span style="font-size:0.75rem; color:var(--muted); font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">Citizen Green Credits Issued</span>
            </div>
            <div style="height:36px; width:1px; background:var(--border);"></div>
            <div style="text-align:center;">
                <span style="font-size:1.6rem; font-weight:800; color:var(--success);">~{kpis['trees_equivalent']}</span><br/>
                <span style="font-size:0.75rem; color:var(--muted); font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">Tree Carbon Absorption Eq.</span>
            </div>
        </div>
        """
    )

    # 4-STEP "HOW IT WORKS" VISUAL PROCESS (EQUAL-HEIGHT RESPONSIVE GRID)
    st.markdown("### 🔄 How SheCycle Works: Transparent 4-Stage Lifecycle")
    st.caption("Statutory segregation of duties: collection & aggregation by women SHGs; smelting & refining by CPCB recyclers.")

    render_html(
        """
        <div class="she-card-grid-4">
            <div class="she-grid-card she-card-green">
                <span style="font-size:1.8rem;">📱</span>
                <div class="she-card-title" style="color:var(--success);">1. Citizen Request</div>
                <p class="she-card-body">
                    Submit doorstep pickup in under 60 seconds with no complex password. Data protected under DPDP Act 2023.
                </p>
            </div>
            <div class="she-grid-card she-card-indigo">
                <span style="font-size:1.8rem;">👩‍🦰</span>
                <div class="she-card-title" style="color:var(--primary);">2. SHG Collection</div>
                <p class="she-card-body">
                    Verified women SHGs accept jobs in their ward, verify weight with calibrated digital scales, and follow PPE rules.
                </p>
            </div>
            <div class="she-grid-card she-card-highlight">
                <span style="font-size:1.8rem;">🔬</span>
                <div class="she-card-title" style="color:var(--accent);">3. Safe Aggregation</div>
                <p class="she-card-body">
                    Basic non-hazardous fraction segregation into metals, plastics, and boards. Batteries remain sealed in transit.
                </p>
            </div>
            <div class="she-grid-card she-card-green">
                <span style="font-size:1.8rem;">🚛</span>
                <div class="she-card-title" style="color:var(--success);">4. Authorised Recycling</div>
                <p class="she-card-body">
                    Aggregated scrap consigned to CPCB-authorised recyclers under legal manifest. 75% net value credited via DBT.
                </p>
            </div>
        </div>
        """
    )

    st.markdown("---")

    # ROLE SELECTOR CARDS WITH SEAMLESS 1-CLICK CALLBACKS
    st.markdown("### 🚪 Choose Your Portal")
    st.caption("Select your role to access dedicated portals and operational workflows.")

    r1, r2, r3 = st.columns(3)

    with r1:
        render_html(
            """
            <div class="she-card she-card-green" style="min-height:190px; display:flex; flex-direction:column; justify-content:space-between;">
                <div>
                    <h4 style="margin-top:0; color:var(--success);">👤 For Citizens</h4>
                    <p style="font-size:0.88rem; line-height:1.45; margin-bottom:0;">
                        Discard obsolete phones, chargers, and appliances safely. Earn Green Credits and track your pickup live.
                    </p>
                </div>
            </div>
            """
        )
        st.button(
            "🚀 Go to Citizen Portal",
            key="btn_goto_cit",
            use_container_width=True,
            type="primary",
            on_click=go_to,
            args=("👤 Citizen Portal (Request Pickup)",)
        )

    with r2:
        render_html(
            """
            <div class="she-card she-card-highlight" style="min-height:190px; display:flex; flex-direction:column; justify-content:space-between;">
                <div>
                    <h4 style="margin-top:0; color:var(--accent);">👩‍🦰 For Women SHGs</h4>
                    <p style="font-size:0.88rem; line-height:1.45; margin-bottom:0;">
                        DAY-NRLM / NULM Self-Help Groups: view ward jobs, log verified weights, and track your 75% revenue share.
                    </p>
                </div>
            </div>
            """
        )
        st.button(
            "🤝 Open SHG Portal",
            key="btn_goto_shg",
            use_container_width=True,
            on_click=go_to,
            args=("👩‍🦰 Women SHG Partner Portal",)
        )

    with r3:
        render_html(
            """
            <div class="she-card she-card-indigo" style="min-height:190px; display:flex; flex-direction:column; justify-content:space-between;">
                <div>
                    <h4 style="margin-top:0; color:var(--primary);">🏛️ For Municipal Admin</h4>
                    <p style="font-size:0.88rem; line-height:1.45; margin-bottom:0;">
                        Urban Local Bodies & CPCB officials: scrutinize SHG applications, analyze tonnage, and reconcile DBT payouts.
                    </p>
                </div>
            </div>
            """
        )
        st.button(
            "📊 Access Admin Dashboard",
            key="btn_goto_admin",
            use_container_width=True,
            on_click=go_to,
            args=("🏛️ Municipal Admin Dashboard",)
        )

    # Clean Footer
    render_html(
        """
        <div class="she-footer">
            <strong>SheCycle: Women-Led Smart E-Waste Management Platform</strong><br/>
            Developed by <strong>Team Zero Toxic (Pragya Rajwanshi, Rohit Kumar)</strong> | Finalist, <strong>IEEE WIE HackEarth 2026</strong><br/>
            <em>Demo data is simulated for the Meerut, Uttar Pradesh municipal cluster pilot.</em>
        </div>
        """
    )


# ==========================================
# ROUTER & DISPATCHER
# ==========================================

current_page = st.session_state.get("main_nav_radio", nav_options[0])

if current_page == "🏠 Home & Impact Hub":
    render_home_page()
elif current_page == "👤 Citizen Portal (Request Pickup)":
    render_citizen_portal()
elif current_page == "👩‍🦰 Women SHG Partner Portal":
    render_shg_portal()
elif current_page == "🏛️ Municipal Admin Dashboard":
    render_admin_portal()
elif current_page == "🗺️ Pilot Roadmap & Compliance":
    render_roadmap_page()
elif current_page == "❓ Help & Guide":
    render_help_page()
