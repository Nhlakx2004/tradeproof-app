"""pages/scan.py"""
import streamlit as st
from data import get_passport, get_supplier, get_journey
from branding import esg_color, page_header, section

import streamlit as st
from urllib.parse import unquote

# Check if arriving from a QR code scan
params = st.query_params
if "verify" in params:
  pid = unqoute(params["verify"])
  st.session_state["qr_scan_id"] = pid


def render():
    st.markdown(page_header("Verify Product", "What a customer sees when they scan a TradeProof QR code"),
                unsafe_allow_html=True)
    
    # Auto-load from QR scan if arriving via URL
    preselect = st.session_state.get("qr_scan_id", None)

    pas = st.session_state.passports
    if not pas:
        st.warning("No passports to verify yet — create one in Product Passports first.")
        return

    opts   = {f"{p['id']} - {p['product_name']}": p["id"] for p in pas}

    #If arriving from QR, find the matching product
    default_index = 0
    if preselect:
        for i, pid in enumerate(opts.values()):
            if pid == preselect:
                default_index = i
                break
                        
    choice = st.selectbox("Select a product to simulate a scan",
                          list(opts.keys()),
                          index=default_index)
    st.markdown("---")
    _verify_view(opts[choice])
    
        # ── How it works (collapsed by default) ───────────────
    st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
    with st.expander("How does QR scanning actually work?"):
        steps = [
            ("Supplier registers","The supplier's details, certifications and ESG score are hashed and sealed on the blockchain."),
            ("Brand issues a passport","Each product batch gets a unique passport ID with a SHA-256 hash that locks its data permanently."),
            ("A QR code is generated","TradeProof creates a unique QR code linking to localhost:8501/verify/[ID] (production: tradeproof.co.za/verify/[ID]), printed on the label."),
            ("Customer scans","Any phone camera opens the verification page directly — no app needed, takes about 3 seconds."),
            ("Blockchain hash verified","The record's hash is checked in under a second. Tampered or fake codes show an UNVERIFIED warning."),
            ("Full story displayed","The customer sees the verified supplier, certifications, carbon footprint and complete journey."),
        ]
        for i, (title, desc) in enumerate(steps, start=1):
            st.markdown(f"""
            <div style="display:flex;gap:12px;margin-bottom:10px;align-items:flex-start;">
              <div style="flex-shrink:0;width:30px;height:30px;border-radius:50%;background:#1B5E35;
                          display:flex;align-items:center;justify-content:center;
                          font-size:13px;font-weight:700;color:#fff;">{i}</div>
              <div>
                <div style="font-weight:700;color:#20302A;font-size:13px;">{title}</div>
                <div style="font-size:12.5px;color:#7C8B80;line-height:1.6;">{desc}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#FDEAE3;border:1px solid #F6CBB9;border-radius:10px;
                    padding:12px 16px;margin-top:8px;font-size:12.5px;color:#7D4429;">
          <b>No app required.</b> A copied QR code only points to the original product's record —
          a counterfeiter cannot create a new sealed passport without account access.
          The QR code costs nothing extra to print; it sits alongside the existing barcode.
        </div>
        """, unsafe_allow_html=True)


