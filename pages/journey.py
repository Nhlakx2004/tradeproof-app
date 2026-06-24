"""pages/journey.py"""
import streamlit as st
from data import make_hash, now_ts, add_ledger_entry, get_passport, get_supplier, get_journey, delete_milestone
from branding import esg_color, page_header, section


def _monogram(stage):
    """Single-letter monogram from the stage name — replaces per-category emoji icons."""
    s = stage.strip()
    return s[0].upper() if s else "?"


def render():
    st.markdown(page_header("Journey Tracker", "Every supply chain movement timestamped and permanently recorded"),
                unsafe_allow_html=True)

    pas = st.session_state.passports
    if not pas:
        st.info("No products yet — create one in Product Passports first.")
        return

    opts    = {f"{p['id']}  —  {p['product_name']}": p["id"] for p in pas}
    choice  = st.selectbox("Select Product", list(opts.keys()))
    pid     = opts[choice]
    pp      = get_passport(pid)
    sup     = get_supplier(pp["supplier_id"]) if pp else None
    journey = get_journey(pid)

    if pp and sup:
        eg = sup["esg_score"]
        ec = esg_color(eg)
        st.markdown(f"""
        <div style="background:#E7F3EC;border:1px solid #CFE6D8;border-radius:10px;
                    padding:12px 16px;margin:12px 0 20px;font-size:13px;color:#2E4A36;">
          <b>{pp["product_name"]}</b> &nbsp;·&nbsp; Supplier: <b>{sup["name"]}</b>
          &nbsp;·&nbsp; Carbon: <b>{pp["carbon_kg"]} kg CO₂e</b>
          &nbsp;·&nbsp; ESG: <b style="color:{ec};">{eg}/100</b>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(section("SUPPLY CHAIN JOURNEY"), unsafe_allow_html=True)

    if journey and journey.get("milestones"):
        ms = journey["milestones"]
        st.caption(f"{len(ms)} milestone(s) recorded on-chain for this product.")

        for i, m in enumerate(ms):
            is_last  = i == len(ms) - 1
            mono     = _monogram(m["stage"])
            ring_col = "#1B5E35" if m["verified"] else "#F07A5A"
            bg_col   = "#E7F3EC" if m["verified"] else "#FDEAE3"
            tick     = "VERIFIED" if m["verified"] else "PENDING"
            mhash    = make_hash({"s":m["stage"],"l":m["location"],"t":m["ts"]})

            row = st.container()
            with row:
                col_dot, col_body = st.columns([0.5, 9.5])
                with col_dot:
                    st.markdown(f"""
                    <div style="display:flex;flex-direction:column;align-items:center;height:100%;">
                      <div class="jt-dot" style="background:{bg_col};border-color:{ring_col};color:{ring_col};">{mono}</div>
                      {"<div class='jt-line'></div>" if not is_last else ""}
                    </div>
                    """, unsafe_allow_html=True)
                with col_body:
                    st.markdown(f"""
                    <div style="background:#fff;border:1px solid #E6EEE9;border-radius:10px;
                                padding:12px 16px;margin-bottom:{'16px' if not is_last else '6px'};">
                      <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;">
                        <span style="font-weight:700;color:#20302A;font-size:13px;">{m["stage"]}</span>
                        <div style="display:flex;align-items:center;gap:8px;">
                          <span style="font-size:10px;font-weight:700;color:{ring_col};
                                       background:{bg_col};padding:2px 9px;border-radius:10px;">{tick}</span>
                          <span style="font-size:11px;color:#aab8b0;">{m["ts"]}</span>
                        </div>
                      </div>
                      <div style="font-size:12px;color:#7C8B80;margin-top:4px;">{m["location"]}</div>
                      <div style="font-family:monospace;font-size:9px;color:#C5D2CB;margin-top:5px;">{mhash[:52]}…</div>
                    </div>
                    """, unsafe_allow_html=True)

        if all(m["verified"] for m in ms):
            st.markdown(f"""
            <div style="background:#E7F3EC;border:1px solid #CFE6D8;border-radius:10px;
                        padding:12px 16px;margin-top:6px;">
              <b style="color:#1B5E35;">Full journey verified on blockchain</b><br>
              <span style="font-size:11px;color:#374151;font-family:monospace;">{journey["hash"][:54]}…</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No milestones recorded yet — add the first one below.")

    # ── Add milestone ──────────────────────────────────────
    st.markdown(section("LOG NEW MILESTONE"), unsafe_allow_html=True)
    with st.form("ms_form", clear_on_submit=True):
        mc1, mc2 = st.columns(2)
        stage    = mc1.text_input("Stage / Event *", placeholder="e.g. Dispatched from Warehouse")
        location = mc2.text_input("Location *",      placeholder="e.g. Cape Town DC")

        if st.form_submit_button("Record Milestone", use_container_width=True):
            if not stage.strip() or not location.strip():
                st.error("Stage and location are required.")
            else:
                nm = {"stage":stage.strip(),"location":location.strip(),
                      "ts":now_ts()[:16],"verified":True}
                if journey:
                    idx = next(i for i,j in enumerate(st.session_state.journeys) if j["passport_id"]==pid)
                    st.session_state.journeys[idx]["milestones"].append(nm)
                    st.session_state.journeys[idx]["hash"] = make_hash(st.session_state.journeys[idx])
                else:
                    nj = {"passport_id":pid,"milestones":[nm]}
                    nj["hash"] = make_hash(nj)
                    st.session_state.journeys.append(nj)
                add_ledger_entry("JOURNEY_MILESTONE", pid)
                st.success(f"'{stage}' recorded on blockchain.")
                st.rerun()
