"""
portal_shg.py - Women Self-Help Group (SHG) Micro-Entrepreneur Portal
Features:
- Demo auth with registration ID + PIN (hashed with salt)
- Strict compliance gating: Pending SHGs cannot see or accept jobs
- Available Job Board strictly filtered to operating localities
- 4-step progressive collection lifecycle:
  1. Accept job (Requested -> Assigned)
  2. Confirm Collection (Assigned -> Collected): enter actual weight, verify PPE & safety checklist
  3. Basic Sorting (Collected -> Sorted): enter fraction weights, compliance advisory displayed
  4. Dispatch to Recycler (Sorted -> Delivered to Recycler): select CPCB recycler, enter challan
- Financial ledger with 75% SHG net revenue share and CSV export
- New SHG Registration onboarding with regex scrutiny (NULM/NRLM)
- Contextual help tooltips and equal-height aligned cards
"""

import streamlit as st
import pandas as pd
import json
from typing import Optional, List, Dict, Any

from services import (
    validate_reg_id,
    validate_indian_mobile,
    validate_pin,
    validate_positive_weight,
    mask_phone,
    verify_pin,
    MEERUT_WARDS,
    AUTHORISED_RECYCLERS,
    calculate_earnings,
    REVENUE_SPLIT
)
import db
from modules.ui_common import (
    inject_custom_css,
    render_page_header,
    get_status_badge_html,
    render_status_stepper,
    render_html
)


def render_shg_portal():
    """Renders the complete Women SHG portal view."""
    inject_custom_css(dark_mode=st.session_state.get("dark_mode", False))

    render_page_header(
        icon="👩‍🦰",
        title="Women SHG Micro-Entrepreneur Portal",
        subtitle="Empowering DAY-NRLM / DAY-NULM registered women Self-Help Groups with dignified green livelihoods in Meerut.",
        badge="DAY-NRLM / NULM Partner"
    )

    # Check session state for logged-in SHG
    current_shg_id = st.session_state.get("logged_in_shg_id")

    # If not logged in, show Auth / Login Screen
    if not current_shg_id:
        _render_login_view()
        return

    # Fetch fresh SHG details
    shg_data = db.get_shg_by_id(current_shg_id)
    if not shg_data:
        st.session_state["logged_in_shg_id"] = None
        st.rerun()

    # Logged-in Header Banner
    _render_shg_header(shg_data)

    # Check Verification Status: If Pending or Rejected, block operational access
    if shg_data["status"] == "Pending Approval":
        st.warning(
            "⏳ **Verification in Progress:** Your SHG registration is currently **Pending Municipal Approval**. "
            "Under compliance guidelines, unverified groups cannot view citizen requests or accept pickup jobs. "
            "Please await verification by the Meerut Municipal Commissioner / NULM City Project Officer."
        )
        # Show only registration details & info tab
        t1, t2 = st.tabs(["📋 My Registration Details", "🌐 Official Guidelines"])
        with t1:
            st.write(f"**Group Name:** {shg_data['name']}")
            st.write(f"**Registration ID:** `{shg_data['reg_id']}`")
            st.write(f"**Portal Registry:** {shg_data['portal_type']}")
            st.write(f"**Operating Localities:** {shg_data['localities']}")
            st.write(f"**Leader:** {shg_data['leader_name']} ({mask_phone(shg_data['phone'])})")
            st.write(f"**DBT Bank Account:** `{shg_data['bank_ac_masked']}`")
            st.write(f"**Applied On:** {shg_data['created_at']}")
        with t2:
            st.info("ℹ️ SHGs in Uttar Pradesh are onboarded in partnership with DAY-NULM (Urban Livelihoods) and DAY-NRLM (State Rural Livelihoods Mission - UPSRLM).")
        return

    if shg_data["status"] == "Rejected":
        st.error(
            f"❌ **Registration Rejected:** This group was rejected during municipal scrutiny. "
            f"Reason: *{shg_data.get('rejection_reason', 'Did not meet criteria')}*."
        )
        return

    # For Approved SHGs: Full Portal Tabs
    tab_board, tab_active, tab_ledger, tab_onboard = st.tabs([
        "📲 Available Job Board",
        "📦 My Collections Workflow",
        "💰 Earnings & Statement",
        "📝 Register Another SHG"
    ])

    with tab_board:
        _render_job_board(shg_data)

    with tab_active:
        _render_collections_workflow(shg_data)

    with tab_ledger:
        _render_earnings_ledger(shg_data)

    with tab_onboard:
        _render_registration_form()