def _verify_view(pid):
    pp = get_passport(pid)
    if not pp:
        st.error("Passport not found — this product is not registered on TradeProof.")
        return
    sup     = get_supplier(pp["supplier_id"])
    journey = get_journey(pid)

    st.markdown(f"""
    <div class="verify-banner">
      <div style="width:56px;height:56px;border-radius:50%;
                  border:2px solid rgba(255,255,255,0.45);
                  display:flex;align-items:center;justify-content:center;
                  margin:0 auto 14px;font-size:26px;color:white;">&#10003;</div>
      <div style="font-size:22px;font-weight:700;margin-bottom:6px;">Authenticity Verified</div>
      <div style="font-size:13px;color:rgba(255,255,255,0.7);margin-bottom:14px;">
        Registered and verified on the TradeProof blockchain
      </div>
      <div style="background:rgba(0,0,0,0.18);border-radius:6px;padding:7px 14px;
                  display:inline-block;font-family:monospace;font-size:11px;color:#BCE6CC;">
        {pp["hash"][:56]}&#8230;
      </div>
    </div>
    """, unsafe_allow_html=True)

    vc1, vc2 = st.columns(2)
    with vc1:
        st.markdown(f"""
        <div class="tp-card">
          <div class="tp-card-title">{pp["product_name"]}</div>
          <div style="font-size:13px;color:#374151;line-height:1.9;margin-top:6px;">
            <b>SKU:</b> {pp["sku"]} &nbsp;·&nbsp; <b>Batch:</b> {pp["batch"]}<br>
            <b>Origin:</b> {pp["origin"]}<br>
            <b>Manufactured:</b> {pp["manufacture_date"]}<br>
            <b>Carbon:</b> {pp["carbon_kg"]} kg CO₂e
          </div>
        </div>
        """, unsafe_allow_html=True)

    with vc2:
        if sup:
            eg = sup["esg_score"]
            ec = esg_color(eg)
            st.markdown(f"""
            <div class="tp-card">
              <div class="tp-card-title">Verified Supplier</div>
              <div style="font-size:14.5px;font-weight:700;color:#20302A;margin:4px 0 2px;">{sup["name"]}</div>
              <div style="font-size:12px;color:#7C8B80;margin-bottom:10px;">{sup["location"]}</div>
              <div style="font-size:28px;font-weight:700;color:{ec};line-height:1;">{eg}
                <span style="font-size:13px;color:#aab8b0;font-weight:400;">/100</span></div>
              <div style="font-size:10px;color:#aab8b0;font-weight:600;margin-bottom:8px;">ESG SCORE</div>
              <div class="esg-track"><div class="esg-fill" style="width:{eg}%;background:{ec};"></div></div>
              <div style="margin-top:10px;font-size:12px;color:#1B5E35;">
                {" · ".join(sup["certifications"]) or "No certifications"}
              </div>
            </div>
            """, unsafe_allow_html=True)

    if pp["certifications"]:
        chips = "".join(
            f"<span style='background:#E7F3EC;color:#1B5E35;padding:5px 12px;"
            f"border-radius:20px;font-size:12px;font-weight:600;'>✓ {c}</span>"
            for c in pp["certifications"]
        )
        st.markdown(f"<div style='display:flex;gap:8px;flex-wrap:wrap;margin:14px 0;'>{chips}</div>",
                    unsafe_allow_html=True)

    if journey and journey.get("milestones"):
        st.markdown(section("VERIFIED PRODUCT JOURNEY"), unsafe_allow_html=True)
        for i, m in enumerate(journey["milestones"]):
            is_last = i == len(journey["milestones"]) - 1
            mono = m["stage"].strip()[0].upper() if m["stage"].strip() else "?"
            st.markdown(f"""
            <div class="jt-node">
              <div style="display:flex;flex-direction:column;align-items:center;flex-shrink:0;">
                <div class="jt-dot" style="background:#E7F3EC;border-color:#1B5E35;color:#1B5E35;">{mono}</div>
                {"<div class='jt-line'></div>" if not is_last else ""}
              </div>
              <div style="flex:1;padding-bottom:{'10px' if not is_last else '0'};">
                <span style="font-weight:700;color:#20302A;font-size:13px;">{m["stage"]}</span>
                <span style="font-size:11px;color:#aab8b0;margin-left:10px;">{m["location"]} · {m["ts"]}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;padding:20px 0 4px;border-top:1px solid #E6EEE9;margin-top:20px;">
      <div style="font-size:13px;font-weight:700;color:#1B5E35;">TradeProof (Pty) Ltd</div>
      <div style="font-size:11px;color:#aab8b0;margin-top:3px;">
        Blockchain traceability for South African supply chains · Johannesburg, SA
      </div>
    </div>
    """, unsafe_allow_html=True)
