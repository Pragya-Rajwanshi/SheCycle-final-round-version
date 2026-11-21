"""
portal_roadmap.py - Strategic Roadmap & Regulatory Compliance Architecture
Features:
- Pragmatic 3-Phase Expansion Plan (Meerut Pilot -> UP State -> National Scale)
- Statutory alignment with India's E-Waste (Management) Rules 2022
- Privacy by design adhering to Digital Personal Data Protection (DPDP) Act 2023
- Clear boundaries, safety limitations, and honest engineering disclosures
"""

import streamlit as st
from modules.ui_common import inject_custom_css, render_page_header, render_html


def render_roadmap_page():
    """Renders the Strategic Roadmap & Compliance view."""
    inject_custom_css(dark_mode=st.session_state.get("dark_mode", False))

    render_page_header(
        icon="🗺️",
        title="Strategic Roadmap & Regulatory Compliance",
        subtitle="A pragmatic, scalable circular-economy architecture designed for real-world municipal rollouts in tier-2 and tier-3 Indian cities.",
        badge="E-Waste 2022 & DPDP 2023"
    )

    # 3-Phase Roadmap Visual
    st.markdown("### 🚀 Phased Evolution Plan")
    st.caption("A disciplined path from offline-validated city pilot to smart-city IoT integration.")

    c1, c2, c3 = st.columns(3)

    with c1:
        render_html(
            """
            <div class="she-card she-card-green" style="min-height:360px; display:flex; flex-direction:column; justify-content:space-between;">
                <div>
                    <span class="status-pill status-approved">Phase 1: Current Pilot</span>
                    <h4 style="margin:12px 0 8px 0; color:var(--success);">Meerut City Pilot</h4>
                    <p style="font-size:0.85rem; color:var(--muted); line-height:1.55;">
                        • 3-5 verified SHGs across 10 core municipal wards.<br/>
                        • Doorstep pickup web interface (zero-friction, no password).<br/>
                        • Calibrated handheld digital scales for weight validation.<br/>
                        • Basic aggregation & segregation into non-hazardous fractions.<br/>
                        • Localized partnership with CPCB/UPPCB authorised recyclers.<br/>
                        • Offline SQLite persistence for robust field demos.
                    </p>
                </div>
                <div class="compliance-pill-box" style="margin-top:16px;">
                    <strong>Status:</strong> Active in HackEarth Final
                </div>
            </div>
            """
        )

    with c2:
        render_html(
            """
            <div class="she-card she-card-indigo" style="min-height:360px; display:flex; flex-direction:column; justify-content:space-between;">
                <div>
                    <span class="status-pill status-assigned">Phase 2: Scale-Up</span>
                    <h4 style="margin:12px 0 8px 0; color:var(--primary);">Regional App & MIS Integration</h4>
                    <p style="font-size:0.85rem; color:var(--muted); line-height:1.55;">
                        • Offline-first progressive mobile app in Hindi & regional languages.<br/>
                        • Live API bridge with DAY-NULM / DAY-NRLM national portals for automated SHG credential verification.<br/>
                        • WhatsApp Business Bot for citizen pickup booking via voice notes.<br/>
                        • Direct Bank Transfer (DBT) integration with PFMS for instant SHG payouts.<br/>
                        • Expansion across Western UP (Ghaziabad, Noida, Agra).
                    </p>
                </div>
                <div class="compliance-pill-box" style="margin-top:16px;">
                    <strong>Timeline:</strong> Q2 - Q4 2027
                </div>
            </div>
            """
        )

    with c3:
        render_html(
            """
            <div class="she-card she-card-highlight" style="min-height:360px; display:flex; flex-direction:column; justify-content:space-between;">
                <div>
                    <span class="status-pill status-sorted">Phase 3: Smart Cities</span>
                    <h4 style="margin:12px 0 8px 0; color:var(--accent);">IoT Drop-Boxes & B2B EPR</h4>
                    <p style="font-size:0.85rem; color:var(--muted); line-height:1.55;">
                        • Solar-powered smart community e-waste bins with ultrasonic level & strain-gauge weight sensors.<br/>
                        • Automated bin fill-level alerts dispatched to nearest SHG cluster.<br/>
                        • B2B API integration with Producer Responsibility Organizations (PROs) and OEMs for statutory EPR compliance credits.<br/>
                        • End-to-end cryptographic audit certificates for CPCB reporting.
                    </p>
                </div>
                <div class="compliance-pill-box" style="margin-top:16px;">
                    <strong>Timeline:</strong> 2028+
                </div>
            </div>
            """
        )

    st.markdown("---")

    # Statutory Compliance Framework
    st.markdown("### ⚖️ Regulatory Compliance & Safety Protocols")
    st.caption("Operating boundaries strictly governed by environmental and data privacy laws.")

    col_law1, col_law2 = st.columns(2)

    with col_law1:
        render_html(
            """
            <div class="she-card she-card-green">
                <h4 style="margin-top:0; color:var(--success);">📜 E-Waste (Management) Rules 2022</h4>
                <ul style="font-size:0.85rem; color:var(--text); line-height:1.6; padding-left:18px;">
                    <li>
                        <strong>Aggregation Boundary:</strong> In strict accordance with Ministry of Environment, Forest & Climate Change (MoEFCC) guidelines, SHGs act exclusively as certified <em>Collection & Aggregation Centers</em>.
                    </li>
                    <li>
                        <strong>No Unregulated Dismantling:</strong> Chemical leaching, CRT crushing, and acid extraction are legally prohibited at the SHG level. Dismantling and precious metal recovery take place strictly at CPCB-authorized recycling facilities.
                    </li>
                    <li>
                        <strong>Sealed Hazardous Transit:</strong> High-risk fractions (Lithium-ion batteries) are never opened by SHG members; they are bagged in fire-retardant pouches and handed over intact.
                    </li>
                    <li>
                        <strong>Chain of Custody:</strong> Every consignment carries a sequential Recycler Manifest & Challan, providing a transparent audit trail from citizen doorstep to recycler smelter.
                    </li>
                </ul>
            </div>
            """
        )

    with col_law2:
        render_html(
            """
            <div class="she-card she-card-highlight">
                <h4 style="margin-top:0; color:var(--primary);">🛡️ DPDP Act 2023 (Data Protection by Design)</h4>
                <ul style="font-size:0.85rem; color:var(--text); line-height:1.6; padding-left:18px;">
                    <li>
                        <strong>Purpose Limitation:</strong> Citizen contact details and home addresses are used strictly for collection logistics and never monetized or shared with third parties.
                    </li>
                    <li>
                        <strong>Data Masking Everywhere:</strong> Citizen phone numbers (e.g. <code>98XXXXXX10</code>) and SHG bank accounts (e.g. <code>****1234</code>) are masked across all user, SHG, and admin views.
                    </li>
                    <li>
                        <strong>Dual-Key Tracking Authentication:</strong> Tracking does not expose citizen data; querying status strictly requires both Request ID and the last 4 digits of the citizen's mobile number.
                    </li>
                    <li>
                        <strong>Pre-Collection Safety Advisory:</strong> Citizens are prompted before booking to factory-reset devices and wipe personal storage media.
                    </li>
                </ul>
            </div>
            """
        )

    st.markdown("---")

    # Honest Engineering Disclosures & Assumptions
    st.markdown("### 🔍 Transparent Limitations & Stated Assumptions")
    render_html(
        """
        <div class="she-card">
            <h5 style="margin-top:0; color:var(--primary);">Honest Architectural Disclosures for Hackathon Evaluation:</h5>
            <ol style="font-size:0.85rem; color:var(--muted); line-height:1.65; padding-left:18px; margin-bottom:0;">
                <li>
                    <strong style="color:var(--text);">Illustrative Scrap Rates:</strong> Scrap buy-back rates (e.g. ₹120/kg for smartphones, ₹150/kg for batteries) are benchmark averages derived from Indian informal/formal market data and will fluctuate dynamically with live recycler contracts.
                </li>
                <li>
                    <strong style="color:var(--text);">Simulated Government MIS Verification:</strong> In this offline prototype, SHG registration IDs are validated against strict algorithmic format regex (e.g., <code>NULM-YYYY-NN</code>, <code>NRLM-NNNN</code>) and checked for uniqueness. Live production will bridge directly to the National Portal for Urban Livelihoods API.
                </li>
                <li>
                    <strong style="color:var(--text);">Environmental Multipliers:</strong> Environmental CO2 avoidance (~1.44 kg CO2e / kg e-waste) and toxic heavy metal diversion rates are calculated from UNEP and Central Pollution Control Board (CPCB) lifecycle studies, not physical mass spectrometers.
                </li>
            </ol>
        </div>
        """
    )
