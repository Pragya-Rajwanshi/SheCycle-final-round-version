"""
portal_help.py - Comprehensive Help, Quick-Start Tour & Compliance Guide
Features:
- Quick Start 5-Step Click-Path for hackathon judges with direct navigation buttons
- Interactive Role Guides (Citizen, SHG, Admin) with step-by-step instructions & expected results
- Demo Credentials Card with copy-friendly code block
- Visual 6-Stage Status Lifecycle Explainer
- 11 Expandable FAQs addressing compliance, algorithms, data privacy, and scrap economics
- Safety and Compliance Tips (E-Waste Rules 2022 & DPDP Act 2023)
- Contact & Feedback Card + Interactive "Report an Issue" form
- Glossary of Key Regulatory & Program Terms
"""

import streamlit as st
import pandas as pd
from typing import Optional

from modules.ui_common import (
    inject_custom_css,
    render_page_header,
    get_status_badge_html,
    render_html,
    go_to
)


def render_help_page():
    """Renders the comprehensive Help & Guide portal."""
    inject_custom_css(dark_mode=st.session_state.get("dark_mode", False))

    render_page_header(
        icon="❓",
        title="Help, User Guides & Compliance Reference",
        subtitle="Step-by-step operating guides, judge click-paths, statutory compliance FAQ, and program glossary.",
        badge="Pilot Cluster: Meerut, UP"
    )

    # Main Navigation Tabs for Help Page
    tab_tour, tab_roles, tab_creds, tab_lifecycle, tab_faq, tab_safety, tab_glossary, tab_contact = st.tabs([
        "⚡ Judge Quick Tour",
        "📖 Role User Guides",
        "🔑 Demo Credentials",
        "🔄 Status Lifecycle",
        "💬 11 Core FAQs",
        "🛡️ Safety Protocols",
        "📚 Glossary",
        "📞 Help & Feedback"
    ])

    # ==========================================
    # TAB 1: JUDGE QUICK TOUR (5-STEP CLICK-PATH)
    # ==========================================
    with tab_tour:
        render_html(
            """
            <div class="she-card she-card-highlight">
                <h4 style="margin-top:0; color:var(--primary);">⏱️ 2-Minute Evaluator Tour: End-to-End Workflow</h4>
                <p style="font-size:0.9rem; color:var(--muted); margin-bottom:0;">
                    Experience the complete circular flow from citizen doorstep request to CPCB-authorised recycler handover in 5 simple steps.
                    Click the navigation buttons below to jump directly to each portal.
                </p>
            </div>
            """
        )

        steps = [
            {
                "num": "1",
                "title": "Home Impact Hub",
                "badge": "Public",
                "desc": "Review live city impact counters (92+ kg collected, 3 active SHGs, ₹6,100+ paid to women, ~134 kg CO₂ avoided).",
                "action_label": "Go to Home Impact Hub",
                "target_page": "🏠 Home & Impact Hub"
            },
            {
                "num": "2",
                "title": "Citizen Request & QR Pass",
                "badge": "Citizen",
                "desc": "Book a pickup request (e.g. Smartphones, 2.5 kg). Note DPDP consent, instant Request ID (EW-00029), and QR Code Pass.",
                "action_label": "Go to Citizen Portal",
                "target_page": "👤 Citizen Portal (Request Pickup)"
            },
            {
                "num": "3",
                "title": "SHG Collection & Segregation",
                "badge": "Women SHG",
                "desc": "Log in as Maa Durga SHG (PIN: 1234). Accept a job, verify actual weight with digital scale, confirm PPE checklist, and segregate fractions.",
                "action_label": "Go to Women SHG Portal",
                "target_page": "👩‍🦰 Women SHG Partner Portal"
            },
            {
                "num": "4",
                "title": "Recycler Handover",
                "badge": "Formal Handover",
                "desc": "Dispatch sorted e-waste to CPCB-authorised recycler (Attero Recycling) with legal manifest challan #REC-UP-2026-9011.",
                "action_label": "Manage SHG Collections",
                "target_page": "👩‍🦰 Women SHG Partner Portal"
            },
            {
                "num": "5",
                "title": "Admin Scrutiny & Analytics",
                "badge": "Municipal Admin",
                "desc": "Sign in as Admin (password: meerut2026). Scrutinize pending SHGs, review 60-day Plotly tonnage charts, and export compliance CSV.",
                "action_label": "Go to Admin Dashboard",
                "target_page": "🏛️ Municipal Admin Dashboard"
            }
        ]

        for s in steps:
            with st.container(border=True):
                c_num, c_body, c_btn = st.columns([0.6, 3, 1.4])
                with c_num:
                    render_html(
                        f"""
                        <div style="background:linear-gradient(135deg, var(--primary), var(--accent)); color:white; border-radius:50%; width:44px; height:44px; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:1.1rem; box-shadow:0 4px 12px var(--shadow);">
                            {s['num']}
                        </div>
                        """
                    )
                with c_body:
                    render_html(f"<div><strong style='color:var(--text); font-size:1rem;'>Step {s['num']}: {s['title']}</strong> &nbsp; <span class='status-pill status-assigned'>{s['badge']}</span></div>")
                    st.caption(s["desc"])
                with c_btn:
                    st.write("")
                    st.button(
                        f"👉 {s['action_label']}",
                        key=f"quick_tour_{s['num']}",
                        use_container_width=True,
                        on_click=go_to,
                        args=(s["target_page"],)
                    )

    # ==========================================
    # TAB 2: ROLE USER GUIDES
    # ==========================================
    with tab_roles:
        r_citizen, r_shg, r_admin = st.tabs(["👤 Citizen Guide", "👩‍🦰 Women SHG Guide", "🏛️ Municipal Admin Guide"])

        with r_citizen:
            st.markdown("#### 👤 Citizen Doorstep E-Waste Recycling Guide")
            st.markdown(
                """
                1. **Step 1: Open the Citizen Portal & Select Language**  
                   Use the bilingual toggle at the top right to switch between **English** and **हिंदी (Hindi)**.
                   *Expected Result:* Form labels and safety notices immediately adapt.

                2. **Step 2: Enter Contact Details & Meerut Ward**  
                   Provide your name, 10-digit mobile number, full address, and select your Meerut ward (e.g. *Kankar Khera*).
                   *Expected Result:* Mobile number is automatically validated (`^[6-9]\\d{9}$`).

                3. **Step 3: Select Item Category & Estimated Weight**  
                   Choose an e-waste type (e.g., *Smartphones & Feature Phones*) and enter approximate kg.
                   *Expected Result:* System calculates provisional Green Credits based on category multipliers.

                4. **Step 4: Review Safety Advisory & Accept DPDP Consent**  
                   Wipe personal data, remove SIM/SD cards, and accept the minimal data consent under the DPDP Act 2023.
                   *Expected Result:* Form allows submission only after consent is confirmed.

                5. **Step 5: Submit & Receive Digital Pickup Pass**  
                   Submit request to get your unique sequential **Request ID (`EW-00029`)** and downloadable **QR Pass**.
                   *Expected Result:* Nearby verified SHG receives the pickup request on their ward job board.

                6. **Step 6: Track Pickup via Dual-Key Authentication**  
                   Visit the "Track Request" tab, enter your Request ID + last 4 digits of your phone.
                   *Expected Result:* Full 6-stage visual timeline stepper and audit history log appear.
                """
            )

        with r_shg:
            st.markdown("#### 👩‍🦰 Women Self-Help Group (SHG) Operating Guide")
            st.markdown(
                """
                1. **Step 1: Authenticate with Registration ID & PIN**  
                   Enter your Govt. Registration ID (`NULM-2024-88`) and 4-digit security PIN (`1234`).
                   *Expected Result:* Salted SHA-256 hash verifies identity and unlocks your ward job board.

                2. **Step 2: Browse Available Ward Jobs**  
                   Open the "Available Job Board" tab. Notice that requests are strictly filtered to your group's operating localities.
                   *Expected Result:* Only relevant local pickups are visible.

                3. **Step 3: Accept Pickup Job**  
                   Click "Accept Pickup".
                   *Expected Result:* Request status transitions from `Requested` &rarr; `Assigned`.

                4. **Step 4: Doorstep Collection & Weighing**  
                   Visit the citizen, weigh items on calibrated digital scales, and confirm mandatory PPE & battery safety checkboxes.
                   *Expected Result:* Request transitions to `Collected`. Actual weight is stored and earnings recalculated.

                5. **Step 5: Basic Fraction Segregation (Non-Hazardous)**  
                   Segregate into metals, PCBs, batteries, and plastics. Lithium batteries must remain sealed intact.
                   *Expected Result:* Request transitions to `Sorted`. Fraction weights recorded in JSON.

                6. **Step 6: Handover to Authorised Recycler**  
                   Deliver aggregated consignment to a CPCB-authorised recycler and record manifest challan #.
                   *Expected Result:* Request transitions to `Delivered to Recycler`.

                7. **Step 7: Direct Bank Transfer (DBT) Settlement**  
                   Municipal finance officers reconcile weigh-bills and disburse the 75% net share to the group bank account.
                   *Expected Result:* Request transitions to `Settled`. Available in downloadable CSV ledger.
                """
            )

        with r_admin:
            st.markdown("#### 🏛️ Municipal Administration & CPCB Oversight Guide")
            st.markdown(
                """
                1. **Step 1: Admin Authentication**  
                   Enter the demo password `meerut2026` or click "One-Click Judge Login".
                   *Expected Result:* Full administrative controls, audit trails, and analytics unlock.

                2. **Step 2: Review Exception Alerts**  
                   Check the top notification banner for operational bottlenecks (requests unassigned > 48 hours or inactive SHGs).
                   *Expected Result:* Immediate visibility into service gaps across Meerut wards.

                3. **Step 3: Scrutinize Pending SHGs**  
                   Open the "SHG Scrutiny Queue" tab. Review applicant credentials (e.g. *Nav Chetna Mahila Mandal*).
                   Click **Approve SHG** or **Reject** with a recorded reason.
                   *Expected Result:* Status transitions to `Approved` or `Rejected` with permanent audit logging.

                4. **Step 4: Analyze Real Tonnage Flows**  
                   Open "Real Tonnage Analytics" to explore 60-day tonnage trends, ward distributions, category breakdowns, and SHG leaderboards.
                   *Expected Result:* Interactive Plotly charts provide real-time spatial and categorical insights.

                5. **Step 5: Settle Recycler Consignments**  
                   Open "Financial Reconciliation & DBT" tab to reconcile recycler weigh-bills and approve direct bank transfers.
                   *Expected Result:* Payout marked as `Settled` and logged in compliance history.

                6. **Step 6: Export Master Compliance Record**  
                   Open "Master Compliance Audit Trail" and click **Download Master Compliance Audit Trail (CSV)**.
                   *Expected Result:* Full audit log exportable for CPCB and UPPCB Extended Producer Responsibility (EPR) reporting.
                """
            )

    # ==========================================
    # TAB 3: DEMO CREDENTIALS
    # ==========================================
    with tab_creds:
        render_html(
            """
            <div class="she-card she-card-indigo">
                <h4 style="margin-top:0; color:var(--primary);">🔑 Complete Demo Credentials Card (Hackathon Evaluators)</h4>
                <p style="font-size:0.85rem; color:var(--muted); margin-bottom:0;">
                    These pre-configured credentials allow instant evaluation of all 4 system roles without manual sign-ups.
                </p>
            </div>
            """
        )

        st.code(
            """# -----------------------------------------------------------------
# SHECYCLE DEMO CREDENTIALS (MEERUT PILOT CLUSTER)
# -----------------------------------------------------------------

1. MUNICIPAL ADMIN PORTAL:
   - Password: meerut2026
   - Scope: City-wide oversight, SHG verification, tonnage analytics, DBT settlement

2. APPROVED WOMEN SHG #1 (DAY-NULM Urban):
   - Group Name: Maa Durga Mahila SHG
   - Reg ID: NULM-2024-88
   - PIN: 1234
   - Operating Localities: Kankar Khera, Modipuram, Pallavpuram

3. APPROVED WOMEN SHG #2 (DAY-NRLM Rural):
   - Group Name: Ekta Sakhi Mahila SHG
   - Reg ID: NRLM-1024
   - PIN: 1234
   - Operating Localities: Rohta Road, Partapur

4. PENDING SHG (For Admin Scrutiny & Approval Testing):
   - Group Name: Nav Chetna Mahila Mandal
   - Reg ID: NULM-2025-12
   - PIN: 1234
   - Status: Pending Municipal Approval (Gated from viewing or accepting jobs)

5. CITIZEN REQUEST TRACKING SAMPLES:
   - Request ID: EW-00001 | Phone Last 4: 3210 (Status: Settled)
   - Request ID: EW-00002 | Phone Last 4: 5678 (Status: Settled)
   - Request ID: EW-00025 | Phone Last 4: 9988 (Status: Assigned)
# -----------------------------------------------------------------""",
            language="yaml"
        )

    # ==========================================
    # TAB 4: STATUS LIFECYCLE EXPLAINER
    # ==========================================
    with tab_lifecycle:
        st.markdown("#### 🔄 6-Stage Statutory Compliance Lifecycle")
        st.caption("Unlike binary 'Pending/Completed' prototypes, SheCycle enforces an immutable 6-stage compliance pipeline.")

        lifecycle_steps = [
            ("1. Requested", "Citizen", "Citizen books pickup via web portal. System generates EW-00001 ID and estimates Green Credits.", "DPDP Act minimal consent verified"),
            ("2. Assigned", "Women SHG", "Verified local SHG operating in the ward accepts the job on their private board.", "SHG municipal verification checked"),
            ("3. Collected", "Women SHG", "SHG visits doorstep, weighs items on digital scales, and confirms PPE safety checklist.", "Digital weight & safety verified"),
            ("4. Sorted", "Women SHG", "Basic non-hazardous fraction segregation (metals, PCBs, plastics). Lithium batteries kept sealed.", "CPCB non-dismantling rule enforced"),
            ("5. Delivered to Recycler", "Authorised Recycler", "Scrap consigned to CPCB/UPPCB authorised recycler under official manifest challan #.", "Recycler CPCB registration checked"),
            ("6. Settled", "Municipal Admin", "Finance cell reconciles recycler weigh-bill and releases 75% DBT share to SHG bank account.", "Direct Bank Transfer (DBT) confirmed")
        ]

        for stage, actor, action, compliance in lifecycle_steps:
            with st.container(border=True):
                c_stg, c_act, c_dtl = st.columns([1.2, 1, 2.5])
                with c_stg:
                    st.markdown(f"**{stage}**")
                with c_act:
                    render_html(f"<span class='status-pill status-assigned'>{actor}</span>")
                with c_dtl:
                    st.write(action)
                    st.caption(f"🔒 *Rule:* {compliance}")

    # ==========================================
    # TAB 5: 11 CORE FAQS
    # ==========================================
    with tab_faq:
        st.markdown("#### 💬 Frequently Asked Questions (FAQ)")
        st.caption("Common inquiries regarding regulatory alignment, data privacy, scrap algorithms, and municipal policies.")

        faqs = [
            (
                "1. How is an SHG verified in the system before gaining access to citizen e-waste?",
                "New SHGs register using their official DAY-NRLM or DAY-NULM registration ID. The system validates the format using strict regular expressions (`NULM-YYYY-NN` or `NRLM-NNNN`) and rejects duplicates. Crucially, newly registered groups are placed in 'Pending Approval' status and cannot view citizen addresses, phone numbers, or open pickup requests until the Municipal Commissioner or NULM City Project Officer reviews their credentials in the Admin Scrutiny Queue and approves them."
            ),
            (
                "2. What happens to citizen personal data under the DPDP Act 2023?",
                "SheCycle is designed around 'Data Protection by Design'. Citizen mobile numbers and bank accounts are masked throughout the platform (e.g. `98XXXXXX10`, `****1234`). Contact information is collected solely for doorstep pickup coordination and is never monetized or shared with third parties. Citizens must explicitly accept a minimal data consent checkbox before submitting a request."
            ),
            (
                "3. Why are SHGs prohibited from dismantling or burning electronic scrap?",
                "Under India's E-Waste (Management) Rules 2022, unregulated dismantling, crude acid leaching, and open-air burning of printed circuit boards release toxic lead, mercury, and dioxins into soil and air. SheCycle restricts SHG operations strictly to safe collection, digital weighing, aggregation, and non-hazardous category sorting. Industrial dismantling and smelting are performed exclusively by CPCB-authorised recycling facilities."
            ),
            (
                "4. How are scrap earnings split (75% / 12% / 8% / 5%)?",
                "Gross scrap value is computed from verified digital weights and illustrative market benchmarks. Revenue is reconciled strictly in `services.py` to sum to 100%:\n- **75%** Net SHG Livelihood (deposited directly via Direct Bank Transfer)\n- **12%** Logistics & Safety Fund (calibrated digital scales, puncture-proof battery pouches, PPE)\n- **8%** Municipal Platform & Audit Fee (software hosting, GIS routing, statutory compliance)\n- **5%** Citizen Green Credits Fund (property tax rebates and eco-partner coupons)."
            ),
            (
                "5. Are the CO2 avoided and toxic heavy-metal diversion numbers real?",
                "The environmental savings shown are illustrative estimates derived from published UNEP and Central Pollution Control Board (CPCB) lifecycle assessment studies. On average, diverting 1 kg of e-waste from open burning to scientific recovery prevents approximately 1.44 kg of CO2 equivalent emissions and protects soil from ~28 grams of toxic heavy metal contamination."
            ),
            (
                "6. What are Green Credits and how can citizens redeem them?",
                "Green Credits are digital sustainability points awarded to citizens based on the verified weight and category of e-waste safely segregated at doorstep (e.g., 25 credits/kg for smartphones, 30 credits/kg for batteries). In the Meerut municipal model, credits can be redeemed for property tax rebates (100 credits = ₹50 rebate) or partner eco-discounts."
            ),
            (
                "7. What happens if a citizen request is not picked up within 48 hours?",
                "The system continuously monitors request timestamps. If an open request remains in 'Requested' status without an assigned SHG for more than 48 hours, it automatically triggers an **Operational Exception Alert** on the Municipal Admin Dashboard, prompting administrators to reassign the pickup to an adjacent ward cluster."
            ),
            (
                "8. How does dual-key tracking protect citizen privacy?",
                "Instead of allowing anyone to query private requests by entering any phone number (which would leak addresses and item details), SheCycle requires dual authentication: the unique **Request ID** (e.g. `EW-00001`) PLUS the **last 4 digits of the registered mobile number**. This prevents open enumeration and protects citizen privacy."
            ),
            (
                "9. Is SheCycle currently connected to live government NRLM/NULM MIS APIs?",
                "In this prototype, government MIS verification is simulated using strict algorithmic pattern validation (`NULM-YYYY-NN` and `NRLM-NNNN`), uniqueness enforcement, and manual administrative scrutiny. In Phase 2 of our strategic roadmap, this layer will bridge directly to the Ministry of Housing and Urban Affairs (MoHUA) NULM open API gateway."
            ),
            (
                "10. What e-waste items are accepted versus strictly prohibited?",
                "**Accepted:** Smartphones, feature phones, laptops, computer components, chargers, lithium-ion battery packs (intact), irons, toasters, kettles, blenders, and assorted wires/adapters.\n**Prohibited:** Smashed or leaking lead-acid automotive batteries, damaged fluorescent CRT cathode tubes, industrial radiation equipment, and bio-medical electronic waste."
            ),
            (
                "11. How do SHGs receive payment (Direct Bank Transfer - DBT)?",
                "Once the CPCB-authorised recycler certifies consignment delivery and issues a formal manifest challan, the Municipal Finance Officer reconciles the weigh-bill in the Admin Dashboard and clicks 'Reconcile & Settle'. The 75% net share is disbursed via Direct Bank Transfer (DBT) directly into the SHG's group bank account."
            )
        ]

        for q, a in faqs:
            with st.expander(f"❓ {q}"):
                st.markdown(a)

    # ==========================================
    # TAB 6: SAFETY & COMPLIANCE PROTOCOLS
    # ==========================================
    with tab_safety:
        st.markdown("#### 🛡️ Statutory Safety & Regulatory Protocols")
        st.caption("Operational standards adhering to India's E-Waste (Management) Rules 2022 and DPDP Act 2023.")

        c_s1, c_s2 = st.columns(2)
        with c_s1:
            render_html(
                """
                <div class="she-card she-card-green">
                    <h5 style="margin-top:0; color:var(--success);">🔋 Citizen Pre-Collection Advisory</h5>
                    <ul style="font-size:0.85rem; color:var(--text); line-height:1.6; padding-left:18px;">
                        <li><strong>Factory Reset Devices:</strong> Back up data and factory-reset mobile phones and laptops before handover.</li>
                        <li><strong>Remove Removable Media:</strong> Take out SIM cards, SD storage cards, and external flash drives.</li>
                        <li><strong>Do Not Dismantle Batteries:</strong> Never puncture, crush, or disassemble lithium-ion batteries.</li>
                        <li><strong>Store Separately:</strong> Keep loose batteries in a separate dry plastic container away from heat sources.</li>
                    </ul>
                </div>
                """
            )

        with c_s2:
            render_html(
                """
                <div class="she-card she-card-highlight">
                    <h5 style="margin-top:0; color:var(--accent);">👩‍🦰 SHG Field Handling & PPE Rules</h5>
                    <ul style="font-size:0.85rem; color:var(--text); line-height:1.6; padding-left:18px;">
                        <li><strong>Mandatory Protective Gear:</strong> Wear cut-resistant nitrile gloves and safety eyewear during all collection jobs.</li>
                        <li><strong>Puncture-Proof Transit Bags:</strong> Place all intact batteries in fire-retardant transit pouches.</li>
                        <li><strong>No Open Burning or Acid Leaching:</strong> Chemical separation and smelting are strictly handled by CPCB recyclers.</li>
                        <li><strong>Digital Scale Calibration:</strong> Calibrate digital scale zero-tare before each weighing.</li>
                    </ul>
                </div>
                """
            )

    # ==========================================
    # TAB 7: GLOSSARY OF TERMS
    # ==========================================
    with tab_glossary:
        st.markdown("#### 📚 Glossary of Regulatory & Technical Terms")
        st.caption("Standard acronyms and terms used across Indian waste management and women empowerment missions.")

        glossary = [
            ("SHG", "Self-Help Group: A village or neighborhood-based financial intermediary committee composed of 10 to 20 local women."),
            ("DAY-NRLM", "Deendayal Antyodaya Yojana - National Rural Livelihoods Mission: Flagship poverty alleviation program by the Ministry of Rural Development."),
            ("DAY-NULM", "National Urban Livelihoods Mission: Mission by the Ministry of Housing and Urban Affairs focusing on urban micro-enterprises and self-help groups."),
            ("CPCB", "Central Pollution Control Board: Statutory authority under the Ministry of Environment, Forest and Climate Change governing pollution control in India."),
            ("EPR", "Extended Producer Responsibility: Environmental policy approach where electronic producers bear financial and physical responsibility for end-of-life disposal."),
            ("DPDP Act 2023", "Digital Personal Data Protection Act 2023: India's statutory legal framework governing personal digital data handling and privacy by design."),
            ("DBT", "Direct Bank Transfer: Direct crediting of government welfare subsidies and enterprise payments into beneficiary Aadhaar-linked bank accounts."),
            ("Green Credits", "Municipal environmental reward points issued for verifiable eco-actions, redeemable for local tax rebates and merchant discounts.")
        ]

        gdf = pd.DataFrame(glossary, columns=["Term / Acronym", "Definition & Context"])
        st.dataframe(gdf, use_container_width=True, hide_index=True)

    # ==========================================
    # TAB 8: CONTACT & FEEDBACK
    # ==========================================
    with tab_contact:
        st.markdown("#### 📞 Municipal Helpline & Issue Reporting")
        st.caption("Contact the Meerut Nagar Nigam environmental helpdesk or report a collection grievance.")

        c_c1, c_c2 = st.columns([1.2, 1.5])
        with c_c1:
            render_html(
                """
                <div class="she-card she-card-indigo">
                    <h5 style="margin-top:0; color:var(--primary);">🏛️ Meerut Municipal Cluster Office</h5>
                    <p style="font-size:0.85rem; color:var(--muted); line-height:1.5;">
                        <strong style="color:var(--text);">Cell:</strong> Environmental Management Cell, Meerut Nagar Nigam<br/>
                        <strong style="color:var(--text);">Location:</strong> Town Hall, Near Clock Tower, Meerut, UP 250002<br/>
                        <strong style="color:var(--text);">Toll-Free Helpline:</strong> <code>1800-SHE-CYCLE</code> (9 AM - 6 PM)<br/>
                        <strong style="color:var(--text);">Email:</strong> <code>support@shecycle.up.gov.in</code><br/>
                        <em>(Contact information is illustrative demo data)</em>
                    </p>
                </div>
                """
            )

        with c_c2:
            st.markdown("##### 📝 Report an Operational Issue or Grievance")
            with st.form("feedback_issue_form"):
                issue_cat = st.selectbox(
                    "Issue Category",
                    ["Delayed Pickup (> 48 Hours)", "Incorrect Digital Weighing", "Damaged / Leaking Item", "SHG Portal Login Issue", "General Suggestion"]
                )
                issue_req_id = st.text_input("Request ID (if applicable)", placeholder="e.g. EW-00001")
                issue_desc = st.text_area("Issue Description", placeholder="Describe the grievance or operational problem in detail...")
                issue_submit = st.form_submit_button("Submit Grievance to Municipal Cell", type="primary", use_container_width=True)

                if issue_submit:
                    if not issue_desc.strip():
                        st.error("Please describe your issue before submitting.")
                    else:
                        st.success("✅ Grievance recorded under Ticket #GRV-2026-9481. A municipal nodal officer will inspect the record.")
