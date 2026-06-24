"""pages/suppliers.py"""
import streamlit as st
from data import make_hash, now_ts, short_id, add_ledger_entry, update_supplier, delete_supplier
from branding import esg_color, page_header, section

# ── SA-relevant supplier categories ──────────────────────
CATEGORIES = [
    "Wine & Viticulture",
    "Rooibos & Tea",
    "Citrus & Fresh Produce",
    "Macadamia & Nuts",
    "Fashion & Apparel",
    "Cosmetics & Beauty",
    "Food & Agriculture",
    "Industrial / Manufacturing",
    "Other",
]

# ── Real certifications grouped by type ──────────────────
# Every entry here is a real, independently verifiable certification body.
CERT_GROUPS = {
    "South Africa": [
        "BBBEE Level 1", "BBBEE Level 2", "BBBEE Level 3", "BBBEE Level 4",
        "SABS", "SIZA", "WIETA", "IPW", "PPECB", "NRCS",
    ],
    "Food Safety & Agriculture": [
        "HACCP", "FSSC 22000", "ISO 22000", "BRC Global Standard",
        "SQF", "GlobalGAP", "GlobalGAP GRASP",
    ],
    "Organic & Natural": [
        "EU Organic", "USDA Organic", "Ecocert", "COSMOS Organic",
        "NATRUE", "Rainforest Alliance", "Demeter",
    ],
    "Ethical Trade": [
        "Fairtrade International", "Sedex / SMETA", "SA8000",
        "Better Cotton Initiative",
    ],
    "Textile & Fashion": [
        "OEKO-TEX Standard 100", "GOTS",
    ],
    "Cosmetics": [
        "Cruelty-Free International", "Leaping Bunny", "Vegan Society", "ISO 22716",
    ],
    "Management Systems": [
        "ISO 9001", "ISO 14001", "ISO 50001",
    ],
    "ESG & Corporate": [
        "B-Corp", "GRI", "CDP", "Science Based Targets (SBTi)",
        "Ecovadis", "WWF Conservation Champion",
    ],
}

ALL_CERTS = [c for certs in CERT_GROUPS.values() for c in certs]


def cert_picker(prefix: str, defaults: list = None):
    """Grouped certification multiselects — one expander per category.
    Returns a flat list of all selected certifications."""
    defaults = defaults or []
    selected = []
    st.markdown("<div style='margin-top:4px;margin-bottom:2px;"
                "font-size:12px;font-weight:600;color:#374151;'>Certifications</div>",
                unsafe_allow_html=True)
    cols = st.columns(2)
    for i, (group, certs) in enumerate(CERT_GROUPS.items()):
        with cols[i % 2]:
            picked = st.multiselect(
                group, certs,
                default=[c for c in defaults if c in certs],
                key=f"cert_{prefix}_{group}",
            )
            selected.extend(picked)
    return selected


def _esg_bar(score):
    c = esg_color(score)
    return f"""
    <div style="margin:6px 0 2px;">
      <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
        <span style="font-size:11px;color:#7C8B80;font-weight:600;">ESG SCORE</span>
        <span style="font-size:14px;font-weight:700;color:{c};">{score}<span style="font-size:10px;color:#aab8b0;">/100</span></span>
      </div>
      <div class="esg-track"><div class="esg-fill" style="width:{score}%;background:{c};"></div></div>
    </div>"""


