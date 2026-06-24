"""
TradeProof
Blockchain traceability for South African supply chains.
Johannesburg, South Africa
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from branding import LOGO_SIDEBAR_SRC

st.set_page_config(
    page_title="TradeProof",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS — White / Peach / Green design system ────────────────────────
st.markdown("""
<style>
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  font-size: 14px;
  color: #20302A;
  background: #FAFBF9;
}

/* ══ SIDEBAR ══════════════════════════════════════ */
[data-testid="stSidebar"] {
  background: #34383C !important;
  border-right: none !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }

.sb-logo {
  background: #FFFFFF;
  margin: 18px 16px 8px;
  border-radius: 14px;
  padding: 16px 12px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.12);
}
.sb-logo img { width: 100%; max-width: 200px; }

.sb-tagline {
  text-align: center;
  font-size: 10.5px;
  color: rgba(255,255,255,0.55);
  letter-spacing: 0.5px;
  padding: 0 24px 18px;
  line-height: 1.6;
}

/* Nav radio */
[data-testid="stSidebar"] .stRadio > label { display: none !important; }
[data-testid="stSidebar"] .stRadio > div { gap: 2px !important; padding: 0 12px; }
[data-testid="stSidebar"] .stRadio > div > label {
  display: flex !important;
  align-items: center !important;
  padding: 11px 14px !important;
  border-radius: 9px !important;
  font-size: 13.5px !important;
  font-weight: 500 !important;
  color: rgba(255,255,255,0.78) !important;
  background: transparent !important;
  border: none !important;
  cursor: pointer !important;
  transition: all 0.15s !important;
}
[data-testid="stSidebar"] .stRadio > div > label:hover {
  background: rgba(255,255,255,0.08) !important;
  color: #fff !important;
}
[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {
  background: #F07A5A !important;
  color: #fff !important;
  font-weight: 600 !important;
  box-shadow: 0 2px 8px rgba(240,122,90,0.35) !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div { color: rgba(255,255,255,0.6) !important; }

.sb-footer {
  position: fixed; bottom: 0; left: 0; width: 21rem;
  padding: 14px 24px;
  background: rgba(0,0,0,0.15);
  border-top: 1px solid rgba(255,255,255,0.08);
  font-size: 11px; line-height: 1.9;
}
.status-dot {
  display: inline-block; width: 7px; height: 7px;
  border-radius: 50%; background: #6FCF97;
  margin-right: 5px; vertical-align: middle;
}

/* ══ MAIN CONTENT ═════════════════════════════════ */
.main .block-container {
  padding: 28px 36px 60px !important;
  max-width: 1180px !important;
}

/* Page header */
.page-header {
  display: flex; align-items: center; gap: 16px;
  padding: 18px 24px;
  background: #FFFFFF;
  border: 1px solid #E6EEE9;
  border-radius: 14px;
  margin-bottom: 22px;
  box-shadow: 0 1px 3px rgba(27,94,53,0.05);
}
.page-header-icon { width: 46px; height: auto; flex-shrink: 0; }
.page-header h2 { font-size: 19px; font-weight: 700; color: #20302A; margin: 0 0 2px; }
.page-header p  { font-size: 12.5px; color: #7C8B80; margin: 0; }

/* Section heading */
.sec-head {
  font-size: 12.5px; font-weight: 700;
  color: #1B5E35; text-transform: uppercase;
  letter-spacing: 1px;
  padding: 22px 0 10px;
  border-bottom: 1px solid #E6EEE9;
  margin-bottom: 14px;
}

/* ══ METRICS ══════════════════════════════════════ */
[data-testid="metric-container"] {
  background: #FFFFFF !important;
  border: 1px solid #E6EEE9 !important;
  border-radius: 12px !important;
  padding: 16px 18px 12px !important;
  box-shadow: 0 1px 3px rgba(27,94,53,0.04) !important;
}
[data-testid="stMetricValue"] {
  font-size: 25px !important; font-weight: 700 !important; color: #1B5E35 !important;
}
[data-testid="stMetricLabel"] {
  font-size: 11px !important; color: #7C8B80 !important;
  font-weight: 600 !important; text-transform: uppercase !important;
  letter-spacing: 0.5px !important;
}
[data-testid="stMetricDelta"] { font-size: 11px !important; }

/* ══ BUTTONS ══════════════════════════════════════ */
.stButton > button {
  background: #1B5E35 !important;
  color: #fff !important;
  border: none !important;
  border-radius: 9px !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  padding: 9px 22px !important;
  transition: background 0.15s, transform 0.1s !important;
  box-shadow: 0 1px 3px rgba(27,94,53,0.25) !important;
}
.stButton > button:hover { background: #154d2b !important; }
.stButton > button:active { transform: scale(0.98); }

.stDownloadButton > button {
  background: #FFFFFF !important;
  color: #1B5E35 !important;
  border: 1.5px solid #1B5E35 !important;
  border-radius: 9px !important;
  font-weight: 600 !important;
  font-size: 13px !important;
  box-shadow: none !important;
}
.stDownloadButton > button:hover {
  background: #E7F3EC !important;
}

/* ══ INPUTS ═══════════════════════════════════════ */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
textarea {
  border: 1.5px solid #E6EEE9 !important;
  border-radius: 9px !important;
  font-size: 13px !important;
  background: #fff !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
  border-color: #1B5E35 !important;
  box-shadow: 0 0 0 3px rgba(27,94,53,0.08) !important;
}
[data-testid="stSelectbox"] > div > div,
[data-testid="stDateInput"] > div > div {
  border: 1.5px solid #E6EEE9 !important;
  border-radius: 9px !important;
  font-size: 13px !important;
}
label { color: #3A4E40 !important; font-size: 13px !important; font-weight: 500 !important; }

/* ══ EXPANDER ═════════════════════════════════════ */
[data-testid="stExpander"] {
  background: #FFFFFF !important;
  border: 1px solid #E6EEE9 !important;
  border-radius: 12px !important;
  margin-bottom: 8px !important;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
}
[data-testid="stExpander"] summary {
  font-weight: 600 !important; color: #20302A !important;
  padding: 14px 18px !important; font-size: 13.5px !important;
}
[data-testid="stExpander"] summary:hover { color: #1B5E35 !important; }

/* ══ TABS ══════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
  gap: 4px !important; border-bottom: 2px solid #E6EEE9 !important;
  background: transparent !important;
}
.stTabs [data-baseweb="tab"] {
  font-size: 13px !important; font-weight: 600 !important; color: #7C8B80 !important;
  padding: 9px 20px !important; border-radius: 8px 8px 0 0 !important;
  background: transparent !important; border: none !important;
}
.stTabs [aria-selected="true"] {
  color: #1B5E35 !important; background: #E7F3EC !important;
  border-bottom: 2px solid #1B5E35 !important;
}

/* ══ PILL TOGGLE (radio displayed horizontally) ═══ */
div[data-testid="stHorizontalBlock"] .stRadio > div {
  flex-direction: row !important; gap: 6px !important;
}
.stRadio > div > label {
  border: 1.5px solid #E6EEE9 !important;
  border-radius: 20px !important;
  padding: 6px 16px !important;
  font-size: 12.5px !important;
  font-weight: 600 !important;
  color: #7C8B80 !important;
  background: #fff !important;
  cursor: pointer !important;
  transition: all 0.15s !important;
}
.stRadio > div > label:hover { border-color: #1B5E35 !important; }
.stRadio > div > label[data-checked="true"] {
  background: #1B5E35 !important;
  border-color: #1B5E35 !important;
  color: #fff !important;
}

/* ══ MISC ═════════════════════════════════════════ */
hr { border: none !important; border-top: 1px solid #E6EEE9 !important; margin: 18px 0 !important; }
[data-testid="stAlert"] { border-radius: 10px !important; font-size: 13px !important; }

/* Cards */
.tp-card {
  background: #FFFFFF;
  border: 1px solid #E6EEE9;
  border-radius: 12px;
  padding: 18px 20px;
  margin-bottom: 10px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
  transition: box-shadow 0.15s, border-color 0.15s;
}
.tp-card:hover { box-shadow: 0 4px 14px rgba(27,94,53,0.08); border-color: #CFE6D8; }
.tp-card-title { font-size: 14.5px; font-weight: 700; color: #20302A; margin-bottom: 4px; }
.tp-card-sub   { font-size: 12px; color: #7C8B80; line-height: 1.65; }

/* Hash pill */
.hash-pill {
  font-family: "Courier New", monospace; font-size: 10px;
  background: #E7F3EC; color: #1B5E35;
  padding: 3px 9px; border-radius: 5px;
  border: 1px solid #CFE6D8;
  display: inline-block; word-break: break-all;
}

/* Badges */
.badge { display:inline-block; padding:3px 11px; border-radius:20px; font-size:11px; font-weight:700; letter-spacing:0.3px; }
.badge-green { background:#E7F3EC; color:#1B5E35; }
.badge-peach { background:#FDEAE3; color:#C75B3D; }
.badge-grey  { background:#EEF1EF; color:#7C8B80; }

/* ESG bar */
.esg-track { background:#EEF1EF; border-radius:4px; height:7px; overflow:hidden; }
.esg-fill  { height:7px; border-radius:4px; }

/* Verify banner */
.verify-banner {
  background: linear-gradient(135deg, #1B5E35 0%, #2E7D4F 100%);
  border-radius: 16px; padding: 30px 24px; text-align: center;
  margin-bottom: 20px; color: white;
}

/* Journey timeline */
.jt-node { display:flex; gap:14px; margin-bottom:4px; }
.jt-dot {
  flex-shrink:0; width:36px; height:36px; border-radius:50%;
  background:#E7F3EC; border:2px solid #1B5E35;
  display:flex; align-items:center; justify-content:center; font-size:14px; font-weight:700;
}
.jt-line { width:2px; flex:1; min-height:20px; background:linear-gradient(#CFE6D8,#E6EEE9); margin:2px auto; }

/* Scrollbar */
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:#F0F4F1; }
::-webkit-scrollbar-thumb { background:#CFE6D8; border-radius:3px; }

/* Hide chrome */
#MainMenu, footer, header { visibility:hidden !important; }
[data-testid="stToolbar"] { display:none !important; }
</style>
""", unsafe_allow_html=True)

# ── State ────────────────────────────────────────────────────────────────────
from data import init_state
init_state()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="sb-logo">
      <img src="{LOGO_SIDEBAR_SRC}" alt="TradeProof"
           style="width:200px;max-width:100%;display:block;margin:0 auto 2px;"/>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("nav", [
        "Dashboard",
        "Suppliers",
        "Product Passports",
        "Journey Tracker",
        "Verify Product",
        "ESG Report",
    ], label_visibility="collapsed")

    st.markdown("""
    <div class="sb-footer">
      TradeProof (Pty) Ltd<br>
      Johannesburg, South Africa<br>
      <span class="status-dot"></span>Platform Online
    </div>
    """, unsafe_allow_html=True)

# ── Route ────────────────────────────────────────────────────────────────────
if   "Dashboard" in page: from pages.dashboard import render; render()
elif "Suppliers" in page: from pages.suppliers import render; render()
elif "Passport"  in page: from pages.passports import render; render()
elif "Journey"   in page: from pages.journey   import render; render()
elif "Verify"    in page: from pages.scan      import render; render()
elif "ESG"       in page: from pages.esg       import render; render()