# ==========================================
# 1. LOGIN & AUTHENTICATION VIEW
# ==========================================

def _render_login_view():
    """Renders the SHG Login and Quick Demo switchers."""
    col1, col2 = st.columns([1.5, 1])

    with col1:
        render_html(
            """
            <div class="she-card she-card-highlight">
                <h4 style="margin-top:0; color:var(--primary);">🔐 SHG Leader / Member Login</h4>
                <p style="font-size:0.85rem; color:var(--muted); margin-bottom:0;">
                    Access pickup requests assigned to your operating wards, log verified weights, and manage revenue splits.
                </p>
            </div>
            """
        )

        with st.form("shg_login_form"):
            reg_id_input = st.text_input(
                "Govt. Registration ID",
                placeholder="e.g. NULM-2024-88 or NRLM-1024",
                help="Enter your official DAY-NRLM or DAY-NULM registration identifier."
            )
            pin_input = st.text_input(
                "4-Digit Security PIN",
                type="password",
                placeholder="••••",
                help="Your 4-digit PIN set during group onboarding."
            )
            login_submitted = st.form_submit_button("Sign In to SHG Hub", type="primary", use_container_width=True)

            if login_submitted:
                if not reg_id_input.strip() or not pin_input.strip():
                    st.error("Please enter both Registration ID and PIN.")
                else:
                    shg = db.get_shg_by_reg_id(reg_id_input.strip())
                    if not shg:
                        st.error("No SHG found with this Registration ID. Please check or register below.")
                    else:
                        is_valid = verify_pin(pin_input.strip(), shg["pin_salt"], shg["pin_hash"])
                        if is_valid:
                            st.session_state["logged_in_shg_id"] = shg["id"]
                            st.toast(f"Welcome, {shg['name']}!")
                            st.rerun()
                        else:
                            st.error("Incorrect PIN. Please re-enter your 4-digit security PIN.")

    with col2:
        render_html(
            """
            <div class="she-card she-card-green">
                <h4 style="margin-top:0; color:var(--success);">⚡ Quick Demo Login (Judges)</h4>
                <p style="font-size:0.85rem; color:var(--muted); margin-bottom:0;">Click below to instantly log in as a verified group:</p>
            </div>
            """
        )

        if st.button("👩‍🦰 Log in as Maa Durga SHG (NULM Urban)", use_container_width=True):
            st.session_state["logged_in_shg_id"] = "SHG-001"
            st.rerun()

        if st.button("🌾 Log in as Ekta Sakhi SHG (NRLM Rural)", use_container_width=True):
            st.session_state["logged_in_shg_id"] = "SHG-002"
            st.rerun()

        if st.button("⏳ Log in as Nav Chetna (Pending Group)", use_container_width=True):
            st.session_state["logged_in_shg_id"] = "SHG-004"
            st.rerun()

        st.caption("Default Demo PIN for all groups: `1234`")

    st.markdown("---")
    st.markdown("#### Need to Onboard a New Women's Self-Help Group?")
    with st.expander("📝 Click here to Register a New SHG under DAY-NRLM / NULM"):
        _render_registration_form()


# ==========================================
# 2. SHG HEADER BANNER
# ==========================================

def _render_shg_header(shg: Dict[str, Any]):
    """Renders profile header for logged-in SHG."""
    c_info, c_btn = st.columns([3.5, 1])
    with c_info:
        badge_html = get_status_badge_html(shg['status'])
        render_html(
            f"""
            <div style="background:var(--surface); border:1px solid var(--border); border-radius:14px; padding:16px 22px; margin-bottom:18px; box-shadow:0 4px 16px var(--shadow);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <h4 style="margin:0; color:var(--primary); font-weight:800;">{shg['name']} &nbsp; {badge_html}</h4>
                        <div style="font-size:0.85rem; color:var(--muted); margin-top:4px; line-height:1.5;">
                            <strong style="color:var(--text);">Reg ID:</strong> <code>{shg['reg_id']}</code> &nbsp;|&nbsp;
                            <strong style="color:var(--text);">Portal:</strong> {shg['portal_type']} &nbsp;|&nbsp;
                            <strong style="color:var(--text);">Leader:</strong> {shg['leader_name']} &nbsp;|&nbsp;
                            <strong style="color:var(--text);">Bank (DBT):</strong> <code>{shg['bank_ac_masked']}</code>
                        </div>
                        <div style="font-size:0.82rem; color:var(--success); font-weight:600; margin-top:4px;">
                            📍 Operating Wards: {shg['localities']}
                        </div>
                    </div>
                </div>
            </div>
            """
        )
    with c_btn:
        st.write("")
        if st.button("🚪 Sign Out", key="shg_signout", use_container_width=True):
            st.session_state["logged_in_shg_id"] = None
            st.rerun()


