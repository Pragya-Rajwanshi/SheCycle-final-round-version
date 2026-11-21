"""
ui_common.py - Common UI Components, Design System CSS, Bilingual Support & Helpers
Features:
- Theme Engine: Light and Dark mode palette injection with CSS variables
- render_html helper to eliminate raw HTML / 4-space markdown code-block bugs
- on_click callback helper go_to(page_name) for 1-click instantaneous portal switching
- Responsive 6-stage connecting-line status timeline stepper (horizontal desktop, vertical mobile)
- Unified render_page_header component
- Plotly theme generator
"""

import streamlit as st
import io
import textwrap
import re
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
    "help_nav": {
        "en": "❓ Help & Guide",
        "hi": "❓ सहायता एवं उपयोगकर्ता निर्देशिका"
    },
    "doorstep_title": {
        "en": "Request Doorstep E-Waste Pickup",
        "hi": "घर बैठे ई-कचरा पिकअप का अनुरोध करें"
    },
    "doorstep_sub": {
        "en": "Safely discard obsolete electronics, prevent toxic heavy metal leakage, and support local women micro-entrepreneurs in Meerut.",
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
# 2. RAW-HTML SAFETY HELPER (ISSUE 1 FIX)
# ==========================================

def render_html(html: str):
    """
    Renders raw HTML safely in Streamlit without triggering Markdown code block formatting.
    1. Dedents the string.
    2. Strips leading and trailing whitespace from every line.
    3. Drops completely empty lines.
    4. Joins into a single compact string without 4+ space line indentations.
    5. Calls st.markdown(compact, unsafe_allow_html=True).
    """
    if not html:
        return
    dedented = textwrap.dedent(html)
    lines = [line.strip() for line in dedented.splitlines() if line.strip()]
    compact = "".join(lines)
    st.markdown(compact, unsafe_allow_html=True)


# ==========================================
# 3. ON-CLICK NAVIGATION HELPER (ISSUE 2 FIX)
# ==========================================

def go_to(page_name: str):
    """
    Callback executed during button on_click.
    Updates st.session_state['main_nav_radio'] BEFORE the rerun so the sidebar radio
    and the main script immediately render the target page on the very first click.
    """
    st.session_state["main_nav_radio"] = page_name
    st.session_state["nav_page"] = page_name


# ==========================================
# 4. DESIGN SYSTEM CSS INJECTION (LIGHT/DARK)
# ==========================================

def inject_custom_css(dark_mode: bool = False):
    """Injects high-polish responsive styling matching IEEE presentation theme."""
    if dark_mode:
        vars_css = """
        :root {
            --bg: #0F0B1E;
            --surface: #1A1530;
            --surface-2: #2A2350;
            --surface-alt: #231C42;
            --border: #2E2750;
            --border-subtle: #3A3265;
            --text: #F1EEFA;
            --muted: #A9A3C4;
            --primary: #8B7CF6;
            --accent: #FF5FA8;
            --success: #34D399;
            --warning: #FBBF24;
            --error: #F87171;
            --info: #38BDF8;
            --code-bg: #2A2350;
            --code-text: #FFD3E8;
            --shadow: rgba(0, 0, 0, 0.45);
            --header-bg: #0F0B1E;
            --badge-req-bg: rgba(251, 191, 36, 0.2);
            --badge-req-txt: #FBBF24;
            --badge-req-brd: rgba(251, 191, 36, 0.5);
            --badge-asg-bg: rgba(96, 165, 250, 0.2);
            --badge-asg-txt: #60A5FA;
            --badge-asg-brd: rgba(96, 165, 250, 0.5);
            --badge-col-bg: rgba(167, 139, 250, 0.2);
            --badge-col-txt: #C084FC;
            --badge-col-brd: rgba(167, 139, 250, 0.5);
            --badge-srt-bg: rgba(244, 114, 182, 0.2);
            --badge-srt-txt: #F472B6;
            --badge-srt-brd: rgba(244, 114, 182, 0.5);
            --badge-del-bg: rgba(45, 212, 191, 0.2);
            --badge-del-txt: #2DD4BF;
            --badge-del-brd: rgba(45, 212, 191, 0.5);
            --badge-set-bg: rgba(52, 211, 153, 0.2);
            --badge-set-txt: #34D399;
            --badge-set-brd: rgba(52, 211, 153, 0.5);
        }
        """
    else:
        vars_css = """
        :root {
            --bg: #F7F5FC;
            --surface: #FFFFFF;
            --surface-2: #EFEBF8;
            --surface-alt: #F1EDFA;
            --border: #E6E1F5;
            --border-subtle: #D8D2EE;
            --text: #1E1B4B;
            --muted: #524B70;
            --primary: #3B2F72;
            --accent: #E8318A;
            --success: #1FA971;
            --warning: #D97706;
            --error: #DC2626;
            --info: #2563EB;
            --code-bg: #F1EDFB;
            --code-text: #3B2F72;
            --shadow: rgba(59, 47, 114, 0.05);
            --header-bg: #FFFFFF;
            --badge-req-bg: rgba(251, 191, 36, 0.15);
            --badge-req-txt: #D97706;
            --badge-req-brd: rgba(251, 191, 36, 0.4);
            --badge-asg-bg: rgba(59, 130, 246, 0.15);
            --badge-asg-txt: #2563EB;
            --badge-asg-brd: rgba(59, 130, 246, 0.4);
            --badge-col-bg: rgba(139, 92, 246, 0.15);
            --badge-col-txt: #7C3AED;
            --badge-col-brd: rgba(139, 92, 246, 0.4);
            --badge-srt-bg: rgba(236, 72, 153, 0.15);
            --badge-srt-txt: #DB2777;
            --badge-srt-brd: rgba(236, 72, 153, 0.4);
            --badge-del-bg: rgba(20, 184, 166, 0.15);
            --badge-del-txt: #0D9488;
            --badge-del-brd: rgba(20, 184, 166, 0.4);
            --badge-set-bg: rgba(31, 169, 113, 0.15);
            --badge-set-txt: #1FA971;
            --badge-set-brd: rgba(31, 169, 113, 0.4);
        }
        """

    custom_css = f"""
    <style>
    /* Google Fonts: Plus Jakarta Sans & Inter */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

    {vars_css}

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text);
        background-color: var(--bg);
        -webkit-font-smoothing: antialiased;
    }}

    .stApp {{
        background-color: var(--bg) !important;
        color: var(--text) !important;
    }}

    /* Top Streamlit Header, Toolbar, Decoration & Header Controls */
    header[data-testid="stHeader"],
    .stApp > header {{
        background-color: var(--header-bg) !important;
        background: var(--header-bg) !important;
        border-bottom: 1px solid var(--border) !important;
    }}

    [data-testid="stToolbar"] {{
        background-color: transparent !important;
        color: var(--text) !important;
    }}

    [data-testid="stDecoration"] {{
        background: linear-gradient(90deg, var(--primary), var(--accent)) !important;
        height: 3px !important;
    }}

    header[data-testid="stHeader"] button,
    header[data-testid="stHeader"] button svg,
    [data-testid="stToolbar"] button,
    [data-testid="stToolbar"] svg,
    [data-testid="stHeaderActionElements"] button,
    [data-testid="stHeaderActionElements"] button svg,
    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="stSidebarCollapseButton"] svg,
    [data-testid="collapsedControl"] button,
    [data-testid="collapsedControl"] svg {{
        color: var(--text) !important;
        fill: var(--text) !important;
    }}

    [data-testid="stHeaderActionElements"] button {{
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }}

    [data-testid="stHeaderActionElements"] button:hover {{
        background-color: var(--surface-2) !important;
        border-color: var(--accent) !important;
        color: var(--accent) !important;
    }}

    /* Max Content Width Container */
    .block-container {{
        max-width: 1180px !important;
        padding-top: 1.8rem !important;
        padding-bottom: 3.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }}

    /* Page Fade-in Animation */
    .main .block-container {{
        animation: fadeIn 0.35s ease-in-out;
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(6px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Standardized Unified Page Header */
    .she-page-header {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 22px 28px;
        margin-bottom: 24px;
        box-shadow: 0 4px 16px var(--shadow);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }}
    .she-page-header-left {{
        display: flex;
        align-items: center;
        gap: 16px;
    }}
    .she-page-header-icon {{
        font-size: 2.2rem;
        background: var(--surface-alt);
        border: 1px solid var(--border);
        border-radius: 14px;
        width: 54px;
        height: 54px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 8px var(--shadow);
    }}
    .she-page-header-title {{
        margin: 0;
        font-size: 1.55rem;
        font-weight: 800;
        color: var(--primary);
        letter-spacing: -0.02em;
    }}
    .she-page-header-sub {{
        margin: 3px 0 0 0;
        font-size: 0.9rem;
        color: var(--muted);
        line-height: 1.45;
    }}

    /* Streamlit Metric Card Polish */
    div[data-testid="stMetric"] {{
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 16px !important;
        padding: 18px 22px !important;
        box-shadow: 0 4px 16px var(--shadow) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }}
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 24px var(--shadow) !important;
        border-color: var(--accent) !important;
    }}
    div[data-testid="stMetricLabel"] p {{
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        color: var(--muted) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.6px !important;
    }}
    div[data-testid="stMetricValue"] {{
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        color: var(--text) !important;
        letter-spacing: -0.02em !important;
    }}
    div[data-testid="stMetricDelta"] svg {{
        fill: currentColor !important;
    }}

    /* Hero Banner for Home Page */
    .hero-banner {{
        background: linear-gradient(135deg, #3B2F72 0%, #2A1F56 50%, #150F2C 100%);
        color: white;
        padding: 38px 42px;
        border-radius: 20px;
        margin-bottom: 26px;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(232, 49, 138, 0.25);
        box-shadow: 0 12px 30px rgba(59, 47, 114, 0.22);
    }}
    .hero-banner::after {{
        content: "";
        position: absolute;
        top: -60%;
        right: -8%;
        width: 380px;
        height: 380px;
        background: radial-gradient(circle, rgba(232, 49, 138, 0.22) 0%, rgba(31, 169, 113, 0.15) 50%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }}
    .hero-title {{
        font-size: 2.35rem;
        font-weight: 800;
        margin-bottom: 8px;
        letter-spacing: -0.025em;
        background: linear-gradient(90deg, #FFFFFF 0%, #FCE7F3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .hero-tagline {{
        font-size: 1.15rem;
        color: #F1EDFA;
        font-weight: 500;
        margin-bottom: 14px;
        letter-spacing: -0.01em;
    }}
    .hero-badges {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 14px;
    }}
    .hero-badge {{
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.22);
        color: #F8FAFC;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        backdrop-filter: blur(4px);
    }}

    /* Card Containers & Grids */
    .she-card {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 22px 26px;
        margin-bottom: 18px;
        box-shadow: 0 4px 16px var(--shadow);
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        overflow-wrap: anywhere;
        word-break: break-word;
        color: var(--text);
    }}
    .she-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 24px var(--shadow);
        border-color: var(--accent);
    }}
    .she-card-highlight {{
        border-left: 5px solid var(--accent);
    }}
    .she-card-green {{
        border-left: 5px solid var(--success);
    }}
    .she-card-indigo {{
        border-left: 5px solid var(--primary);
    }}

    /* Equal-Height Card Grids */
    .she-card-grid-4 {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
        align-items: stretch;
    }}
    @media (max-width: 1024px) {{
        .she-card-grid-4 {{
            grid-template-columns: repeat(2, 1fr);
        }}
    }}
    @media (max-width: 600px) {{
        .she-card-grid-4 {{
            grid-template-columns: 1fr;
        }}
    }}

    .she-card-grid-3 {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 18px;
        margin-bottom: 24px;
        align-items: stretch;
    }}
    @media (max-width: 800px) {{
        .she-card-grid-3 {{
            grid-template-columns: 1fr;
        }}
    }}

    .she-grid-card {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 22px 20px;
        display: flex;
        flex-direction: column;
        height: 100%;
        min-height: 215px;
        box-sizing: border-box;
        overflow-wrap: anywhere;
        word-break: break-word;
        box-shadow: 0 4px 16px var(--shadow);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        color: var(--text);
    }}
    .she-grid-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 24px var(--shadow);
        border-color: var(--accent);
    }}
    .she-card-title {{
        min-height: 2.6rem;
        display: flex;
        align-items: center;
        font-size: 1.05rem;
        font-weight: 700;
        margin: 8px 0 6px 0;
        line-height: 1.3;
        color: var(--text);
    }}
    .she-card-body {{
        font-size: 0.88rem;
        color: var(--muted) !important;
        line-height: 1.45;
        flex-grow: 1;
        margin: 0;
    }}

    /* Card Headings & Content Typography */
    .she-card h4, .she-grid-card h4 {{
        margin: 8px 0 6px 0;
        font-weight: 700;
    }}
    .she-card-green h4 {{ color: var(--success) !important; }}
    .she-card-highlight h4 {{ color: var(--accent) !important; }}
    .she-card-indigo h4 {{ color: var(--primary) !important; }}

    .she-card p, .she-grid-card p {{
        color: var(--muted) !important;
    }}
    .she-card strong, .she-grid-card strong {{
        color: var(--text) !important;
    }}
    .she-card li, .she-grid-card li {{
        color: var(--text) !important;
    }}

    /* Status Pills with High Contrast in Both Modes */
    .status-pill {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.76rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        line-height: 1.2;
    }}
    .status-requested {{ background-color: var(--badge-req-bg) !important; color: var(--badge-req-txt) !important; border: 1px solid var(--badge-req-brd) !important; }}
    .status-assigned {{ background-color: var(--badge-asg-bg) !important; color: var(--badge-asg-txt) !important; border: 1px solid var(--badge-asg-brd) !important; }}
    .status-collected {{ background-color: var(--badge-col-bg) !important; color: var(--badge-col-txt) !important; border: 1px solid var(--badge-col-brd) !important; }}
    .status-sorted {{ background-color: var(--badge-srt-bg) !important; color: var(--badge-srt-txt) !important; border: 1px solid var(--badge-srt-brd) !important; }}
    .status-delivered {{ background-color: var(--badge-del-bg) !important; color: var(--badge-del-txt) !important; border: 1px solid var(--badge-del-brd) !important; }}
    .status-settled {{ background-color: var(--badge-set-bg) !important; color: var(--badge-set-txt) !important; border: 1px solid var(--badge-set-brd) !important; }}
    .status-pending {{ background-color: var(--badge-req-bg) !important; color: var(--badge-req-txt) !important; border: 1px solid var(--badge-req-brd) !important; }}
    .status-approved {{ background-color: var(--badge-set-bg) !important; color: var(--badge-set-txt) !important; border: 1px solid var(--badge-set-brd) !important; }}
    .status-rejected {{ background-color: rgba(239, 68, 68, 0.2) !important; color: var(--error) !important; border: 1px solid rgba(239, 68, 68, 0.5) !important; }}

    /* Responsive 6-Stage Horizontal Stepper with Connecting Lines */
    .timeline-stepper {{
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        width: 100%;
        margin: 24px 0 18px 0;
        position: relative;
    }}
    .timeline-step {{
        display: flex;
        flex-direction: column;
        align-items: center;
        position: relative;
        flex: 1;
        text-align: center;
    }}
    .timeline-step:not(:last-child)::after {{
        content: "";
        position: absolute;
        top: 19px;
        left: 50%;
        width: 100%;
        height: 3px;
        background-color: var(--border);
        z-index: 1;
    }}
    .timeline-step.completed:not(:last-child)::after {{
        background-color: var(--success);
    }}
    .timeline-step .step-circle {{
        width: 38px;
        height: 38px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.88rem;
        margin-bottom: 8px;
        position: relative;
        z-index: 2;
        background-color: var(--surface);
        border: 2px solid var(--border);
        color: var(--muted);
        transition: all 0.25s ease;
    }}
    .timeline-step.completed .step-circle {{
        background-color: var(--success) !important;
        border-color: var(--success) !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 0 3px rgba(31, 169, 113, 0.25);
    }}
    .timeline-step.current .step-circle {{
        background-color: var(--accent) !important;
        border-color: var(--accent) !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 0 4px rgba(232, 49, 138, 0.25);
        animation: pulse-ring 2s infinite;
    }}
    .timeline-step .step-label {{
        font-size: 0.76rem;
        font-weight: 600;
        color: var(--muted);
        max-width: 95px;
        line-height: 1.25;
        margin-top: 2px;
    }}
    .timeline-step.current .step-label {{
        color: var(--accent) !important;
        font-weight: 800;
    }}
    .timeline-step.completed .step-label {{
        color: var(--text) !important;
        font-weight: 700;
    }}
    @media (max-width: 640px) {{
        .timeline-stepper {{
            flex-direction: column;
            align-items: flex-start;
            padding-left: 12px;
            gap: 14px;
        }}
        .timeline-step {{
            flex-direction: row;
            align-items: center;
            gap: 14px;
            width: 100%;
            text-align: left;
        }}
        .timeline-step:not(:last-child)::after {{
            top: 38px;
            left: 18px;
            width: 3px;
            height: 100%;
        }}
        .timeline-step .step-label {{
            max-width: none;
            font-size: 0.85rem;
        }}
    }}

    @keyframes pulse-ring {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.08); }}
        100% {{ transform: scale(1); }}
    }}

    /* Safety & Compliance Box */
    .safety-box {{
        background: rgba(245, 158, 11, 0.12) !important;
        border: 1px solid rgba(245, 158, 11, 0.4) !important;
        border-left: 5px solid var(--warning) !important;
        border-radius: 12px;
        padding: 15px 20px;
        color: var(--text) !important;
        font-size: 0.9rem;
        margin: 16px 0;
        line-height: 1.45;
    }}
    .safety-box strong {{
        color: var(--text) !important;
    }}

    .compliance-pill-box {{
        background: var(--surface-alt);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 10px 14px;
        font-size: 0.82rem;
        color: var(--text);
        margin-top: 10px;
    }}

    /* Buttons: Indigo to Pink Gradient for Primary Buttons */
    div.stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, var(--primary) 0%, #683074 50%, var(--accent) 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.55rem 1.4rem !important;
        box-shadow: 0 4px 14px rgba(232, 49, 138, 0.25) !important;
        transition: all 0.2s ease !important;
    }}
    div.stButton > button[kind="primary"]:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(232, 49, 138, 0.35) !important;
        color: #FFFFFF !important;
    }}

    /* Secondary Buttons */
    div.stButton > button:not([kind="primary"]) {{
        border-radius: 10px !important;
        font-weight: 600 !important;
        border: 1px solid var(--border) !important;
        background-color: var(--surface) !important;
        color: var(--text) !important;
        transition: all 0.2s ease !important;
    }}
    div.stButton > button:not([kind="primary"]):hover {{
        transform: translateY(-1px) !important;
        border-color: var(--accent) !important;
        color: var(--accent) !important;
        background-color: var(--surface-2) !important;
        box-shadow: 0 4px 12px var(--shadow) !important;
    }}

    div.stButton > button:disabled {{
        opacity: 0.5 !important;
        cursor: not-allowed !important;
        border-color: var(--border) !important;
        background-color: var(--surface-2) !important;
        color: var(--muted) !important;
    }}

    /* Form Inputs Focus Ring & Heights */
    div[data-baseweb="input"] {{
        border-radius: 10px !important;
        border: 1px solid var(--border) !important;
        background-color: var(--surface) !important;
    }}
    div[data-baseweb="input"] input {{
        color: var(--text) !important;
        background-color: transparent !important;
    }}
    div[data-baseweb="input"]:focus-within {{
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(232, 49, 138, 0.2) !important;
    }}

    div[data-baseweb="textarea"] {{
        border-radius: 10px !important;
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
    }}
    div[data-baseweb="textarea"] textarea {{
        color: var(--text) !important;
        background-color: transparent !important;
    }}
    div[data-baseweb="textarea"]:focus-within {{
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(232, 49, 138, 0.2) !important;
    }}

    div[data-baseweb="select"] > div {{
        border-radius: 10px !important;
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
    }}
    div[data-baseweb="select"] span {{
        color: var(--text) !important;
    }}
    div[data-baseweb="select"] svg {{
        fill: var(--text) !important;
    }}

    /* Dropdown popover list & options */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    div[data-baseweb="menu"],
    ul[role="listbox"] {{
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        box-shadow: 0 8px 24px var(--shadow) !important;
    }}
    li[role="option"] {{
        background-color: var(--surface) !important;
        color: var(--text) !important;
    }}
    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {{
        background-color: var(--surface-2) !important;
        color: var(--accent) !important;
    }}

    /* Multiselect tag chips */
    div[data-baseweb="tag"] {{
        background-color: var(--surface-2) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
    }}
    div[data-baseweb="tag"] span {{
        color: var(--text) !important;
    }}
    div[data-baseweb="tag"] svg {{
        fill: var(--text) !important;
    }}

    /* Input placeholders */
    input::placeholder,
    textarea::placeholder {{
        color: var(--muted) !important;
        opacity: 0.85 !important;
    }}

    /* Tabs Styling */
    div[data-baseweb="tab-list"] {{
        gap: 8px;
        border-bottom: 2px solid var(--border) !important;
        margin-bottom: 20px;
        background-color: transparent !important;
    }}
    button[data-baseweb="tab"] {{
        border-radius: 8px 8px 0 0 !important;
        font-weight: 600 !important;
        color: var(--muted) !important;
        background-color: transparent !important;
        padding: 10px 18px !important;
        border: none !important;
        transition: color 0.2s ease, border-color 0.2s ease !important;
    }}
    button[data-baseweb="tab"]:hover {{
        color: var(--text) !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: var(--primary) !important;
        font-weight: 700 !important;
        border-bottom: 3px solid var(--accent) !important;
    }}

    /* Radio Options & Circles */
    div[data-testid="stRadio"] label {{
        color: var(--text) !important;
        cursor: pointer !important;
    }}
    div[data-testid="stRadio"] label span,
    div[data-testid="stRadio"] label p {{
        color: var(--text) !important;
    }}
    /* Outer radio circle */
    div[data-testid="stRadio"] div[role="radiogroup"] label > div:first-child {{
        background-color: var(--surface) !important;
        border: 2px solid var(--muted) !important;
        transition: all 0.2s ease !important;
    }}
    div[data-testid="stRadio"] div[role="radiogroup"] label:hover > div:first-child {{
        border-color: var(--accent) !important;
    }}
    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) > div:first-child {{
        border-color: var(--accent) !important;
    }}
    /* Inner dot when radio is selected */
    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) > div:first-child > div,
    div[data-testid="stRadio"] div[role="radiogroup"] input:checked + div > div {{
        background-color: var(--accent) !important;
    }}

    /* Toggle Switch */
    div[data-testid="stToggle"] label {{
        color: var(--text) !important;
    }}
    div[data-testid="stToggle"] label span,
    div[data-testid="stToggle"] label p {{
        color: var(--text) !important;
        font-weight: 600 !important;
    }}
    div[data-testid="stToggle"] label > div:first-child {{
        background-color: var(--surface-2) !important;
        border: 1px solid var(--border) !important;
    }}
    div[data-testid="stToggle"] label:has(input:checked) > div:first-child {{
        background-color: var(--accent) !important;
        border-color: var(--accent) !important;
    }}
    div[data-testid="stToggle"] label div:first-child > div {{
        background-color: #FFFFFF !important;
    }}

    /* Sidebar Container Styling */
    section[data-testid="stSidebar"] {{
        background-color: var(--surface) !important;
        border-right: 1px solid var(--border) !important;
    }}
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] h5,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] span {{
        color: var(--text);
    }}
    section[data-testid="stSidebar"] hr {{
        border-color: var(--border) !important;
    }}

    /* Hyperlinks */
    a,
    section[data-testid="stSidebar"] a {{
        color: var(--primary) !important;
        text-decoration: none !important;
        transition: color 0.15s ease !important;
    }}
    a:hover,
    section[data-testid="stSidebar"] a:hover {{
        color: var(--accent) !important;
        text-decoration: underline !important;
    }}

    /* Streamlit Captions */
    div[data-testid="stCaptionContainer"] p,
    .stCaption,
    small {{
        color: var(--muted) !important;
        font-size: 0.85rem !important;
    }}

    /* Tooltip Icons & Miscellaneous SVGs */
    div[data-testid="stTooltipIcon"] svg {{
        color: var(--muted) !important;
        fill: var(--muted) !important;
    }}
    div[data-testid="stTooltipIcon"]:hover svg {{
        color: var(--accent) !important;
        fill: var(--accent) !important;
    }}

    /* Tooltip Popover Container */
    div[data-baseweb="tooltip"],
    div[data-testid="stTooltipContent"] {{
        background-color: var(--surface-2) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 16px var(--shadow) !important;
    }}

    /* Streamlit Alert Callouts (Info, Success, Warning, Error) */
    div[data-testid="stAlert"] {{
        border-radius: 12px !important;
        border: 1px solid var(--border) !important;
        background-color: var(--surface) !important;
        box-shadow: 0 2px 8px var(--shadow) !important;
    }}
    div[data-testid="stAlert"] p,
    div[data-testid="stAlert"] span,
    div[data-testid="stAlert"] strong,
    div[data-testid="stAlert"] div {{
        color: var(--text) !important;
    }}

    /* File Uploader */
    div[data-testid="stFileUploader"] {{
        background-color: var(--surface) !important;
        border: 1px dashed var(--border) !important;
        border-radius: 12px !important;
        padding: 12px !important;
    }}
    div[data-testid="stFileUploader"] section {{
        background-color: var(--surface-2) !important;
        border: none !important;
        border-radius: 8px !important;
    }}
    div[data-testid="stFileUploader"] span,
    div[data-testid="stFileUploader"] small,
    div[data-testid="stFileUploader"] p {{
        color: var(--muted) !important;
    }}
    div[data-testid="stFileUploader"] button {{
        background-color: var(--surface) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
    }}
    div[data-testid="stFileUploader"] button:hover {{
        background-color: var(--surface-2) !important;
        border-color: var(--accent) !important;
        color: var(--accent) !important;
    }}

    /* Inline Code and Code Chips (Bug 2 Fix) */
    code,
    pre,
    .stMarkdown code,
    div[data-testid="stMarkdownContainer"] code,
    [data-testid="stCode"],
    .she-code,
    section[data-testid="stSidebar"] code,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] code {{
        font-family: 'JetBrains Mono', 'Fira Code', Consolas, monospace !important;
        font-size: 0.88em !important;
        padding: 2px 6px !important;
        border-radius: 6px !important;
        background-color: var(--code-bg) !important;
        color: var(--code-text) !important;
        border: 1px solid var(--border) !important;
        box-shadow: none !important;
    }}

    /* Code Blocks */
    [data-testid="stCodeBlock"] pre,
    [data-testid="stCodeBlock"] {{
        background-color: var(--code-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
    }}
    [data-testid="stCodeBlock"] code {{
        background-color: transparent !important;
        border: none !important;
        color: var(--code-text) !important;
    }}
    [data-testid="stCodeBlock"] button {{
        background-color: var(--surface) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
    }}
    [data-testid="stCodeBlock"] button svg {{
        fill: var(--text) !important;
    }}

    /* Streamlit Expanders (Bug 1 Fix - Judge Demo Mode & FAQ) */
    div[data-testid="stExpander"] {{
        background: var(--surface) !important;
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 2px 8px var(--shadow) !important;
        overflow: hidden !important;
    }}

    div[data-testid="stExpander"] details {{
        background: var(--surface) !important;
        background-color: var(--surface) !important;
        border: none !important;
        border-radius: 12px !important;
    }}

    div[data-testid="stExpander"] summary {{
        background-color: var(--surface) !important;
        color: var(--text) !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        border: none !important;
        transition: background-color 0.2s ease, color 0.2s ease !important;
    }}

    div[data-testid="stExpander"] summary:hover {{
        background-color: var(--surface-2) !important;
        color: var(--accent) !important;
    }}

    div[data-testid="stExpander"] details[open] summary {{
        border-bottom: 1px solid var(--border) !important;
        border-bottom-left-radius: 0 !important;
        border-bottom-right-radius: 0 !important;
    }}

    div[data-testid="stExpander"] summary span,
    div[data-testid="stExpander"] summary p,
    div[data-testid="stExpander"] summary strong {{
        color: var(--text) !important;
    }}

    div[data-testid="stExpander"] summary:hover span,
    div[data-testid="stExpander"] summary:hover p,
    div[data-testid="stExpander"] summary:hover strong {{
        color: var(--accent) !important;
    }}

    div[data-testid="stExpander"] summary svg {{
        fill: var(--text) !important;
        color: var(--text) !important;
    }}

    div[data-testid="stExpander"] summary:hover svg {{
        fill: var(--accent) !important;
        color: var(--accent) !important;
    }}

    div[data-testid="stExpander"] [data-testid="stExpanderDetails"] {{
        background-color: var(--surface) !important;
        color: var(--text) !important;
        padding: 14px 16px !important;
    }}

    div[data-testid="stExpander"] [data-testid="stExpanderDetails"] * {{
        color: var(--text);
    }}

    /* Dataframe container */
    div[data-testid="stDataFrame"] {{
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        background-color: var(--surface) !important;
    }}

    /* Clean Footer */
    .she-footer {{
        margin-top: 48px;
        padding-top: 24px;
        border-top: 1px solid var(--border);
        text-align: center;
        color: var(--muted);
        font-size: 0.85rem;
        line-height: 1.6;
    }}
    .she-footer strong {{
        color: var(--text);
    }}
    </style>
    """
    render_html(custom_css)


# ==========================================
# 5. UNIFIED PAGE HEADER HELPER
# ==========================================

def render_page_header(icon: str, title: str, subtitle: str, badge: Optional[str] = None):
    """Renders a standardized, ultra-clean page header with consistent typography."""
    badge_markup = f'<span class="hero-badge" style="background:var(--surface-alt); color:var(--text); border:1px solid var(--border);">{badge}</span>' if badge else ''
    html = f"""
    <div class="she-page-header">
        <div class="she-page-header-left">
            <div class="she-page-header-icon">{icon}</div>
            <div>
                <h2 class="she-page-header-title">{title}</h2>
                <p class="she-page-header-sub">{subtitle}</p>
            </div>
        </div>
        <div>{badge_markup}</div>
    </div>
    """
    render_html(html)


# ==========================================
# 6. VISUAL STATUS TIMELINE RENDERER (ISSUE 1 FIX)
# ==========================================

def render_status_stepper(current_status: str, lang: str = "en"):
    """
    Renders a 6-step visual progress bar with connecting lines between circles.
    Completed steps: Green circle with check mark ✓ and green connecting line.
    Current step: Highlighted pink with pulse animation.
    Future steps: Muted border with step number.
    On mobile: Stacks cleanly into a vertical progress track.
    Renders via render_html() to eliminate raw Markdown code block leaks.
    """
    from services import STATUS_ORDER

    try:
        curr_idx = STATUS_ORDER.index(current_status)
    except ValueError:
        curr_idx = 0

    labels_en = ["Requested", "Assigned", "Collected", "Sorted", "Delivered to Recycler", "Settled"]
    labels_hi = ["अनुरोध दर्ज", "समूह आवंटित", "घर से एकत्र", "प्राथमिक छंटाई", "रीसाइक्लर सुपुर्द", "भुगतान संपन्न"]
    labels = labels_hi if lang == "hi" else labels_en

    icons = ["📝", "🤝", "⚖️", "🔬", "🚛", "💰"]

    html_parts = ['<div class="timeline-stepper">']
    for i, status_name in enumerate(STATUS_ORDER):
        if i < curr_idx:
            cls = "timeline-step completed"
            icon_content = "✓"
        elif i == curr_idx:
            cls = "timeline-step current"
            icon_content = icons[i]
        else:
            cls = "timeline-step future"
            icon_content = str(i + 1)

        label_text = labels[i]
        step_html = f'<div class="{cls}"><div class="step-circle">{icon_content}</div><div class="step-label">{label_text}</div></div>'
        html_parts.append(step_html)

    html_parts.append('</div>')
    render_html("".join(html_parts))


def get_status_badge_html(status: str) -> str:
    """Returns compact HTML for color-coded status badge with high WCAG AA contrast in both themes."""
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
# 7. THEME-AWARE PLOTLY HELPER (ISSUE 4 FIX)
# ==========================================

def get_plotly_theme(is_dark: bool = False) -> Dict[str, Any]:
    """Returns theme-harmonized colors and transparent backgrounds for Plotly charts."""
    if is_dark:
        return {
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "font_color": "#F1EEFA",
            "grid_color": "#2E2750",
            "colors": ["#8B7CF6", "#FF5FA8", "#34D399", "#FBBF24", "#A78BFA", "#38BDF8"]
        }
    else:
        return {
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "font_color": "#1E1B4B",
            "grid_color": "#E6E1F5",
            "colors": ["#3B2F72", "#E8318A", "#1FA971", "#F59E0B", "#683074", "#0D9488"]
        }


# ==========================================
# 8. QR CODE GENERATOR
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
