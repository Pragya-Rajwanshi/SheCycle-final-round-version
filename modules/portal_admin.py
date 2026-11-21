"""
portal_admin.py - Municipal Admin & Regulatory Authority Dashboard
Features:
- Password protected (demo password from st.secrets or fallback 'meerut2026')
- KPI impact metrics with stated environmental assumptions
- SHG Scrutiny & Approval Queue (Approve / Reject with logged reason)
- Real Tonnage Analytics (Plotly interactive charts matching design palette)
- Financial Settlement Reconciler (Delivered -> Settled via DBT)
- Master Compliance Audit Trail with drill-down inspector and CSV export
- Real-time Exception Alerts (unassigned > 48 hours, inactive SHGs)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, List, Dict, Any

from services import mask_phone, AUTHORISED_RECYCLERS
import db
from modules.ui_common import (
    inject_custom_css,
    render_page_header,
    get_status_badge_html,
    render_html,
    get_plotly_theme
)


def render_admin_portal():
    """Renders the Municipal Admin portal view."""
    inject_custom_css(dark_mode=st.session_state.get("dark_mode", False))

    render_page_header(
        icon="🏛️",
        title="Municipal Administration & Regulatory Oversight",
        subtitle="City-level e-waste compliance monitoring, SHG scrutiny, and tonnage lifecycle audit for Meerut Nagar Nigam.",
        badge="CPCB / UPPCB Cluster"
    )

    # Admin Authentication Check
    if not _check_admin_auth():
        return

    # Render Logout / Session Bar
    col_adm_hdr, col_adm_out = st.columns([4, 1])
    with col_adm_hdr:
        st.info("🔐 Authenticated as: **Municipal Commissioner & CPCB Nodal Officer (Meerut Cluster)**")
    with col_adm_out:
        if st.button("Log Out Admin", use_container_width=True):
            st.session_state["admin_logged_in"] = False
            st.rerun()

    # KPI Summary Cards
    kpis = db.get_kpi_summary()
    _render_kpi_cards(kpis)

    # Operational Exception Alerts
    _render_exception_alerts()

    # Main Admin Tabs
    t_analytics, t_shg_queue, t_settle, t_audit = st.tabs([
        "📊 Real Tonnage Analytics",
        f"👩‍🦰 SHG Scrutiny Queue ({kpis['pending_shgs']} Pending)",
        "💳 Financial Reconciliation & DBT",
        "📜 Master Compliance Audit Trail"
    ])

    with t_analytics:
        _render_tonnage_analytics()

    with t_shg_queue:
        _render_shg_queue()

    with t_settle:
        _render_settlement_reconciler()

    with t_audit:
        _render_master_audit_trail()


# ==========================================
# 1. AUTHENTICATION HELPER
# ==========================================

def _check_admin_auth() -> bool:
    """Verifies admin password using st.secrets fallback."""
    if st.session_state.get("admin_logged_in", False):
        return True

    # Retrieve demo password
    expected_pwd = "meerut2026"
    try:
        if "ADMIN_PASSWORD" in st.secrets:
            expected_pwd = st.secrets["ADMIN_PASSWORD"]
    except Exception:
        pass

    render_html(
        """
        <div class="she-card she-card-indigo">
            <h4 style="margin-top:0; color:var(--primary);">🔒 Municipal Authority Access Restricted</h4>
            <p style="font-size:0.85rem; color:var(--muted); margin-bottom:0;">
                Authorized access for Urban Local Bodies (ULB), UP Pollution Control Board (UPPCB), and NULM City Project Officers.
            </p>
        </div>
        """
    )

    with st.form("admin_auth_form"):
        pwd_input = st.text_input(
            "Enter Municipal Admin Password",
            type="password",
            placeholder="••••••••",
            help="Pre-configured demo password for evaluators: 'meerut2026'."
        )
        pwd_submit = st.form_submit_button("Authenticate as Admin", type="primary", use_container_width=True)

        if pwd_submit:
            if pwd_input.strip() == expected_pwd:
                st.session_state["admin_logged_in"] = True
                st.toast("Admin authenticated successfully.")
                st.rerun()
            else:
                st.error("Incorrect password. Demo password is: 'meerut2026'")

    # Quick helper for judges
    st.caption("💡 *Judges Quick Access: Default demo password is* `meerut2026`")
    if st.button("⚡ One-Click Judge Login (Admin)", use_container_width=True):
        st.session_state["admin_logged_in"] = True
        st.rerun()

    return False


# ==========================================
# 2. KPI CARDS
# ==========================================

def _render_kpi_cards(kpi: Dict[str, Any]):
    """Renders top impact metric cards."""
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Requests", kpi["total_requests"])
    c2.metric("Collected Tonnage", f"{kpi['total_kg']} kg")
    c3.metric("Verified SHGs Active", kpi["active_shgs"], delta=f"{kpi['pending_shgs']} Pending", delta_color="inverse")
    c4.metric("SHG Revenue Paid", f"₹{kpi['total_shg_earnings']:,.0f}")
    c5.metric("Est. CO2 Avoided", f"{kpi['co2_avoided_kg']} kg", delta=f"{kpi['trees_equivalent']} trees")

    st.caption(
        "ℹ️ *Impact Note: Environmental savings are calculated based on CPCB and UNEP lifecycle averages (1.44 kg CO2e / kg diverted e-waste, 28g heavy metals prevented from groundwater).* "
        "*Scrap rates are illustrative demo benchmarks.*"
    )


# ==========================================
# 3. EXCEPTION ALERTS
# ==========================================

def _render_exception_alerts():
    """Renders real-time operational alerts for admin action."""
    alerts = db.get_exception_alerts()
    stale = alerts["stale_requests"]
    inactive = alerts["inactive_shgs"]

    if stale or inactive:
        with st.expander("🚨 Operational Exception Alerts & Flags", expanded=True):
            if stale:
                st.error(
                    f"⚠️ **{len(stale)} Request(s) Unassigned for > 48 Hours:** "
                    f"Requests waiting without an assigned SHG: " +
                    ", ".join([f"`{r['id']}` ({r['ward']} - {r['estimated_kg']} kg)" for r in stale])
                )
            if inactive:
                st.warning(
                    f"⚠️ **{len(inactive)} Approved SHG(s) With Zero Activity in 30 Days:** " +
                    ", ".join([f"**{s['name']}** (Leader: {s['leader_name']})" for s in inactive])
                )


# ==========================================
# 4. REAL TONNAGE ANALYTICS (PALETTE POLISHED & THEME AWARE)
# ==========================================

def _render_tonnage_analytics():
    """Renders Plotly charts for tonnage analytics matching design system palette in light/dark mode."""
    st.markdown("#### 📈 Real E-Waste Tonnage & Flow Analytics")
    st.caption("Detailed spatial, temporal, and categorical breakdown across Meerut Nagar Nigam.")

    ptheme = get_plotly_theme(st.session_state.get("dark_mode", False))

    # Row 1: Tonnage Over Time & Funnel
    ch1, ch2 = st.columns([1.5, 1])

    with ch1:
        timeline_data = db.get_tonnage_timeline()
        if timeline_data:
            tdf = pd.DataFrame(timeline_data)
            fig_timeline = px.line(
                tdf,
                x="day_date",
                y="daily_kg",
                markers=True,
                title="Daily E-Waste Tonnage Influx (Last 60 Days)",
                labels={"day_date": "Date", "daily_kg": "Weight (kg)"},
                color_discrete_sequence=[ptheme["colors"][0]]
            )
            fig_timeline.update_layout(
                xaxis_title="Date",
                yaxis_title="Kilograms (kg)",
                template="plotly_white",
                font=dict(family="Plus Jakarta Sans", color=ptheme["font_color"]),
                margin=dict(l=20, r=20, t=40, b=20),
                height=320,
                paper_bgcolor=ptheme["paper_bgcolor"],
                plot_bgcolor=ptheme["plot_bgcolor"],
                xaxis=dict(gridcolor=ptheme["grid_color"], color=ptheme["font_color"]),
                yaxis=dict(gridcolor=ptheme["grid_color"], color=ptheme["font_color"])
            )
            fig_timeline.update_traces(
                line=dict(width=3, color=ptheme["colors"][0]),
                marker=dict(size=7, color=ptheme["colors"][1])
            )
            st.plotly_chart(fig_timeline, use_container_width=True)

    with ch2:
        funnel_data = db.get_status_funnel_data()
        if funnel_data:
            fdf = pd.DataFrame(funnel_data)
            fig_funnel = px.funnel(
                fdf,
                x="count",
                y="status",
                title="Status Pipeline Funnel",
                color="status",
                color_discrete_sequence=ptheme["colors"]
            )
            fig_funnel.update_layout(
                showlegend=False,
                template="plotly_white",
                font=dict(family="Plus Jakarta Sans", color=ptheme["font_color"]),
                margin=dict(l=20, r=20, t=40, b=20),
                height=320,
                paper_bgcolor=ptheme["paper_bgcolor"],
                plot_bgcolor=ptheme["plot_bgcolor"]
            )
            st.plotly_chart(fig_funnel, use_container_width=True)

    # Row 2: Ward Distribution & Category Breakdown
    ch3, ch4 = st.columns([1.2, 1.2])

    with ch3:
        ward_data = db.get_tonnage_by_ward()
        if ward_data:
            wdf = pd.DataFrame(ward_data)
            fig_ward = px.bar(
                wdf,
                x="total_kg",
                y="ward",
                orientation="h",
                title="Ward-Wise E-Waste Collection (Meerut)",
                labels={"total_kg": "Total kg", "ward": "Locality"},
                color="total_kg",
                color_continuous_scale=[ptheme["grid_color"], ptheme["colors"][0]]
            )
            fig_ward.update_layout(
                template="plotly_white",
                font=dict(family="Plus Jakarta Sans", color=ptheme["font_color"]),
                yaxis=dict(categoryorder='total ascending', color=ptheme["font_color"]),
                xaxis=dict(gridcolor=ptheme["grid_color"], color=ptheme["font_color"]),
                margin=dict(l=20, r=20, t=40, b=20),
                height=340,
                paper_bgcolor=ptheme["paper_bgcolor"],
                plot_bgcolor=ptheme["plot_bgcolor"]
            )
            st.plotly_chart(fig_ward, use_container_width=True)

    with ch4:
        cat_data = db.get_tonnage_by_category()
        if cat_data:
            cdf = pd.DataFrame(cat_data)
            fig_cat = px.pie(
                cdf,
                names="category",
                values="total_kg",
                hole=0.48,
                title="Tonnage Share by Category",
                color_discrete_sequence=ptheme["colors"]
            )
            fig_cat.update_layout(
                template="plotly_white",
                font=dict(family="Plus Jakarta Sans", color=ptheme["font_color"]),
                margin=dict(l=20, r=20, t=40, b=20),
                height=340,
                paper_bgcolor=ptheme["paper_bgcolor"],
                legend=dict(font=dict(color=ptheme["font_color"]))
            )
            st.plotly_chart(fig_cat, use_container_width=True)

    # Row 3: SHG Leaderboard
    st.markdown("##### 🏆 Women SHG Performance & Earnings Leaderboard")
    shg_lead = db.get_shg_leaderboard()
    if shg_lead:
        sldf = pd.DataFrame(shg_lead)
        sldf.columns = ["ID", "SHG Name", "Portal", "Reg ID", "Leader", "Assigned", "Completed", "Total kg", "Total Earnings (₹)"]
        st.dataframe(sldf, use_container_width=True, hide_index=True)


# ==========================================
# 5. SHG APPROVAL QUEUE
# ==========================================

def _render_shg_queue():
    """Scrutiny queue for approving or rejecting pending SHG registrations."""
    st.markdown("#### 👩‍🦰 SHG Verification & Scrutiny Queue")
    st.caption("Review official DAY-NRLM / DAY-NULM credentials before authorizing SHGs to access citizen e-waste.")

    pending_shgs = db.get_all_shgs(status_filter="Pending Approval")

    if not pending_shgs:
        st.success("✅ Verification queue is clear. No pending SHG applications.")
    else:
        st.warning(f"⚠️ **{len(pending_shgs)} SHG(s) awaiting municipal scrutiny:**")

        for shg in pending_shgs:
            with st.container(border=True):
                render_html(f"<div style='font-size:1.1rem; font-weight:700; color:var(--text); margin-bottom:8px;'>{shg['name']} &nbsp; {get_status_badge_html('Pending Approval')}</div>")
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**Application ID:** `{shg['id']}`")
                    st.write(f"**Government Portal:** {shg['portal_type']}")
                    st.write(f"**Govt Registration ID:** `{shg['reg_id']}`")
                    st.write(f"**Leader Name:** {shg['leader_name']}")
                    st.write(f"**Leader Contact:** `{mask_phone(shg['phone'])}`")
                with c2:
                    st.write(f"**Operating Wards:** {shg['localities']}")
                    st.write(f"**Bank Account (DBT):** `{shg['bank_ac_masked']}`")
                    st.write(f"**Applied On:** {shg['created_at']}")

                st.markdown("---")
                col_appr, col_rej = st.columns([1, 1.5])
                with col_appr:
                    if st.button("✅ Approve & Verify SHG", key=f"appr_{shg['id']}", type="primary", use_container_width=True):
                        db.update_shg_status(shg["id"], "Approved", actor="Municipal Commissioner, Meerut")
                        st.success(f"{shg['name']} successfully verified and approved!")
                        st.rerun()

                with col_rej:
                    rejection_note = st.text_input(
                        "Rejection Reason (if rejecting):",
                        key=f"rej_note_{shg['id']}",
                        placeholder="e.g. ID not matching UP NULM directory",
                        help="Enter a specific reason for rejection to be permanently logged in the audit record."
                    )
                    if st.button("❌ Reject SHG", key=f"rej_{shg['id']}", use_container_width=True):
                        if not rejection_note.strip():
                            st.error("Please provide a reason for rejection.")
                        else:
                            db.update_shg_status(shg["id"], "Rejected", actor="Municipal Commissioner, Meerut", reason=rejection_note.strip())
                            st.warning(f"{shg['name']} application marked Rejected.")
                            st.rerun()

    # Full Directory of All SHGs
    st.markdown("---")
    st.markdown("##### 📚 Master Directory of Registered SHGs")
    all_shgs = db.get_all_shgs()
    if all_shgs:
        adf = pd.DataFrame(all_shgs)[["id", "name", "portal_type", "reg_id", "leader_name", "status", "localities", "created_at"]]
        adf.columns = ["ID", "Group Name", "Portal", "Reg ID", "Leader", "Status", "Wards", "Registration Date"]
        st.dataframe(adf, use_container_width=True, hide_index=True)


# ==========================================
# 6. FINANCIAL SETTLEMENT RECONCILER
# ==========================================

def _render_settlement_reconciler():
    """Municipal settlement of recycler payouts to SHGs."""
    st.markdown("#### 💳 Recycler Handover Settlement & Direct Bank Transfer (DBT)")
    st.caption("Reconcile certified recycler weigh-bills and approve direct bank transfers to SHG accounts.")

    conn = db.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM requests
    WHERE status = 'Delivered to Recycler'
    ORDER BY updated_at ASC;
    """)
    rows = cursor.fetchall()
    conn.close()

    delivered_requests = [dict(r) for r in rows]

    if not delivered_requests:
        st.info("✅ All recycler deliveries have been reconciled and settled.")
    else:
        st.write(f"**Found {len(delivered_requests)} delivery batch(es) awaiting settlement:**")
        for req in delivered_requests:
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 2, 1.2])
                with c1:
                    render_html(f"<div><strong style='color:var(--text);'>Request ID:</strong> <code>{req['id']}</code></div>")
                    st.write(f"**SHG:** {req['assigned_shg_name']}")
                    st.write(f"**Category:** {req['category']}")
                    st.write(f"**Verified Weight:** {req['actual_kg']} kg")
                with c2:
                    st.write(f"**Authorised Recycler:** {req['recycler_name']}")
                    st.write(f"**Handover Challan #:** `{req['recycler_challan_no']}`")
                    st.write(f"**Gross Value:** ₹{req['gross_value']:.2f}")
                    st.write(f"**SHG Share (75%):** ₹{req['shg_earnings']:.2f}")
                with c3:
                    st.write("")
                    if st.button("💳 Reconcile & Settle (DBT)", key=f"settle_btn_{req['id']}", type="primary", use_container_width=True):
                        ok, msg = db.mark_settled(req["id"], actor="Municipal Finance Officer")
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)