# ==========================================
# 3. AVAILABLE JOB BOARD
# ==========================================

def _render_job_board(shg: Dict[str, Any]):
    """Renders available pickups in SHG operating localities."""
    st.markdown("#### 📲 Open E-Waste Pickup Requests")
    st.caption(f"Showing open requests currently waiting for collection in your registered operating localities: **{shg['localities']}**.")

    open_jobs = db.get_open_jobs_for_shg(shg["id"])

    if not open_jobs:
        st.info("✅ All requests in your localities have been accepted! Check back soon for new citizen requests.")
        return

    # Ward filter
    wards_in_jobs = sorted(list(set(j["ward"] for j in open_jobs)))
    selected_ward = st.selectbox("Filter by Ward:", options=["All Operating Wards"] + wards_in_jobs)

    filtered_jobs = open_jobs
    if selected_ward != "All Operating Wards":
        filtered_jobs = [j for j in open_jobs if j["ward"] == selected_ward]

    st.write(f"**Found {len(filtered_jobs)} open request(s):**")

    for job in filtered_jobs:
        with st.container(border=True):
            c1, c2, c3 = st.columns([2, 2, 1.2])
            with c1:
                render_html(f"<div><strong style='color:var(--text);'>ID:</strong> <code>{job['id']}</code></div>")
                st.write(f"**Citizen:** {job['citizen_name']}")
                st.write(f"**Phone:** `{mask_phone(job['phone'])}`")
                st.write(f"**Address:** {job['address']} ({job['ward']})")
            with c2:
                st.write(f"**Item Category:** {job['category']}")
                st.write(f"**Estimated Weight:** {job['estimated_kg']} kg")
                st.write(f"**Preferred Slot:** {job['pickup_slot']}")
                st.caption(f"Requested on: {job['created_at']}")
            with c3:
                st.write("")
                accept_key = f"accept_btn_{job['id']}"
                if st.button("🤝 Accept Pickup", key=accept_key, type="primary", use_container_width=True):
                    success, msg = db.accept_job(job["id"], shg["id"])
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)


# ==========================================
# 4. MY COLLECTIONS WORKFLOW
# ==========================================

