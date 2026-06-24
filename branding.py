"""
branding.py — shared brand constants for TradeProof
"""
import os, base64

_DIR = os.path.dirname(os.path.abspath(__file__))


def _b64(filename):
    with open(os.path.join(_DIR, filename)) as f:
        return f.read().strip()


# ── Logo assets ──────────────────────────────────────────
LOGO_SIDEBAR_SRC = f"data:image/png;base64,{_b64('logo_b64_sidebar.txt')}"
LOGO_ICON_SRC    = f"data:image/png;base64,{_b64('logo_icon_b64.txt')}"

# ── Brand colours ────────────────────────────────────────
GREEN       = "#1B5E35"   # primary — deep forest green
GREEN_MID   = "#2E7D4F"   # secondary green
GREEN_PALE  = "#E7F3EC"   # light green background
PEACH       = "#F07A5A"   # accent — coral / peach
PEACH_PALE  = "#FDEAE3"   # light peach background
WHITE       = "#FFFFFF"
PAGE_BG     = "#FAFBF9"
TEXT        = "#20302A"
MUTED       = "#7C8B80"
BORDER      = "#E6EEE9"
SIDEBAR_GREY = "#34383C"  # neutral charcoal — sidebar background


def esg_color(score: int) -> str:
    """Two-tone scoring in brand colours: green = good, peach = needs attention."""
    if score >= 70:
        return GREEN
    return PEACH


# A clean inline checkmark icon (no emoji) used wherever a "verified" visual is needed.
CHECK_ICON_LARGE = """
<svg width="50" height="50" viewBox="0 0 24 24" fill="none" style="margin:0 auto;display:block;">
  <circle cx="12" cy="12" r="10" stroke="white" stroke-width="1.4" opacity="0.4"></circle>
  <path d="M7 12.5l3.2 3.2L17 9" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>
</svg>
"""


def page_header(title: str, subtitle: str) -> str:
    """Returns HTML for a consistent page header with the brand icon mark."""
    return f"""
    <div class="page-header">
      <img src="{LOGO_ICON_SRC}" class="page-header-icon" alt="TradeProof"/>
      <div><h2>{title}</h2><p>{subtitle}</p></div>
    </div>"""


def section(label: str) -> str:
    return f"<div class='sec-head'>{label}</div>"