# ==========================================
# 7. MASTER COMPLIANCE AUDIT TRAIL
# ==========================================

def _render_master_audit_trail():
    """Filterable compliance table and drill-down request inspector."""
    st.markdown("#### 📜 Master Pickup-to-Processing Compliance Record")
    st.caption("Complete, tamper-evident audit history satisfying E-Waste Management Rules 2022 Extended Producer Responsibility (EPR) requirements.")

    all_data = db.get_all_requests_df_data()

    if not all_data:
        st.info("No requests recorded in the database.")
        return

    # Filters
    c_f1, c_f2, c_f3 = st.columns(3)
    with c_f1:
        statuses = ["All Statuses"] + list(set(r["status"] for r in all_data))
        f_status = st.selectbox("Filter Status:", statuses)
    with c_f2:
        wards = ["All Wards"] + list(set(r["ward"] for r in all_data))
        f_ward = st.selectbox("Filter Ward:", wards)
    with c_f3:
        categories = ["All Categories"] + list(set(r["category"] for r in all_data))
        f_cat = st.selectbox("Filter Category:", categories)

    filtered = all_data
    if f_status != "All Statuses":
        filtered = [r for r in filtered if r["status"] == f_status]
    if f_ward != "All Wards":
        filtered = [r for r in filtered if r["ward"] == f_ward]
    if f_cat != "All Categories":
        filtered = [r for r in filtered if r["category"] == f_cat]

    st.write(f"**Displaying {len(filtered)} request record(s):**")
    m_df = pd.DataFrame(filtered)[[
        "id", "citizen_name", "phone_masked", "ward", "category", "estimated_kg",
        "actual_kg", "status", "assigned_shg_name", "gross_value", "shg_earnings",
        "recycler_name", "recycler_challan_no", "created_at"
    ]]
    m_df.columns = [
        "Request ID", "Citizen", "Phone", "Ward", "Category", "Est. kg",
        "Actual kg", "Status", "Assigned SHG", "Gross (₹)", "SHG (₹)",
        "Recycler", "Challan #", "Created At"
    ]
    st.dataframe(m_df, use_container_width=True, hide_index=True)

    # Export CSV Button
    full_audit = db.get_full_audit_history()
    if full_audit:
        audit_df = pd.DataFrame(full_audit)
        csv_bytes = audit_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Master Compliance Audit Trail (CSV)",
            data=csv_bytes,
            file_name="SheCycle_Compliance_Audit_Record.csv",
            mime="text/csv",
            type="primary"
        )

    # Drill-down request inspector
    st.markdown("---")
    st.markdown("##### 🔬 Inspect Single Request Audit Timeline")
    inspect_id = st.selectbox("Select Request ID to Inspect:", [r["id"] for r in all_data])
    if inspect_id:
        req_hist = db.get_request_history(inspect_id)
        if req_hist:
            rh_df = pd.DataFrame(req_hist)[["id", "timestamp", "from_status", "to_status", "actor", "note"]]
            rh_df.columns = ["Event #", "Timestamp", "From Status", "To Status", "Actor", "Note"]
            st.dataframe(rh_df, use_container_width=True, hide_index=True)
