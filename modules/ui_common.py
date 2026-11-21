"""
ui_common.py - Common UI Components, Custom Theme CSS, Bilingual Support & Helpers
Brand Palette:
- Deep Indigo / Purple: #3B2F72
- Vibrant Pink Accent: #E8318A
- Sustainability Emerald: #0D9488 / #10B981
- Soft Background Tint: #F8FAFC
"""

import streamlit as st
import io
from typing import Dict, Any, List, Optional

# ==========================================
# 1. BILINGUAL TRANSLATION DICTIONARY
# ==========================================

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "app_title": {
        "en": "SheCycle: Women-Led Smart E-Waste Management",
        "hi": "शीसाइकिल (SheCycle): महिला स्वयं सहायता समूह ई-कचरा प्रबंधन प्रणाली"
    },
    "tagline": {
        "en": "Transforming Waste Management into Women-Led Prosperity",
        "hi": "ई-कचरे का सुरक्षित समाधान, महिला आत्मनिर्भरता का नया सोपान"
    },
    "home_nav": {
        "en": "🏠 Home & Impact Hub",
        "hi": "🏠 मुख्य पृष्ठ एवं प्रभाव"
    },
    "citizen_nav": {
        "en": "👤 Citizen Portal (Request Pickup)",
        "hi": "👤 नागरिक पोर्टल (पिकअप अनुरोध)"
    },
    "shg_nav": {
        "en": "👩‍🦰 Women SHG Partner Portal",
        "hi": "👩‍🦰 महिला स्वयं सहायता समूह (SHG) पोर्टल"
    },
    "admin_nav": {
        "en": "🏛️ Municipal Admin Dashboard",
        "hi": "🏛️ नगर निगम एवं प्रशासनिक डैशबोर्ड"
    },
    "roadmap_nav": {
        "en": "🗺️ Pilot Roadmap & Compliance",
        "hi": "🗺️ आगामी योजना एवं नियम"
    },
    "doorstep_title": {
        "en": "Request Doorstep E-Waste Pickup",
        "hi": "घर बैठे ई-कचरा पिकअप का अनुरोध करें"
    },
    "doorstep_sub": {
        "en": "Safely discard obsolete electronics, prevent soil toxicity, and support local women micro-entrepreneurs in Meerut.",
        "hi": "पुराने इलेक्ट्रॉनिक्स का सुरक्षित निपटान करें, पर्यावरण को बचाएं और मेरठ की महिला उद्यमियों को सशक्त बनाएं।"
    },
    "your_name": {
        "en": "Your Full Name",
        "hi": "आपका पूरा नाम"
    },
    "phone_label": {
        "en": "10-Digit Mobile Number",
        "hi": "१० अंकों का मोबाइल नंबर"
    },
    "address_label": {
        "en": "Complete Street Address",
        "hi": "पूरा पता (मकान नंबर, गली/मोहल्ला)"
    },
    "ward_label": {
        "en": "Select Locality / Ward (Meerut)",
        "hi": "अपना इलाका / वार्ड चुनें (मेरठ)"
    },
    "category_label": {
        "en": "E-Waste Category",
        "hi": "ई-कचरे की श्रेणी"
    },
    "estimated_weight_label": {
        "en": "Estimated Weight (in kg)",
        "hi": "अनुमानित वजन (किलोग्राम में)"
    },
    "pickup_slot_label": {
        "en": "Preferred Pickup Slot",
        "hi": "सुविधाजनक पिकअप समय"
    },
    "submit_pickup": {
        "en": "Submit Pickup Request",
        "hi": "पिकअप अनुरोध दर्ज करें"
    },
    "track_title": {
        "en": "Track Your Pickup Request",
        "hi": "अपने अनुरोध की स्थिति देखें"
    },
    "enter_req_id": {
        "en": "Enter Request ID (e.g. EW-00001)",
        "hi": "अनुरोध संख्या दर्ज करें (जैसे EW-00001)"
    },
    "enter_phone_last4": {
        "en": "Enter Last 4 Digits of Mobile Number",
        "hi": "मोबाइल नंबर के अंतिम ४ अंक"
    },
    "safety_advisory_title": {
        "en": "⚠️ Crucial Safety & Data Advisory",
        "hi": "⚠️ सुरक्षा एवं डेटा गोपनीयता सलाह"
    },
    "safety_advisory_text": {
        "en": "Please factory-reset smartphones and computers before handing them over. Remove SIM cards and SD storage. Do not open, crush, or burn lithium batteries.",
        "hi": "कृपया सौंपने से पहले स्मार्टफोन व लैपटॉप को फ़ैक्टरी रीसेट करें और सिम/मेमोरी कार्ड निकालें। लिथियम बैटरी को कभी न खोलें और न जलाएं।"
    },
    "consent_text": {
        "en": "I consent to minimal address and contact sharing with verified local SHG collectors under India's Digital Personal Data Protection (DPDP) Act 2023 principles.",
        "hi": "मैं डिजिटल व्यक्तिगत डेटा संरक्षण (DPDP) अधिनियम 2023 के तहत केवल पिकअप हेतु न्यूनतम संपर्क साझा करने की सहमति देता/देती हूँ।"
    }
}