def render():
    st.markdown(page_header("Suppliers", "On-chain verified records — tamper-proof and permanently auditable"),
                unsafe_allow_html=True)

    sup            = st.session_state.suppliers
    editing        = st.session_state.editing_ids
    pending_delete = st.session_state.pending_delete_ids

    # ── Pending applications alert ────────────────────────
    pending = [s for s in sup if s["status"] == "Pending"]
    if pending:
        names = ", ".join(s["name"] for s in pending)
        st.markdown(f"""
        <div style="background:#FFF8E1;border:1px solid #FFD54F;border-radius:10px;
                    padding:12px 16px;margin-bottom:14px;font-size:13px;color:#5D4037;">
          <b>Pending Applications ({len(pending)}):</b> {names} —
          expand their card below to Verify or Decline.
        </div>
        """, unsafe_allow_html=True)

    # ── Filter row ────────────────────────────────────────
    fc1, fc2 = st.columns([3, 2])
    search   = fc1.text_input("Search", placeholder="Name, location or category…",
                               label_visibility="collapsed")
    status_f = fc2.radio("Status", ["All", "Verified", "Pending", "Declined"],
                          horizontal=True, label_visibility="collapsed")

    filtered = [s for s in sup
                if (not search or any(search.lower() in s[k].lower()
                                       for k in ("name", "location", "category")))
                and (status_f == "All" or s["status"] == status_f)]
    filtered.sort(key=lambda s: (s["status"] != "Pending", -s["esg_score"]))

    v   = sum(1 for s in filtered if s["status"] == "Verified")
    d   = sum(1 for s in filtered if s["status"] == "Declined")
    avg = round(sum(s["esg_score"] for s in filtered) / len(filtered), 0) if filtered else 0
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Suppliers",  len(filtered))
    m2.metric("Verified",   v)
    m3.metric("Pending",    len([s for s in filtered if s["status"] == "Pending"]))
    m4.metric("Avg ESG",    f"{avg:.0f}/100")

    st.markdown(section("SUPPLIER LIST"), unsafe_allow_html=True)

    for s in filtered:
        sid               = s["id"]
        is_editing        = sid in editing
        is_pending_delete = sid in pending_delete

        with st.expander(
            f"{s['name']}  ·  {s['location']}  ·  ESG {s['esg_score']}/100",
            expanded=(is_editing or is_pending_delete or s["status"] == "Pending"),
        ):

            # ── EDIT MODE ──────────────────────────────────
            if is_editing:
                with st.form(f"edit_sup_{sid}"):
                    e1, e2 = st.columns(2)
                    name_v     = e1.text_input("Company Name", value=s["name"])
                    location_v = e2.text_input("Location", value=s["location"])
                    cat_idx    = CATEGORIES.index(s["category"]) if s["category"] in CATEGORIES else 0
                    category_v = e1.selectbox("Category", CATEGORIES, index=cat_idx)
                    esg_v      = st.slider("ESG Score", 0, 100, s["esg_score"])
                    tax_v      = st.checkbox("Tax clearance confirmed (SARS)",
                                              value=(s.get("tax_status") == "Compliant"))

                st.markdown("**Certifications (edit)**")
                certs_v = cert_picker(f"edit_{sid}", defaults=s["certifications"])

                sc1, sc2 = st.columns(2)
                if sc1.button("Save Changes", key=f"save_{sid}", use_container_width=True):
                    update_supplier(sid, name=name_v.strip(), location=location_v.strip(),
                                    category=category_v, certifications=certs_v,
                                    esg_score=esg_v,
                                    tax_status="Compliant" if tax_v else "Unconfirmed")
                    add_ledger_entry("SUPPLIER_UPDATED", sid)
                    editing.discard(sid)
                    st.success(f"{name_v} updated and re-sealed on-chain.")
                    st.rerun()
                if sc2.button("Cancel", key=f"cancel_{sid}", use_container_width=True):
                    editing.discard(sid)
                    st.rerun()
                continue

            # ── READ-ONLY VIEW ─────────────────────────────
            status = s["status"]
            if status == "Verified":
                badge = '<span class="badge badge-green">Verified</span>'
            elif status == "Declined":
                badge = '<span class="badge" style="background:#FDEAE3;color:#C75B3D;' \
                        'border:1px solid #F6CBB9;">Declined</span>'
            else:
                badge = '<span class="badge badge-peach">Pending</span>'

            certs = " · ".join(s["certifications"]) if s["certifications"] \
                    else "No certifications on record"

            ec1, ec2 = st.columns([5, 2])
            with ec1:
                st.markdown(f"""
                <div style="margin-bottom:10px;">{badge}
                  <span style="font-size:11px;color:#aab8b0;margin-left:10px;">
                    {s["category"]} · Registered {s["registered"][:10]}
                  </span>
                </div>
                <div style="font-size:13px;color:#374151;line-height:1.9;">
                  <b>Certifications:</b>
                  <span style="color:#1B5E35;">{certs}</span><br>
                  <b>Tax Clearance:</b>
                  {"Compliant" if s.get("tax_status") == "Compliant" else "Unconfirmed"}
                  &nbsp;·&nbsp; <b>CIPC:</b> {s.get("cipc_status","Unconfirmed")}
                </div>
                <div style="margin-top:10px;">
                  <span style="font-size:11px;color:#aab8b0;">Blockchain hash: </span>
                  <span class="hash-pill">{s["hash"]}</span>
                </div>
                """, unsafe_allow_html=True)

            with ec2:
                st.markdown(_esg_bar(s["esg_score"]), unsafe_allow_html=True)

                # Verify / Decline — only shown for pending suppliers
                if status == "Pending":
                    if st.button("Verify Supplier", key=f"v_{sid}",
                                 use_container_width=True):
                        update_supplier(sid, status="Verified")
                        add_ledger_entry("SUPPLIER_VERIFIED", sid)
                        st.success(f"{s['name']} verified and sealed on-chain.")
                        st.rerun()
                    if st.button("Decline Application", key=f"dec_{sid}",
                                 use_container_width=True):
                        update_supplier(sid, status="Declined")
                        add_ledger_entry("SUPPLIER_DECLINED", sid)
                        st.warning(f"{s['name']} application declined.")
                        st.rerun()

            st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

            # ── DELETE CONFIRMATION ────────────────────────
            if is_pending_delete:
                st.markdown(f"""
                <div style="background:#FDEAE3;border:1px solid #F6CBB9;border-radius:8px;
                            padding:10px 14px;margin-bottom:8px;font-size:12.5px;color:#7D4429;">
                  Remove <b>{s['name']}</b>? Products linked to this supplier will show
                  "Unknown supplier." This is logged on-chain and cannot be undone.
                </div>
                """, unsafe_allow_html=True)
                dc1, dc2 = st.columns(2)
                if dc1.button("Confirm Delete", key=f"confirmdel_{sid}", use_container_width=True):
                    delete_supplier(sid)
                    add_ledger_entry("SUPPLIER_REMOVED", sid)
                    pending_delete.discard(sid)
                    st.success(f"{s['name']} removed from the registry.")
                    st.rerun()
                if dc2.button("Cancel", key=f"canceldel_{sid}", use_container_width=True):
                    pending_delete.discard(sid)
                    st.rerun()
            else:
                ac1, ac2 = st.columns(2)
                if ac1.button("Edit", key=f"edit_{sid}", use_container_width=True):
                    editing.add(sid)
                    st.rerun()
                if ac2.button("Delete", key=f"del_{sid}", use_container_width=True):
                    pending_delete.add(sid)
                    st.rerun()

    if not filtered:
        st.info("No suppliers match your search.")

    # ── Add new supplier ──────────────────────────────────
    st.markdown(section("ADD NEW SUPPLIER"), unsafe_allow_html=True)
    with st.form("sup_form", clear_on_submit=True):
        r1, r2 = st.columns(2)
        name     = r1.text_input("Company Name *")
        location = r2.text_input("Location (City, Province) *")
        category = r1.selectbox("Category", CATEGORIES)
        esg      = st.slider("Self-Declared ESG Score", 0, 100, 50,
                             help="Will be independently verified by TradeProof before activation.")

        with st.expander("Additional registration details (optional)"):
            d1, d2 = st.columns(2)
            cipc   = d1.text_input("CIPC Registration Number")
            tax_ok = d2.checkbox("Tax clearance confirmed (SARS)")

        submitted = st.form_submit_button("Submit Application", use_container_width=True)

    # cert_picker must live OUTSIDE the form (Streamlit limitation with nested widgets)
    if "sup_form_certs" not in st.session_state:
        st.session_state.sup_form_certs = []
    new_certs = cert_picker("add_new")

    if submitted:
        if not name.strip() or not location.strip():
            st.error("Company name and location are required.")
        else:
            nid = f"SUP-{short_id()}"
            ns  = {
                "id": nid, "name": name.strip(), "location": location.strip(),
                "category": category, "certifications": new_certs,
                "esg_score": esg,
                "tax_status": "Compliant" if tax_ok else "Unconfirmed",
                "cipc_status": "Active" if cipc.strip() else "Unconfirmed",
                "status": "Pending", "registered": now_ts(),
            }
            ns["hash"] = make_hash(ns)
            st.session_state.suppliers.append(ns)
            add_ledger_entry("SUPPLIER_REG", nid)
            st.success(f"**{name}** submitted as `{nid}` — pending verification.")
            st.rerun()
