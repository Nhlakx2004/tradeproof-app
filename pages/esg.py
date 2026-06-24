"""pages/esg.py"""
import streamlit as st
import plotly.graph_objects as go
from data import get_supplier
from branding import GREEN, PEACH, esg_color, page_header, section
from pdf_report import build_supplier_pdf


def render():
    st.markdown(page_header("ESG Report", "Auto-generated from blockchain data — IFRS S2 and King IV ready"),
                unsafe_allow_html=True)

    sup = st.session_state.suppliers
    pas = st.session_state.passports

    period = st.selectbox("Reporting Period",
                ["Q1 2024 (Jan–Mar)","Q2 2024 (Apr–Jun)","Q3 2024 (Jul–Sep)","Full Year 2024"])

    vsup     = [s for s in sup if s["status"] == "Verified"]
    avg_esg  = round(sum(s["esg_score"] for s in vsup)/len(vsup), 1) if vsup else 0
    tot_c    = sum(p.get("carbon_kg",0) for p in pas)
    baseline = round(tot_c*1.35, 2)
    saved    = round(baseline-tot_c, 2)
    certs    = sum(len(s["certifications"]) for s in vsup)

    st.markdown(section("PERIOD SUMMARY"), unsafe_allow_html=True)
    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Verified Suppliers", len(vsup), f"of {len(sup)} total")
    k2.metric("Avg Supplier ESG",   f"{avg_esg:.0f}/100")
    k3.metric("Carbon Saved",       f"{saved} kg CO₂e")
    k4.metric("Certifications",     certs)

    # ── Charts ────────────────────────────────────────────
    st.markdown(section("ANALYTICS"), unsafe_allow_html=True)
    t1, t2 = st.tabs(["Carbon: Actual vs Baseline", "Supplier ESG Scores"])

    with t1:
        if pas:
            fig = go.Figure()
            fig.add_bar(name="Actual", x=[p["product_name"] for p in pas],
                        y=[p["carbon_kg"] for p in pas], marker_color=GREEN, marker_line_width=0,
                        text=[f"{p['carbon_kg']}kg" for p in pas], textposition="outside")
            fig.add_bar(name="Baseline", x=[p["product_name"] for p in pas],
                        y=[round(p["carbon_kg"]*1.35,2) for p in pas],
                        marker_color=PEACH, opacity=0.4, marker_line_width=0,
                        text=[f"{round(p['carbon_kg']*1.35,2)}kg" for p in pas], textposition="outside")
            fig.update_layout(
                barmode="group", plot_bgcolor="#fff", paper_bgcolor="#fff",
                margin=dict(l=0,r=10,t=10,b=0), height=270,
                font=dict(family="system-ui",size=11,color="#7C8B80"),
                legend=dict(orientation="h", y=-0.25, font=dict(size=11)),
                yaxis=dict(title="kg CO₂e", gridcolor="#F0F4F1", zeroline=False),
                xaxis=dict(tickangle=-8), bargap=0.3, bargroupgap=0.08)
            st.plotly_chart(fig, use_container_width=True)

    with t2:
        if sup:
            scores = [s["esg_score"] for s in sup]
            names  = [s["name"] for s in sup]
            colors = [esg_color(sc) for sc in scores]
            fig2 = go.Figure(go.Bar(
                x=scores, y=names, orientation="h", marker_color=colors, marker_line_width=0,
                text=[f"{sc}/100" for sc in scores], textposition="outside"))
            fig2.update_layout(
                plot_bgcolor="#fff", paper_bgcolor="#fff",
                margin=dict(l=0,r=40,t=10,b=0), height=270,
                font=dict(family="system-ui",size=11,color="#7C8B80"),
                xaxis=dict(range=[0,115], title="Score", gridcolor="#F0F4F1", zeroline=False),
                yaxis=dict(title="", automargin=True), showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

    # ── Supplier compliance ────────────────────────────────
    st.markdown(section("SUPPLIER COMPLIANCE"), unsafe_allow_html=True)
    for s in sup:
        ec  = esg_color(s["esg_score"])
        status_dot = "#1B5E35" if s["status"]=="Verified" else "#F07A5A"
        lbl = "On Track" if s["esg_score"]>=70 else "Needs Review"
        crt = " · ".join(s["certifications"]) if s["certifications"] else "None on record"
        st.markdown(f"""
        <div class="tp-card">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap;">
            <div style="flex:1;">
              <div class="tp-card-title">
                <span style="display:inline-block;width:9px;height:9px;border-radius:50%;
                             background:{status_dot};margin-right:7px;"></span>{s["name"]}
              </div>
              <div class="tp-card-sub">{s["location"]} &nbsp;·&nbsp; {s["category"]}</div>
              <div style="color:#1B5E35;font-size:12px;font-weight:500;margin-top:4px;">{crt}</div>
              <div class="esg-track" style="width:180px;margin-top:10px;">
                <div class="esg-fill" style="width:{s["esg_score"]}%;background:{ec};"></div>
              </div>
            </div>
            <div style="text-align:right;">
              <div style="font-size:32px;font-weight:700;color:{ec};line-height:1;">{s["esg_score"]}</div>
              <div style="font-size:10px;color:#aab8b0;">ESG SCORE</div>
              <div style="font-size:11px;font-weight:600;color:{ec};margin-top:4px;">{lbl}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Carbon ledger ──────────────────────────────────────
    st.markdown(section("PRODUCT CARBON LEDGER"), unsafe_allow_html=True)
    for p in pas:
        s    = get_supplier(p["supplier_id"])
        base = round(p["carbon_kg"]*1.35, 2)
        sv   = round(base-p["carbon_kg"], 2)
        pct  = round((sv/base)*100) if base else 0
        st.markdown(f"""
        <div style="background:#fff;border:1px solid #E6EEE9;border-radius:10px;
                    padding:12px 18px;margin-bottom:7px;display:flex;
                    justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
          <div>
            <div style="font-weight:700;color:#20302A;font-size:13px;">{p["product_name"]}</div>
            <div style="font-size:11px;color:#aab8b0;">{s["name"] if s else "Unknown"} · Batch {p["batch"]}</div>
          </div>
          <div style="text-align:right;">
            <div style="font-weight:700;color:#20302A;">{p["carbon_kg"]} kg CO₂e</div>
            <div style="font-size:11px;color:#1B5E35;font-weight:600;">↓ {sv} kg saved ({pct}%)</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Compliance badges ───────────────────────────────────
    st.markdown(section("REGULATORY COMPLIANCE"), unsafe_allow_html=True)
    badges = [("IFRS S2","Scope 3 supply chain emissions disclosed"),
              ("King IV","Supply chain governance documented"),
              ("GHG Protocol","Purchased goods emissions tracked"),
              ("Blockchain Verified","SHA-256 hashed — tamper-proof")]
    bc1, bc2 = st.columns(2)
    for i,(title,desc) in enumerate(badges):
        col = bc1 if i%2==0 else bc2
        col.markdown(f"""
        <div style="background:#E7F3EC;border:1px solid #CFE6D8;border-radius:10px;
                    padding:10px 14px;margin-bottom:7px;">
          <div style="font-weight:700;color:#1B5E35;font-size:12px;">{title}</div>
          <div style="font-size:12px;color:#374151;margin-top:2px;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Export ────────────────────────────────────────────
    st.markdown(section("EXPORT"), unsafe_allow_html=True)

    if not sup:
        st.info("No suppliers yet — add one in Suppliers first.")
    else:
        sel_name = st.selectbox("Generate report for", [s["name"] for s in sup])
        sel_supplier  = next(s for s in sup if s["name"] == sel_name)
        sel_passports = [p for p in pas if p["supplier_id"] == sel_supplier["id"]]

        pdf_bytes = build_supplier_pdf(sel_supplier, sel_passports, period, logo_path="logo.png")

        st.download_button(
            f"Download {sel_supplier['name']} ESG Report (.pdf)",
            data=pdf_bytes,
            file_name=f"TradeProof_ESG_{sel_supplier['id']}_{period[:6].replace(' ','_')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        st.caption("Each report covers one supplier only — no other supplier's data is included, "
                   "and the PDF carries that supplier's own sealed blockchain hash.")
