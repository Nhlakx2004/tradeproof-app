"""pages/dashboard.py"""
import streamlit as st
import plotly.graph_objects as go
from data import get_supplier, verify_chain, reset_demo
from branding import GREEN, PEACH, esg_color, page_header, section


def render():
    st.markdown(page_header("Dashboard", "A live overview of your blockchain-verified supply chain"),
                unsafe_allow_html=True)

    sup = st.session_state.suppliers
    pas = st.session_state.passports
    led = st.session_state.ledger

    verified  = sum(1 for s in sup if s["status"] == "Verified")
    pending_n = sum(1 for s in sup if s["status"] == "Pending")
    tot_c     = sum(p.get("carbon_kg", 0) for p in pas)
    saved     = round(tot_c * 0.35, 2)

    # ── Pending applications alert ────────────────────────
    if pending_n:
        pending_names = ", ".join(s["name"] for s in sup if s["status"] == "Pending")
        st.markdown(f"""
        <div style="background:#FFF8E1;border:1px solid #FFD54F;border-radius:10px;
                    padding:12px 16px;margin-bottom:16px;font-size:13px;color:#5D4037;">
          <b>Action required — {pending_n} pending supplier application(s):</b>
          {pending_names}. Go to <b>Suppliers</b> to Verify or Decline.
        </div>
        """, unsafe_allow_html=True)

    # ── KPIs ──────────────────────────────────────────────
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Verified Suppliers", f"{verified}/{len(sup)}")
    k2.metric("Pending Applications", pending_n)
    k3.metric("Product Passports",   str(len(pas)))
    k4.metric("Blockchain Records",  str(len(led)))
    k5.metric("Carbon Saved",        f"{saved} kg CO₂e")

    # ── Analytics charts ──────────────────────────────────
    st.markdown(section("ANALYTICS"), unsafe_allow_html=True)
    t1, t2 = st.tabs(["Carbon Footprint", "Supplier ESG Scores"])

    with t1:
        if pas:
            names  = [p["product_name"] for p in pas]
            actual = [p["carbon_kg"] for p in pas]
            base   = [round(c * 1.35, 2) for c in actual]
            fig = go.Figure()
            fig.add_bar(name="Actual", x=names, y=actual, marker_color=GREEN,
                        marker_line_width=0, text=[f"{v}kg" for v in actual],
                        textposition="outside", textfont=dict(size=11))
            fig.add_bar(name="Without TradeProof (baseline)", x=names, y=base,
                        marker_color=PEACH, opacity=0.45, marker_line_width=0,
                        text=[f"{v}kg" for v in base],
                        textposition="outside", textfont=dict(size=11))
            fig.update_layout(
                barmode="group", plot_bgcolor="#fff", paper_bgcolor="#fff",
                margin=dict(l=0, r=10, t=10, b=0), height=270,
                font=dict(family="system-ui", size=11, color="#7C8B80"),
                legend=dict(orientation="h", y=-0.25, font=dict(size=11)),
                yaxis=dict(title="kg CO₂e", gridcolor="#F0F4F1", zeroline=False),
                xaxis=dict(tickangle=-8),
                bargap=0.3, bargroupgap=0.08,
            )
            st.plotly_chart(fig, use_container_width=True)

    with t2:
        if sup:
            vsup   = [s for s in sup if s["status"] == "Verified"]
            scores = [s["esg_score"] for s in vsup]
            names  = [s["name"] for s in vsup]
            colors = [esg_color(sc) for sc in scores]
            fig2 = go.Figure(go.Bar(
                x=scores, y=names, orientation="h",
                marker_color=colors, marker_line_width=0,
                text=[f"{sc}/100" for sc in scores],
                textposition="outside", textfont=dict(size=11, color="#20302A"),
            ))
            fig2.update_layout(
                plot_bgcolor="#fff", paper_bgcolor="#fff",
                margin=dict(l=0, r=40, t=10, b=0), height=270,
                font=dict(family="system-ui", size=11, color="#7C8B80"),
                xaxis=dict(range=[0, 115], gridcolor="#F0F4F1", zeroline=False, title="ESG Score"),
                yaxis=dict(title="", automargin=True),
                showlegend=False,
            )
            st.plotly_chart(fig2, use_container_width=True)

    # ── Blockchain integrity ──────────────────────────────
    st.markdown(section("BLOCKCHAIN INTEGRITY"), unsafe_allow_html=True)
    is_valid, broken_at = verify_chain()
    if is_valid:
        st.markdown(f"""
        <div style="background:#E7F3EC;border:1px solid #CFE6D8;border-radius:10px;
                    padding:14px 18px;margin-bottom:14px;display:flex;
                    justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">
          <div>
            <div style="font-weight:700;color:#1B5E35;font-size:13px;">Chain Verified — Unbroken</div>
            <div style="font-size:11.5px;color:#5A6B5D;margin-top:2px;">
              All {len(led)} blocks correctly link to the one before them.
            </div>
          </div>
          <span class="badge badge-green">{len(led)} BLOCKS</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background:#FDEAE3;border:1px solid #F6CBB9;border-radius:10px;
                    padding:14px 18px;margin-bottom:14px;">
          <div style="font-weight:700;color:#C75B3D;font-size:13px;">Chain Broken at Block {broken_at}</div>
          <div style="font-size:11.5px;color:#7D4429;margin-top:2px;">
            A record was altered — every block from #{broken_at} onward no longer matches.
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Recent blockchain activity ────────────────────────
    st.markdown(section("RECENT BLOCKCHAIN ACTIVITY"), unsafe_allow_html=True)
    st.caption("Each block's hash is built from its own data plus the previous block's hash — "
               "the link that makes tampering detectable.")

    LEDGER_TYPES = {
        "SUPPLIER_REG":      ("#1B5E35", "Supplier Application Received"),
        "SUPPLIER_VERIFIED": ("#2E7D4F", "Supplier Verified"),
        "SUPPLIER_DECLINED": ("#C75B3D", "Supplier Application Declined"),
        "SUPPLIER_UPDATED":  ("#5B8DEF", "Supplier Updated"),
        "SUPPLIER_REMOVED":  ("#C75B3D", "Supplier Removed"),
        "PASSPORT_CREATE":   ("#1B5E35", "Passport Issued"),
        "PASSPORT_UPDATED":  ("#5B8DEF", "Passport Updated"),
        "PASSPORT_REMOVED":  ("#C75B3D", "Passport Removed"),
        "JOURNEY_MILESTONE": ("#F07A5A", "Journey Milestone"),
        "JOURNEY_LOG":       ("#F07A5A", "Journey Logged"),
        "MILESTONE_REMOVED": ("#C75B3D", "Milestone Removed"),
    }
    for entry in reversed(led[-6:]):
        dot_color, lbl = LEDGER_TYPES.get(entry["type"], ("#7C8B80", entry["type"]))
        prev_h = entry.get("prev_hash", "—")
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;padding:11px 16px;
                    background:#fff;border:1px solid #E6EEE9;border-radius:10px;margin-bottom:6px;">
          <span style="width:10px;height:10px;border-radius:50%;background:{dot_color};flex-shrink:0;"></span>
          <div style="flex:1;">
            <span style="font-weight:700;color:#20302A;font-size:12.5px;">
              Block #{entry["block"]} · {lbl}
            </span>
            <span style="color:#9aa8a0;font-size:11px;margin-left:10px;">{entry["ts"]}</span><br>
            <span style="font-family:monospace;font-size:9.5px;color:#C5D2CB;">
              prev {prev_h[:16]}… → hash {entry["hash"][:16]}…
            </span>
          </div>
          <span class="badge badge-green">SEALED</span>
        </div>
        """, unsafe_allow_html=True)

    # ── Product passports overview ─────────────────────────
    st.markdown(section("PRODUCT PASSPORTS"), unsafe_allow_html=True)
    for p in pas:
        s  = get_supplier(p["supplier_id"])
        sn = s["name"] if s else "Unknown"
        eg = s["esg_score"] if s else 0
        ec = esg_color(eg)
        st.markdown(f"""
        <div class="tp-card">
          <div style="display:flex;justify-content:space-between;align-items:center;
                      gap:12px;flex-wrap:wrap;">
            <div>
              <div class="tp-card-title">{p["product_name"]}</div>
              <div class="tp-card-sub">
                {sn} &nbsp;·&nbsp; {p["carbon_kg"]} kg CO₂e &nbsp;·&nbsp;
                ESG <b style="color:{ec};">{eg}/100</b>
              </div>
            </div>
            <span class="badge badge-green">ACTIVE</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Demo reset ────────────────────────────────────────
    st.markdown(section("DEMO TOOLS"), unsafe_allow_html=True)
    st.caption("For presenter use only — reloads all seed data if anything goes wrong during demo.")
    if st.button("Reset Demo Data", use_container_width=False):
        reset_demo()
        st.success("Demo data reset. All seed suppliers, passports, and journeys restored.")
        st.rerun()
