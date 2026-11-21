"""
portal_citizen.py - Citizen Doorstep E-Waste Pickup Portal
Features:
- Bilingual English/Hindi toggle
- Doorstep request form with input validation (Indian mobile, positive weight)
- Safety advisory (factory reset, battery handling) & DPDP Act consent
- Sequential Request ID generation + QR code + Green Credits estimate
- Secure tracking requiring Request ID + last 4 digits of phone
- Interactive status timeline and audit history
- Green Credits wallet and privacy-preserving community leaderboard
- Contextual help tooltips and responsive, clean typography
"""

import streamlit as st
import pandas as pd
from typing import Optional

from services import (
    validate_reg_id,
    validate_indian_mobile,
    validate_positive_weight,
    mask_phone,
    MEERUT_WARDS,
    SCRAP_RATES,
    calculate_earnings
)
import db
from modules.ui_common import (
    t,
    inject_custom_css,
    render_page_header,
    render_status_stepper,
    get_status_badge_html,
    generate_qr_image,
    render_html
)


def render_citizen_portal():
    """Renders the complete Citizen portal view."""
    inject_custom_css(dark_mode=st.session_state.get("dark_mode", False))

    # Bilingual Language Selector in Header Row
    col_lang_spc, col_lang = st.columns([3.5, 1])
    with col_lang:
        lang_choice = st.radio(
            "🌐 भाषा / Language",
            options=["English", "हिंदी"],
            horizontal=True,
            key="citizen_lang_toggle"
        )
        lang = "hi" if lang_choice == "हिंदी" else "en"

    # Standardized Page Header
    render_page_header(
        icon="👤",
        title=t("doorstep_title", lang),
        subtitle=t("doorstep_sub", lang),
        badge="Zero Convenience Fee" if lang == "en" else "निःशुल्क सेवा"
    )

    tab_request, tab_track, tab_credits = st.tabs([
        f"📝 {('अनुरोध दर्ज करें' if lang == 'hi' else 'Request Pickup')}",
        f"🔍 {('अनुरोध ट्रैक करें' if lang == 'hi' else 'Track Request')}",
        f"🌱 {('ग्रीन क्रेडिट्स वॉलेट' if lang == 'hi' else 'Green Credits & Wallet')}"
    ])

    # ==========================================
    # TAB 1: PICKUP REQUEST FORM
    # ==========================================
    with tab_request:
        render_html(
            f"""
            <div class="she-card she-card-green">
                <h4 style="margin-top:0; color:var(--success);">⚡ {('त्वरित ३-चरण पिकअप प्रक्रिया' if lang == 'hi' else 'Fast Doorstep Recycling in 3 Steps')}</h4>
                <p style="font-size:0.9rem; color:var(--muted); margin-bottom:0; line-height:1.5;">
                    {('फॉर्म भरें &rarr; स्थानीय सत्यापित महिला SHG आपके घर आकर संग्रह करेगी &rarr; ग्रीन क्रेडिट्स प्राप्त करें!' if lang == 'hi'
                      else 'Fill simple details &rarr; Verified Women SHG collects at your doorstep &rarr; Earn Green Credits & support local women micro-entrepreneurs!')}
                </p>
            </div>
            """
        )

        with st.form("citizen_pickup_form", clear_on_submit=False):
            st.markdown(f"##### 1. {('व्यक्तिगत एवं संपर्क विवरण' if lang == 'hi' else 'Contact & Location Details')}")
            c1, c2 = st.columns(2)
            with c1:
                name_input = st.text_input(
                    f"{t('your_name', lang)} *",
                    placeholder="e.g. Rahul Sharma / राहुल शर्मा",
                    help="Your full legal or preferred name for pickup handover verification.",
                    key="cit_name"
                )
                phone_input = st.text_input(
                    f"{t('phone_label', lang)} *",
                    placeholder="e.g. 9876543210 (10 digits)",
                    help="Used for collection OTP verification and secure dual-key tracking authentication.",
                    key="cit_phone"
                )
            with c2:
                ward_input = st.selectbox(
                    f"{t('ward_label', lang)} *",
                    options=MEERUT_WARDS,
                    index=0,
                    help="Select the Meerut ward or locality where the items are located for routing to local SHGs.",
                    key="cit_ward"
                )
                address_input = st.text_input(
                    f"{t('address_label', lang)} *",
                    placeholder="e.g. House 42, Pocket B, Near Temple",
                    help="Detailed street address, building/flat number, and prominent landmark.",
                    key="cit_address"
                )

            st.markdown("---")
            st.markdown(f"##### 2. {('ई-कचरा सामग्री एवं वजन' if lang == 'hi' else 'E-Waste Items & Quantity')}")
            c3, c4 = st.columns(2)
            with c3:
                category_list = list(SCRAP_RATES.keys())
                category_input = st.selectbox(
                    f"{t('category_label', lang)} *",
                    options=category_list,
                    index=0,
                    help="Select the predominant electronic scrap category.",
                    key="cit_cat"
                )
                weight_input = st.number_input(
                    f"{t('estimated_weight_label', lang)} *",
                    min_value=0.2,
                    max_value=300.0,
                    value=2.0,
                    step=0.5,
                    format="%.1f",
                    help="Approximate weight. Actual weight will be verified using calibrated digital scales upon doorstep collection.",
                    key="cit_weight"
                )
            with c4:
                slot_options = [
                    "Morning (9 AM - 12 PM)",
                    "Afternoon (1 PM - 4 PM)",
                    "Evening (4 PM - 7 PM)",
                    "Weekend Special"
                ]
                slot_input = st.selectbox(
                    f"{t('pickup_slot_label', lang)} *",
                    options=slot_options,
                    index=0,
                    help="Preferred time window when you will be available for doorstep handover.",
                    key="cit_slot"
                )
                photo_file = st.file_uploader(
                    f"{('उपकरण का फोटो (वैकल्पिक)' if lang == 'hi' else 'Device Photo (Optional)')}",
                    type=["jpg", "jpeg", "png"],
                    help="Upload a snap of your scrap for faster identification by the SHG collector.",
                    key="cit_photo"
                )

            # Safety Advisory Box
            render_html(
                f"""
                <div class="safety-box">
                    <strong>{t('safety_advisory_title', lang)}</strong><br/>
                    {t('safety_advisory_text', lang)}
                </div>
                """
            )

            # DPDP Consent Checkbox
            consent_checked = st.checkbox(
                t('consent_text', lang),
                value=False,
                help="Statutory consent required under Section 6 of India's DPDP Act 2023.",
                key="cit_consent"
            )

            submitted = st.form_submit_button(
                f"🚀 {t('submit_pickup', lang)}",
                use_container_width=True,
                type="primary"
            )

            if submitted:
                # Validation checks
                if not name_input.strip():
                    st.error("Please enter your name." if lang == "en" else "कृपया अपना नाम दर्ज करें।")
                elif not address_input.strip():
                    st.error("Please enter your complete address." if lang == "en" else "कृपया अपना पूरा पता दर्ज करें।")
                else:
                    phone_valid, clean_phone = validate_indian_mobile(phone_input)
                    if not phone_valid:
                        st.error(clean_phone)
                    elif not consent_checked:
                        st.error("Please accept the minimal data consent under the DPDP Act 2023." if lang == "en" else "कृपया DPDP अधिनियम 2023 के तहत डेटा उपयोग सहमति को स्वीकार करें।")
                    else:
                        photo_name = photo_file.name if photo_file else None
                        try:
                            req_id, credits = db.create_pickup_request(
                                citizen_name=name_input.strip(),
                                phone=clean_phone,
                                address=address_input.strip(),
                                ward=ward_input,
                                category=category_input,
                                estimated_kg=float(weight_input),
                                pickup_slot=slot_input,
                                photo_name=photo_name
                            )
                            st.session_state["last_created_req_id"] = req_id
                            st.session_state["last_created_phone_last4"] = clean_phone[-4:]
                            st.session_state["last_created_credits"] = credits
                            st.balloons()
                        except Exception as e:
                            st.error(f"Error submitting request: {str(e)}")

        # Post-submission confirmation display
        if "last_created_req_id" in st.session_state:
            req_id = st.session_state["last_created_req_id"]
            credits = st.session_state["last_created_credits"]
            p_last4 = st.session_state["last_created_phone_last4"]

            st.markdown("---")
            st.success(
                f"🎉 **Request Registered Successfully!** Your unique Request ID is **`{req_id}`**."
                if lang == "en" else
                f"🎉 **अनुरोध सफलतापूर्वक दर्ज हुआ!** आपकी अनुरोध संख्या **`{req_id}`** है।"
            )

            col_res1, col_res2 = st.columns([2, 1])
            with col_res1:
                render_html(
                    f"""
                    <div class="she-card she-card-highlight">
                        <h4 style="margin-top:0; color:var(--primary);">📋 {('पिकअप विवरण कार्ड' if lang == 'hi' else 'Pickup Summary Card')}</h4>
                        <p><strong>Request ID:</strong> <code>{req_id}</code></p>
                        <p><strong>Tracking Auth:</strong> Request ID + Last 4 digits of phone (<code>{p_last4}</code>)</p>
                        <p><strong>Assigned Ward:</strong> {st.session_state.get('cit_ward', 'Meerut')}</p>
                        <p><strong>Estimated Green Credits:</strong> <span style="color:var(--success); font-weight:700; font-size:1.1rem;">+{credits} Credits</span></p>
                        <p style="font-size:0.85rem; color:var(--muted); margin-bottom:0;">
                            {('हमारे नजदीकी नगर निगम सत्यापित महिला स्वयं सहायता समूह को यह अनुरोध भेज दिया गया है।' if lang == 'hi'
                              else 'Your pickup request has been routed to the verified local Women SHG operating in your ward.')}
                        </p>
                    </div>
                    """
                )
            with col_res2:
                st.markdown(f"**{'पिकअप क्यूआर कोड' if lang == 'hi' else 'Digital Pickup QR Pass'}**")
                qr_buf = generate_qr_image(f"SheCycle:{req_id}:{p_last4}")
                if qr_buf:
                    st.image(qr_buf, caption=f"Scan upon SHG Doorstep Arrival\nID: {req_id}", width=180)
                else:
                    st.info(f"QR Token: SheCycle:{req_id}")

    # ==========================================
    # TAB 2: SECURE REQUEST TRACKING
    # ==========================================
    with tab_track:
        st.markdown(f"#### 🔍 {t('track_title', lang)}")
        st.caption(
            "To safeguard citizen privacy under DPDP Act principles, tracking requires both your Request ID and the last 4 digits of your registered mobile number."
            if lang == "en" else
            "डेटा सुरक्षा हेतु, अपने अनुरोध की स्थिति देखने के लिए अपनी अनुरोध संख्या एवं पंजीकृत मोबाइल के अंतिम ४ अंक दर्ज करें।"
        )

        default_req = st.session_state.get("last_created_req_id", "EW-00001")
        default_last4 = st.session_state.get("last_created_phone_last4", "3210")

        c_t1, c_t2, c_t3 = st.columns([2, 1.5, 1])
        with c_t1:
            track_id_input = st.text_input(
                t('enter_req_id', lang),
                value=default_req,
                help="Your sequential EW-XXXXX request identifier.",
                key="track_req_id"
            )
        with c_t2:
            track_phone_input = st.text_input(
                t('enter_phone_last4', lang),
                value=default_last4,
                max_chars=4,
                help="Last 4 digits of the mobile number entered during request booking.",
                key="track_last4"
            )
        with c_t3:
            st.write("")
            st.write("")
            track_btn = st.button("🔎 Check Status" if lang == "en" else "🔎 स्थिति जांचें", type="primary", use_container_width=True)

        if track_btn or track_id_input:
            if not track_id_input.strip() or not track_phone_input.strip():
                st.warning("Please provide both Request ID and last 4 digits of mobile." if lang == "en" else "कृपया दोनों विवरण दर्ज करें।")
            else:
                req_data = db.track_request(track_id_input.strip(), track_phone_input.strip())
                if not req_data:
                    st.error(
                        "❌ No matching request found for this ID and phone combination. Please check your credentials."
                        if lang == "en" else
                        "❌ इस अनुरोध संख्या एवं मोबाइल अंतिम ४ अंकों का कोई मिलान नहीं मिला। कृपया पुनः जांचें।"
                    )
                else:
                    st.markdown("---")
                    render_html(
                        f"""
                        <div style="display:flex; align-items:center; gap:12px; margin:14px 0;">
                            <h3 style="margin:0; color:var(--text);">Current Status:</h3>
                            <div>{get_status_badge_html(req_data['status'])}</div>
                        </div>
                        """
                    )

                    # Visual Stepper Bar with Connecting Lines
                    render_status_stepper(req_data["status"], lang=lang)

                    # Request Detail Cards
                    st.write("")
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Request ID", req_data["id"])
                    m2.metric("Ward / Locality", req_data["ward"])
                    weight_display = f"{req_data['actual_kg']} kg (Weighed)" if req_data['actual_kg'] else f"{req_data['estimated_kg']} kg (Est.)"
                    m3.metric("Weight", weight_display)
                    m4.metric("Green Credits", f"{req_data['green_credits_citizen']} Pts")

                    # Assigned SHG info
                    assigned_shg = req_data["assigned_shg_name"] or "Awaiting Local SHG Pickup Acceptance"
                    st.info(f"🤝 **Assigned Women SHG Partner:** {assigned_shg}")

                    # Detailed Chronological Audit Trail
                    st.markdown(f"##### 📜 {('विस्तृत ऑडिट टाइमलाइन (प्रमाणीकरण इतिहास)' if lang == 'hi' else 'Detailed Status Transition Audit Trail')}")
                    history = db.get_request_history(req_data["id"])
                    if history:
                        hist_df = pd.DataFrame(history)[["timestamp", "from_status", "to_status", "actor", "note"]]
                        hist_df.columns = ["Timestamp", "From", "To", "Actor", "Action Note"]
                        st.dataframe(hist_df, use_container_width=True, hide_index=True)

    # ==========================================
    # TAB 3: GREEN CREDITS WALLET & LEADERBOARD
    # ==========================================
    with tab_credits:
        st.markdown(f"#### 🌱 {('ग्रीन क्रेडिट्स वॉलेट एवं समुदाय लीडरबोर्ड' if lang == 'hi' else 'Green Credits Wallet & Community Leaderboard')}")
        st.caption(
            "Every kilogram of safely segregated e-waste diverted from toxic groundwater earns you Green Credits, redeemable for municipal property tax rebates and eco-partner coupons."
            if lang == "en" else
            "सुरक्षित रूप से एकत्र किए गए ई-कचरे के प्रत्येक किलोग्राम पर आपको ग्रीन क्रेडिट मिलते हैं, जिन्हें नगर निगम कर छूट या पर्यावरण-अनुकूल कूपन में भुनाया जा सकता है।"
        )

        col_w1, col_w2 = st.columns([1.5, 2])
        with col_w1:
            render_html(
                """
                <div class="she-card she-card-green">
                    <h4 style="margin-top:0; color:var(--success);">📊 Green Credit Multipliers</h4>
                    <p style="font-size:0.85rem; color:var(--muted);">Earned per kg upon verified doorstep collection:</p>
                    <ul style="font-size:0.85rem; padding-left:18px; color:var(--text); line-height:1.6;">
                        <li><strong>Smartphones & Devices:</strong> 25 Credits/kg</li>
                        <li><strong>Laptops & Computers:</strong> 20 Credits/kg</li>
                        <li><strong>Lithium Batteries (Critical):</strong> 30 Credits/kg</li>
                        <li><strong>Small Home Appliances:</strong> 10 Credits/kg</li>
                        <li><strong>Mixed Scrap:</strong> 12 Credits/kg</li>
                    </ul>
                    <hr style="border:none; border-top:1px solid var(--border); margin:12px 0;"/>
                    <p style="font-size:0.8rem; color:var(--success); margin-bottom:0;">
                        💡 <em>100 Green Credits = ₹50 Municipal Property Tax Rebate (Simulated Meerut Pilot Policy)</em>
                    </p>
                </div>
                """
            )

        with col_w2:
            st.markdown(f"##### 🏆 {('मेरठ के शीर्ष पर्यावरण प्रहरी (नागरिक लीडरबोर्ड)' if lang == 'hi' else 'Top Meerut Green Champions (Leaderboard)')}")
            st.caption(
                "Privacy Notice: Under DPDP Act principles, only first names and localities are displayed."
                if lang == "en" else
                "डेटा गोपनीयता: केवल प्रथम नाम एवं वार्ड प्रदर्शित किया गया है।"
            )
            leaderboard = db.get_citizen_leaderboard()
            if leaderboard:
                ldf = pd.DataFrame(leaderboard)
                ldf.columns = ["Champion (Ward)", "Green Credits", "Kg Recycled"]
                st.dataframe(ldf, use_container_width=True, hide_index=True)
