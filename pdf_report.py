"""pdf_report.py — generates supplier-specific ESG/traceability PDF reports.

Each report covers exactly ONE supplier. This matters for two reasons:
1. Security — a supplier's certifications, ESG score, and pricing-adjacent data
   shouldn't be visible to other suppliers just because they're in the same export.
2. Trust — a PDF with this supplier's own sealed hash on it reads as an official,
   tamper-evident document, not an editable text dump of your whole supplier base.
"""
import io
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                 HRFlowable, Image as RLImage)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

try:
    from PIL import Image as PILImage
except ImportError:
    PILImage = None

GREEN      = HexColor("#1B5E35")
GREEN_PALE = HexColor("#E7F3EC")
PEACH_PALE = HexColor("#FDEAE3")
CHARCOAL   = HexColor("#20302A")
MUTED      = HexColor("#7C8B80")
BORDER     = HexColor("#E6EEE9")
WHITE      = HexColor("#FFFFFF")

_styles = getSampleStyleSheet()
TITLE_STYLE = ParagraphStyle("RTitle", fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=CHARCOAL)
SUB_STYLE   = ParagraphStyle("RSub", fontName="Helvetica", fontSize=10, leading=14, textColor=MUTED)
H_STYLE     = ParagraphStyle("RH", fontName="Helvetica-Bold", fontSize=12, leading=15,
                              textColor=GREEN, spaceBefore=16, spaceAfter=6)
BODY_STYLE  = ParagraphStyle("RBody", fontName="Helvetica", fontSize=9.5, leading=14, textColor=CHARCOAL)
MONO_STYLE  = ParagraphStyle("RMono", fontName="Courier", fontSize=7.5, leading=10, textColor=MUTED)


def _small_logo(logo_path, max_px=160):
    """Downscale the logo before embedding so a high-res source PNG doesn't
    bloat every generated report. Falls back to the raw path if PIL is
    unavailable or anything goes wrong — the logo is cosmetic, never fatal."""
    if not PILImage:
        return logo_path
    try:
        img = PILImage.open(logo_path).convert("RGBA")
        img.thumbnail((max_px, max_px), PILImage.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        buf.seek(0)
        return buf
    except Exception:
        return logo_path


def build_supplier_pdf(supplier: dict, passports: list, period: str, logo_path: str | None = None) -> bytes:
    """Build a single-supplier ESG/traceability PDF report.

    supplier  : one supplier dict (must include name, location, category,
                certifications, esg_score, status, hash)
    passports : list of passport dicts belonging to THIS supplier only
                (filter by supplier_id before calling this)
    period    : reporting period label, e.g. "Q1 2024 (Jan-Mar)"
    logo_path : optional path to a logo PNG; omitted gracefully if not found

    Returns raw PDF bytes, ready for st.download_button(..., mime="application/pdf").
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        topMargin=18 * mm, bottomMargin=18 * mm, leftMargin=18 * mm, rightMargin=18 * mm,
        title=f"TradeProof ESG Report - {supplier['name']}",
    )
    story = []

    # ── Header ──────────────────────────────────────────
    if logo_path:
        try:
            story.append(RLImage(_small_logo(logo_path), width=14 * mm, height=14 * mm))
            story.append(Spacer(1, 6))
        except Exception:
            pass  # logo is cosmetic only — report still builds fine without it

    story.append(Paragraph("TradeProof ESG Compliance Report", TITLE_STYLE))
    story.append(Paragraph(f"Supplier: <b>{supplier['name']}</b> &nbsp;&middot;&nbsp; {period}", SUB_STYLE))
    story.append(Paragraph(f"Generated {datetime.datetime.now():%Y-%m-%d %H:%M}", SUB_STYLE))
    story.append(HRFlowable(width="100%", thickness=1.2, color=GREEN, spaceBefore=10, spaceAfter=14))

    # ── Status banner ───────────────────────────────────
    status_bg = GREEN_PALE if supplier["status"] == "Verified" else PEACH_PALE
    banner = Table(
        [[Paragraph(f"<b>Status: {supplier['status']}</b> &nbsp;&middot;&nbsp; "
                    f"ESG Score: <b>{supplier['esg_score']}/100</b>", BODY_STYLE)]],
        colWidths=[174 * mm],
    )
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), status_bg),
        ("BOX", (0, 0), (-1, -1), 0.75, BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 12), ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    story.append(banner)

    # ── Supplier details ─────────────────────────────────
    story.append(Paragraph("SUPPLIER DETAILS", H_STYLE))
    details = [
        ["Location", supplier["location"]],
        ["Category", supplier["category"]],
        ["Certifications", ", ".join(supplier["certifications"]) or "None on record"],
    ]
    dt = Table(details, colWidths=[40 * mm, 134 * mm])
    dt.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"), ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("TEXTCOLOR", (0, 0), (-1, -1), CHARCOAL),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(dt)

    # ── Product carbon ledger (this supplier only) ───────
    story.append(Paragraph("PRODUCT CARBON LEDGER", H_STYLE))
    if passports:
        rows = [["Product", "SKU", "Carbon (kg CO2e)", "Batch"]]
        for p in passports:
            rows.append([p["product_name"], p["sku"], f"{p['carbon_kg']}", p["batch"]])
        pt = Table(rows, colWidths=[58 * mm, 38 * mm, 40 * mm, 38 * mm])
        pt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), GREEN), ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"), ("TEXTCOLOR", (0, 1), (-1, -1), CHARCOAL),
            ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, GREEN_PALE]),
            ("LEFTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(pt)
    else:
        story.append(Paragraph("No products currently linked to this supplier.", BODY_STYLE))

    # ── Blockchain verification ──────────────────────────
    story.append(Paragraph("BLOCKCHAIN VERIFICATION", H_STYLE))
    story.append(Paragraph(
        "This supplier's record is cryptographically sealed. The hash below is unique to this "
        "exact record — any change to the underlying data would produce a different hash, "
        "making tampering detectable.", BODY_STYLE))
    story.append(Spacer(1, 5))
    story.append(Paragraph(supplier["hash"], MONO_STYLE))

    # ── Footer ────────────────────────────────────────────
    story.append(Spacer(1, 18))
    story.append(HRFlowable(width="100%", thickness=0.75, color=BORDER, spaceAfter=8))
    story.append(Paragraph(
        "TradeProof (Pty) Ltd &middot; Johannesburg, South Africa &middot; "
        "This report is specific to the named supplier only and excludes data on any other "
        "supplier in the TradeProof system.", SUB_STYLE))

    doc.build(story)
    return buf.getvalue()