def _render_collections_workflow(shg: Dict[str, Any]):
    """Multi-stage collection lifecycle manager."""
    st.markdown("#### 📦 My Active Collections Lifecycle")
    st.caption("Manage requests through the statutory compliance pipeline: Assigned &rarr; Collected &rarr; Sorted &rarr; Delivered to Recycler.")

    my_jobs = db.get_shg_jobs(shg["id"])

    if not my_jobs:
        st.info("You haven't accepted any jobs yet. Visit the **Available Job Board** tab to accept open pickups.")
        return

    # Sub-tabs by status
    status_tabs = st.tabs([
        f"1. Assigned ({len([j for j in my_jobs if j['status'] == 'Assigned'])})",
        f"2. Collected ({len([j for j in my_jobs if j['status'] == 'Collected'])})",
        f"3. Sorted ({len([j for j in my_jobs if j['status'] == 'Sorted'])})",
        f"4. Delivered ({len([j for j in my_jobs if j['status'] == 'Delivered to Recycler'])})",
        f"5. Settled ({len([j for j in my_jobs if j['status'] == 'Settled'])})"
    ])

    # STAGE 1: ASSIGNED -> COLLECTED
    with status_tabs[0]:
        assigned_jobs = [j for j in my_jobs if j["status"] == "Assigned"]
        if not assigned_jobs:
            st.info("No jobs waiting for collection.")
        for job in assigned_jobs:
            with st.container(border=True):
                render_html(f"<div style='font-size:1.05rem; font-weight:700; color:var(--text); margin-bottom:8px;'>Request: <code>{job['id']}</code> - {job['citizen_name']}</div>")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**Ward:** {job['ward']}")
                    st.write(f"**Address:** {job['address']}")
                    st.write(f"**Phone:** `{mask_phone(job['phone'])}`")
                    st.write(f"**Item Category:** {job['category']}")
                    st.write(f"**Est. Weight:** {job['estimated_kg']} kg | **Slot:** {job['pickup_slot']}")
                with col_b:
                    st.markdown("**Doorstep Weighing & Safety Verification**")
                    actual_kg = st.number_input(
                        "Actual Verified Weight (kg) *",
                        min_value=0.1,
                        max_value=300.0,
                        value=float(job["estimated_kg"]),
                        step=0.1,
                        help="Verified weight using handheld calibrated digital scale.",
                        key=f"act_kg_{job['id']}"
                    )
                    ppe_check = st.checkbox(
                        "Mandatory PPE: Protective gloves & goggles worn.",
                        help="Confirms cut-resistant nitrile gloves and eye safety gear were used.",
                        key=f"ppe_{job['id']}"
                    )
                    battery_check = st.checkbox(
                        "Battery Safety: Lithium batteries sealed in puncture-proof pouch.",
                        help="Ensures critical battery packs remain sealed in dry fire-retardant pouches.",
                        key=f"batt_{job['id']}"
                    )

                    if st.button("⚖️ Mark Collected", key=f"btn_col_{job['id']}", type="primary"):
                        if not ppe_check or not battery_check:
                            st.error("Both safety checklist conditions must be confirmed before marking Collected.")
                        else:
                            ok, msg = db.mark_collected(
                                req_id=job["id"],
                                shg_id=shg["id"],
                                actual_kg=float(actual_kg),
                                safety_checked=True
                            )
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

    # STAGE 2: COLLECTED -> SORTED
    with status_tabs[1]:
        collected_jobs = [j for j in my_jobs if j["status"] == "Collected"]
        if not collected_jobs:
            st.info("No jobs awaiting sorting.")
        for job in collected_jobs:
            with st.container(border=True):
                render_html(f"<div style='font-size:1.05rem; font-weight:700; color:var(--text); margin-bottom:8px;'>Request: <code>{job['id']}</code> (Total Weight: {job['actual_kg']} kg)</div>")

                # Statutory Compliance Rule Alert
                render_html(
                    """
                    <div class="safety-box">
                        <strong>⚠️ Statutory E-Waste Rule (CPCB Guidelines):</strong><br/>
                        SHGs perform <strong>collection, aggregation and basic category sorting ONLY</strong>.
                        Industrial dismantling, shredding, and chemical refining are done exclusively by authorized recyclers.
                        Hazardous fractions like intact lithium batteries must be handed over unopened.
                    </div>
                    """
                )

                tot_w = float(job["actual_kg"])
                st.markdown("**Enter Basic Segregation Fractions (kg):**")
                s1, s2, s3, s4 = st.columns(4)
                with s1:
                    m_kg = st.number_input("Metals (kg)", min_value=0.0, max_value=tot_w, value=round(tot_w * 0.40, 2), step=0.1, key=f"m_{job['id']}")
                with s2:
                    pcb_kg = st.number_input("PC Boards (kg)", min_value=0.0, max_value=tot_w, value=round(tot_w * 0.25, 2), step=0.1, key=f"pcb_{job['id']}")
                with s3:
                    batt_kg = st.number_input("Batteries (kg)", min_value=0.0, max_value=tot_w, value=round(tot_w * 0.15, 2), step=0.1, key=f"batt_k_{job['id']}")
                with s4:
                    plast_kg = st.number_input("Plastics (kg)", min_value=0.0, max_value=tot_w, value=round(tot_w * 0.15, 2), step=0.1, key=f"pl_{job['id']}")

                if st.button("🔬 Complete Basic Sorting", key=f"btn_sort_{job['id']}", type="primary"):
                    breakdown = {
                        "metals_kg": float(m_kg),
                        "circuit_boards_kg": float(pcb_kg),
                        "lithium_batteries_kg": float(batt_kg),
                        "plastics_kg": float(plast_kg),
                        "other_kg": round(max(0.0, tot_w - (m_kg + pcb_kg + batt_kg + plast_kg)), 2)
                    }
                    ok, msg = db.mark_sorted(job["id"], shg["id"], breakdown)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    # STAGE 3: SORTED -> DELIVERED TO RECYCLER
    with status_tabs[2]:
        sorted_jobs = [j for j in my_jobs if j["status"] == "Sorted"]
        if not sorted_jobs:
            st.info("No sorted jobs ready for recycler dispatch.")
        for job in sorted_jobs:
            with st.container(border=True):
                render_html(f"<div style='font-size:1.05rem; font-weight:700; color:var(--text); margin-bottom:8px;'>Request: <code>{job['id']}</code> (Actual: {job['actual_kg']} kg)</div>")
                d1, d2 = st.columns(2)
                with d1:
                    rec_choice = st.selectbox("Select CPCB-Authorised Recycler:", options=AUTHORISED_RECYCLERS, key=f"rec_sel_{job['id']}")
                with d2:
                    challan_no = st.text_input(
                        "Recycler Handover Challan / Manifest # *",
                        value=f"REC-UP-2026-{job['seq_num'] + 8000}",
                        help="Enter the official paper or digital consignment challan number provided by the recycler.",
                        key=f"chal_{job['id']}"
                    )

                if st.button("🚛 Dispatch to Authorised Recycler", key=f"btn_deliv_{job['id']}", type="primary"):
                    if not challan_no.strip():
                        st.error("Please enter the official handover challan number.")
                    else:
                        ok, msg = db.mark_delivered_to_recycler(job["id"], shg["id"], rec_choice, challan_no.strip())
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

    # STAGE 4: DELIVERED TO RECYCLER
    with status_tabs[3]:
        delivered_jobs = [j for j in my_jobs if j["status"] == "Delivered to Recycler"]
        if not delivered_jobs:
            st.info("No jobs awaiting municipal settlement.")
        for job in delivered_jobs:
            with st.container(border=True):
                render_html(f"<div style='font-size:1.05rem; font-weight:700; color:var(--text); margin-bottom:8px;'>Request: <code>{job['id']}</code></div>")
                st.write(f"**Recycler:** {job['recycler_name']}")
                st.write(f"**Challan #:** `{job['recycler_challan_no']}`")
                st.write(f"**SHG Earnings Share:** ₹{job['shg_earnings']:.2f}")
                st.info("⏳ Awaiting Municipal Reconciliation & DBT Release to your bank account.")

    # STAGE 5: SETTLED
    with status_tabs[4]:
        settled_jobs = [j for j in my_jobs if j["status"] == "Settled"]
        if not settled_jobs:
            st.info("No settled jobs yet.")
        for job in settled_jobs:
            with st.container(border=True):
                render_html(f"<div style='font-size:1.05rem; font-weight:700; color:var(--text); margin-bottom:8px;'>Request: <code>{job['id']}</code> &nbsp; {get_status_badge_html('Settled')}</div>")
                st.write(f"**Category:** {job['category']} | **Weight:** {job['actual_kg']} kg")
                st.write(f"**Gross Value:** ₹{job['gross_value']:.2f} | **SHG Net Share (75%):** ₹{job['shg_earnings']:.2f}")
                st.success(f"✅ Settled to Bank Account `{shg['bank_ac_masked']}` via DBT.")