def t(key: str, lang: str = "en") -> str:
    """Helper to retrieve bilingual text string."""
    item = TRANSLATIONS.get(key, {})
    return item.get(lang, item.get("en", key))


# ==========================================
# 2. CUSTOM CSS INJECTION
# ==========================================

def inject_custom_css():
    """Injects high-polish responsive styling matching IEEE presentation theme."""
    custom_css = """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Primary Palette Definitions */
    :root {
        --color-indigo: #3B2F72;
        --color-pink: #E8318A;
        --color-green: #0D9488;
        --color-emerald: #10B981;
        --color-dark: #1E1B4B;
        --color-card-bg: #FFFFFF;
        --color-subtle-bg: #F8FAFC;
        --color-border: #E2E8F0;
    }

    /* Streamlit Metric Card Polish */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 12px rgba(59, 47, 114, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(59, 47, 114, 0.1);
        border-color: #CBD5E1;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #64748B !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        color: #1E1B4B !important;
    }

    /* Custom Header Hero */
    .hero-banner {
        background: linear-gradient(135deg, #3B2F72 0%, #2A1F56 60%, #1A1338 100%);
        color: white;
        padding: 32px 36px;
        border-radius: 16px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(232, 49, 138, 0.2);
        box-shadow: 0 10px 25px rgba(59, 47, 114, 0.2);
    }
    .hero-banner::after {
        content: "";
        position: absolute;
        top: -50%;
        right: -10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(232, 49, 138, 0.25) 0%, rgba(13, 148, 136, 0.15) 50%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        margin-bottom: 6px;
        background: linear-gradient(90deg, #FFFFFF 0%, #FCE7F3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-tagline {
        font-size: 1.05rem;
        color: #E2E8F0;
        font-weight: 400;
        margin-bottom: 14px;
    }
    .hero-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 12px;
    }
    .hero-badge {
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: #F8FAFC;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    /* Cards */
    .she-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
    }
    .she-card-highlight {
        border-left: 4px solid #E8318A;
    }
    .she-card-green {
        border-left: 4px solid #0D9488;
    }
    .she-card-indigo {
        border-left: 4px solid #3B2F72;
    }

    /* Status Pills */
    .status-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .status-requested { background-color: #FEF3C7; color: #92400E; border: 1px solid #FCD34D; }
    .status-assigned { background-color: #DBEAFE; color: #1E40AF; border: 1px solid #93C5FD; }
    .status-collected { background-color: #EDE9FE; color: #5B21B6; border: 1px solid #C4B5FD; }
    .status-sorted { background-color: #FCE7F3; color: #9D174D; border: 1px solid #F472B6; }
    .status-delivered { background-color: #CCFBF1; color: #115E59; border: 1px solid #5EEAD4; }
    .status-settled { background-color: #D1FAE5; color: #065F46; border: 1px solid #6EE7B7; }
    .status-pending { background-color: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; }
    .status-approved { background-color: #D1FAE5; color: #065F46; border: 1px solid #6EE7B7; }
    .status-rejected { background-color: #FEE2E2; color: #991B1B; border: 1px solid #FCA5A5; }

    /* Timeline Stepper */
    .timeline-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 24px 0 16px 0;
        position: relative;
    }
    .step-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        position: relative;
        z-index: 2;
        text-align: center;
        flex: 1;
    }
    .step-circle {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.85rem;
        margin-bottom: 8px;
        transition: all 0.3s ease;
    }
    .step-circle-done {
        background-color: #0D9488;
        color: white;
        box-shadow: 0 0 0 4px #CCFBF1;
    }
    .step-circle-current {
        background-color: #E8318A;
        color: white;
        box-shadow: 0 0 0 4px #FCE7F3;
        animation: pulse 2s infinite;
    }
    .step-circle-future {
        background-color: #E2E8F0;
        color: #94A3B8;
        border: 2px solid #CBD5E1;
    }
    .step-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #475569;
        max-width: 90px;
    }
    .step-label-active {
        color: #3B2F72;
        font-weight: 700;
    }

    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.08); }
        100% { transform: scale(1); }
    }

    /* Safety Box Alert */
    .safety-box {
        background: #FFFBEB;
        border: 1px solid #FCD34D;
        border-left: 5px solid #F59E0B;
        border-radius: 8px;
        padding: 14px 18px;
        color: #92400E;
        font-size: 0.9rem;
        margin: 14px 0;
    }

    /* Compliance Banner */
    .compliance-pill-box {
        background: #F1F5F9;
        border: 1px solid #CBD5E1;
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 0.82rem;
        color: #334155;
        margin-top: 10px;
    }

    /* Buttons */
    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.9rem;
        padding: 0.5rem 1.2rem;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #F8FAFC;
        border-right: 1px solid #E2E8F0;
    }

    /* Code & Mono */
    code {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85em;
        padding: 2px 6px;
        border-radius: 4px;
        background-color: #F1F5F9;
        color: #3B2F72;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


# ==========================================
# 3. VISUAL STATUS TIMELINE RENDERER
# ==========================================

def render_status_stepper(current_status: str):
    """Renders a polished 6-step visual progress bar for request lifecycle."""
    from services import STATUS_ORDER

    try:
        curr_idx = STATUS_ORDER.index(current_status)
    except ValueError:
        curr_idx = 0

    steps_html = ['<div class="timeline-container">']

    icons = ["📝", "🤝", "⚖️", "🔬", "🚛", "💰"]

    for i, status_name in enumerate(STATUS_ORDER):
        if i < curr_idx:
            circle_class = "step-circle step-circle-done"
            icon = "✓"
            label_class = "step-label"
        elif i == curr_idx:
            circle_class = "step-circle step-circle-current"
            icon = icons[i]
            label_class = "step-label step-label-active"
        else:
            circle_class = "step-circle step-circle-future"
            icon = str(i + 1)
            label_class = "step-label"

        short_name = status_name.replace("to Recycler", "Recycler")
        step_box = f"""
        <div class="step-item">
            <div class="{circle_class}">{icon}</div>
            <div class="{label_class}">{short_name}</div>
        </div>
        """
        steps_html.append(step_box)

    steps_html.append('</div>')
    st.markdown("".join(steps_html), unsafe_allow_html=True)


def get_status_badge_html(status: str) -> str:
    """Returns HTML for color-coded status badge."""
    mapping = {
        "Requested": ("status-requested", "Requested"),
        "Assigned": ("status-assigned", "Assigned"),
        "Collected": ("status-collected", "Collected"),
        "Sorted": ("status-sorted", "Sorted"),
        "Delivered to Recycler": ("status-delivered", "Delivered to Recycler"),
        "Settled": ("status-settled", "Settled"),
        "Approved": ("status-approved", "Approved"),
        "Pending Approval": ("status-pending", "Pending Approval"),
        "Rejected": ("status-rejected", "Rejected")
    }
    css_class, label = mapping.get(status, ("status-assigned", status))
    return f'<span class="status-pill {css_class}">{label}</span>'


# ==========================================
# 4. QR CODE GENERATOR
# ==========================================

def generate_qr_image(payload_text: str):
    """Generates a PIL QR code image with high error correction."""
    try:
        import qrcode
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=2,
        )
        qr.add_data(payload_text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#3B2F72", back_color="#FFFFFF")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf
    except Exception:
        return None