# ==========================================
# 5. EARNINGS & STATEMENT LEDGER
# ==========================================

def _render_earnings_ledger(shg: Dict[str, Any]):
    """Renders financial statements, revenue split breakdown, and CSV statement."""
    st.markdown("#### 💰 SHG Earnings & Financial Settlement Ledger")
    st.caption("Transparent statutory scrap revenue sharing. Net earnings are deposited via Direct Bank Transfer (DBT).")

    my_jobs = db.get_shg_jobs(shg["id"])
    completed = [j for j in my_jobs if j["status"] in ["Collected", "Sorted", "Delivered to Recycler", "Settled"]]

    total_gross = sum(j["gross_value"] for j in completed)
    total_shg = sum(j["shg_earnings"] for j in completed)
    total_logistics = sum(j["logistics_fund"] for j in completed)
    total_platform = sum(j["platform_fee"] for j in completed)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Gross E-Waste Value", f"₹{total_gross:,.2f}")
    c2.metric("SHG Share (75%)", f"₹{total_shg:,.2f}")
    c3.metric("Logistics Fund (12%)", f"₹{total_logistics:,.2f}")
    c4.metric("Completed Pickups", len(completed))

    # Revenue Split Explainer Box
    render_html(
        """
        <div class="she-card she-card-highlight">
            <h5 style="margin-top:0; color:var(--primary);">📊 Configurable Revenue Split Breakdown (Sums to 100%)</h5>
            <p style="font-size:0.85rem; color:var(--muted); line-height:1.6; margin-bottom:0;">
                • <strong style="color:var(--text);">SHG Net Share (75%):</strong> Direct micro-entrepreneur income credited to group bank account.<br/>
                • <strong style="color:var(--text);">Logistics & Safety Fund (12%):</strong> Covers digital weighing scale calibration, PPE kits, and puncture-proof bags.<br/>
                • <strong style="color:var(--text);">Municipal Platform Fee (8%):</strong> Software infrastructure, GIS routing, and administrative audit.<br/>
                • <strong style="color:var(--text);">Green Credits Fund (5%):</strong> Municipal citizen reward and community sustainability pool.
            </p>
        </div>
        """
    )

    if completed:
        ledger_data = []
        for j in completed:
            ledger_data.append({
                "Request ID": j["id"],
                "Date": j["updated_at"][:10],
                "Category": j["category"],
                "Weight (kg)": j["actual_kg"],
                "Gross (₹)": j["gross_value"],
                "SHG Share (75%)": j["shg_earnings"],
                "Logistics (12%)": j["logistics_fund"],
                "Platform (8%)": j["platform_fee"],
                "Green Fund (5%)": j["green_credit_fund"],
                "Status": j["status"]
            })
        ldf = pd.DataFrame(ledger_data)
        st.dataframe(ldf, use_container_width=True, hide_index=True)

        # Download Statement CSV
        csv_bytes = ldf.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Full Earnings Statement (CSV)",
            data=csv_bytes,
            file_name=f"SheCycle_Earnings_{shg['id']}.csv",
            mime="text/csv",
            type="primary"
        )
    else:
        st.info("No completed collections recorded yet for earnings calculation.")


# ==========================================
# 6. SHG REGISTRATION FORM (DAY-NRLM / NULM)
# ==========================================

def _render_registration_form():
    """Renders onboarding form for new SHGs."""
    st.markdown("#### 📝 Register a New Self-Help Group (SHG)")
    st.caption("Verify your group with official National Rural (DAY-NRLM) or Urban (DAY-NULM) Livelihoods Mission credentials.")

    with st.form("new_shg_reg_form"):
        r1, r2 = st.columns(2)
        with r1:
            g_name = st.text_input("SHG Group Name *", placeholder="e.g. Saraswati Mahila Swavalambi Samuh")
            p_type = st.selectbox("Government Registry *", ["DAY-NULM (Urban / Shahari)", "DAY-NRLM (Rural / Dehati)"])
            reg_id = st.text_input(
                "Govt. Registration ID *",
                placeholder="e.g. NULM-2024-99 or NRLM-8823",
                help="Validated with format: NULM-YYYY-NN or NRLM-NNNN."
            )
            leader = st.text_input("Group Leader Name *", placeholder="e.g. Sushila Devi")

        with r2:
            phone = st.text_input(
                "Mobile Number (Aadhaar linked) *",
                placeholder="e.g. 9837112233",
                help="10-digit Indian mobile number for administrative SMS alerts."
            )
            wards = st.multiselect(
                "Operating Localities / Wards *",
                options=MEERUT_WARDS,
                default=["Kankar Khera", "Modipuram"],
                help="Select the wards where your members can provide doorstep collection."
            )
            bank_ac = st.text_input(
                "SHG Bank Account (DBT) *",
                placeholder="e.g. 123456789012",
                help="Will be masked immediately upon submission (****1234) under DPDP Act rules."
            )
            pin = st.text_input(
                "Set 4-Digit Security PIN *",
                type="password",
                max_chars=4,
                placeholder="••••",
                help="Used to log into your SHG collection job board."
            )

        reg_submit = st.form_submit_button("Submit SHG for Municipal Verification", type="primary", use_container_width=True)

        if reg_submit:
            # Validations
            if not g_name.strip() or not leader.strip() or not bank_ac.strip():
                st.error("Please fill in all mandatory fields.")
            elif not wards:
                st.error("Please select at least one operating ward.")
            else:
                id_ok, clean_reg = validate_reg_id(reg_id)
                if not id_ok:
                    st.error(clean_reg)
                else:
                    phone_ok, clean_phone = validate_indian_mobile(phone)
                    if not phone_ok:
                        st.error(clean_phone)
                    else:
                        pin_ok, clean_pin = validate_pin(pin)
                        if not pin_ok:
                            st.error(clean_pin)
                        else:
                            ok, msg, new_id = db.register_shg(
                                name=g_name.strip(),
                                portal_type=p_type,
                                reg_id=clean_reg,
                                leader_name=leader.strip(),
                                phone=clean_phone,
                                localities_list=wards,
                                bank_ac=bank_ac.strip(),
                                pin=clean_pin
                            )
                            if ok:
                                st.success(f"🎉 {msg}")
                                st.info("ℹ️ Your group has been registered with status **'Pending Approval'**. Once reviewed by the Municipal Admin, you can log in to accept jobs.")
                            else:
                                st.error(msg)
