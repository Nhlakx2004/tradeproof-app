"""pages/passports.py"""
import streamlit as st, io
import qrcode
from data import make_hash, now_ts, short_id, add_ledger_entry, get_supplier, update_passport, delete_passport
from branding import GREEN, esg_color, page_header, section

# ── Real product-level certifications ────────────────────
# These apply to the product itself, not the supplier company.
PRODUCT_CERTS = [
    "EU Organic", "USDA Organic", "Ecocert",
    "Fairtrade International", "Rainforest Alliance", "Demeter",
    "GOTS", "OEKO-TEX Standard 100",
    "COSMOS Organic", "Cruelty-Free International", "Leaping Bunny", "Vegan Society",
    "GlobalGAP", "HACCP", "FSSC 22000",
    "Non-GMO", "Halaal", "Kosher",
    "SABS", "B-Corp",
]

# ── QR code URL ───────────────────────────────────────────
# During demo: points to localhost so scanning in the room actually works.
# For production: change to https://tradeproof.co.za/verify/
QR_BASE_URL = "https://tradeproof.streamlit.app/verify/"


def _qr_buf(pid):
    url = f"{QR_BASE_URL}{pid}"
    qr  = qrcode.QRCode(version=2, box_size=8, border=3,
                         error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=GREEN, back_color="white")
    buf = io.BytesIO()
    img.save(buf, "PNG")
    buf.seek(0)
    return buf


def render():
    st.markdown(page_header("Product Passports", "Blockchain-anchored certificates of origin and authenticity"),
                unsafe_allow_html=True)

    pas            = st.session_state.passports
    sup            = st.session_state.suppliers
    editing        = st.session_state.editing_ids
    pending_delete = st.session_state.pending_delete_ids
    vsup_all       = [s for s in sup if s["status"] == "Verified"]

    st.markdown(section(f"{len(pas)} ACTIVE PASSPORTS"), unsafe_allow_html=True)

    for p in pas:
        pid               = p["id"]
        is_editing        = pid in editing
        is_pending_delete = pid in pending_delete
        s  = get_supplier(p["supplier_id"])
        sn = s["name"] if s else "Unknown"

        with st.expander(f"{p['product_name']}  ·  {p['id']}  ·  {p['batch']}",
                          expanded=(is_editing or is_pending_delete)):

            # ── EDIT MODE ──────────────────────────────────
            if is_editing:
                sup_options      = {sp["name"]: sp["id"] for sp in vsup_all} if vsup_all \
                                   else {sn: p["supplier_id"]}
                current_sup_name = sn if sn in sup_options else list(sup_options.keys())[0]

                with st.form(f"edit_pp_{pid}"):
                    f1, f2 = st.columns(2)
                    pname_v  = f1.text_input("Product Name",         value=p["product_name"])
                    sku_v    = f2.text_input("SKU / Product Code",    value=p["sku"])
                    sch_v    = f1.selectbox("Supplier (verified)",    list(sup_options.keys()),
                                             index=list(sup_options.keys()).index(current_sup_name))
                    batch_v  = f2.text_input("Batch Number",          value=p["batch"])
                    origin_v = f1.text_input("Origin",                value=p["origin"])
                    certs_v  = st.multiselect("Certifications", PRODUCT_CERTS,
                                               default=p["certifications"])
                    carbon_v = st.number_input("Carbon Footprint (kg CO₂e)", 0.0, 10000.0,
                                                float(p["carbon_kg"]), 0.1)
                    sc1, sc2 = st.columns(2)
                    save   = sc1.form_submit_button("Save Changes", use_container_width=True)
                    cancel = sc2.form_submit_button("Cancel",       use_container_width=True)

                if save:
                    update_passport(pid, product_name=pname_v.strip(), sku=sku_v.strip(),
                                    supplier_id=sup_options[sch_v], batch=batch_v.strip(),
                                    origin=origin_v.strip(), certifications=certs_v,
                                    carbon_kg=carbon_v)
                    add_ledger_entry("PASSPORT_UPDATED", pid)
                    editing.discard(pid)
                    st.success(f"Passport {pid} updated and re-sealed on-chain.")
                    st.rerun()
                if cancel:
                    editing.discard(pid)
                    st.rerun()
                continue

            # ── READ-ONLY VIEW ─────────────────────────────
            eg   = s["esg_score"] if s else 0
            ec   = esg_color(eg)
            cert = " · ".join(p["certifications"]) if p["certifications"] else "None"

            c1, c2 = st.columns([3, 1.3])
            with c1:
                st.markdown(f"""
                <div style="margin-bottom:10px;">
                  <span class="badge badge-green">Active</span>
                  <span style="font-size:11px;color:#aab8b0;margin-left:10px;">
                    Issued {p["created"][:10]}
                  </span>
                </div>
                <div style="font-size:13px;color:#374151;line-height:1.9;">
                  <b>SKU:</b> {p["sku"]} &nbsp;·&nbsp; <b>Batch:</b> {p["batch"]}<br>
                  <b>Supplier:</b> {sn} &nbsp;·&nbsp;
                  <b>ESG:</b> <span style="color:{ec};font-weight:700;">{eg}/100</span><br>
                  <b>Origin:</b> {p["origin"]} &nbsp;·&nbsp;
                  <b>Manufactured:</b> {p["manufacture_date"]}<br>
                  <b>Carbon:</b> {p["carbon_kg"]} kg CO₂e<br>
                  <b>Certifications:</b> <span style="color:#1B5E35;">{cert}</span>
                </div>
                <div style="margin-top:10px;">
                  <span style="font-size:11px;color:#aab8b0;">Blockchain hash: </span>
                  <span class="hash-pill">{p["hash"]}</span>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                try:
                    buf = _qr_buf(pid)
                    st.image(buf, caption="Scan to verify", width=150)
                    buf.seek(0)
                    st.download_button("Download QR", data=buf.read(),
                                       file_name=f"TradeProof_{pid}.png", mime="image/png",
                                       key=f"dl_{pid}", use_container_width=True)
                except Exception as e:
                    st.caption(f"QR: {e}")

            st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

            # ── DELETE CONFIRMATION ────────────────────────
            if is_pending_delete:
                st.markdown(f"""
                <div style="background:#FDEAE3;border:1px solid #F6CBB9;border-radius:8px;
                            padding:10px 14px;margin-bottom:8px;font-size:12.5px;color:#7D4429;">
                  Remove passport <b>{pid}</b> and its journey history? This action is logged
                  on-chain and cannot be undone.
                </div>
                """, unsafe_allow_html=True)
                dc1, dc2 = st.columns(2)
                if dc1.button("Confirm Delete", key=f"confirmdel_{pid}", use_container_width=True):
                    delete_passport(pid)
                    add_ledger_entry("PASSPORT_REMOVED", pid)
                    pending_delete.discard(pid)
                    st.success(f"Passport {pid} removed.")
                    st.rerun()
                if dc2.button("Cancel", key=f"canceldel_{pid}", use_container_width=True):
                    pending_delete.discard(pid)
                    st.rerun()
            else:
                ac1, ac2 = st.columns(2)
                if ac1.button("Edit",   key=f"edit_{pid}", use_container_width=True):
                    editing.add(pid)
                    st.rerun()
                if ac2.button("Delete", key=f"del_{pid}",  use_container_width=True):
                    pending_delete.add(pid)
                    st.rerun()

    # ── Issue new passport ─────────────────────────────────
    st.markdown(section("ISSUE NEW PASSPORT"), unsafe_allow_html=True)
    vsup = [s for s in sup if s["status"] == "Verified"]
    if not vsup:
        st.warning("You need at least one verified supplier first — go to Suppliers.")
        return

    with st.form("pp_form", clear_on_submit=True):
        f1, f2 = st.columns(2)
        pname  = f1.text_input("Product Name *")
        sku    = f2.text_input("SKU / Product Code *")
        sopts  = {s["name"]: s["id"] for s in vsup}
        sch    = f1.selectbox("Supplier (verified) *", list(sopts.keys()))
        batch  = f2.text_input("Batch Number", value=f"BATCH-{short_id()}")
        origin = f1.text_input("Origin (farm / factory)")
        mdate  = f2.date_input("Manufacture Date")
        certs  = st.multiselect("Product Certifications", PRODUCT_CERTS)
        carbon = st.number_input("Carbon Footprint (kg CO₂e)", 0.0, 10000.0, 1.0, 0.1)

        if st.form_submit_button("Issue Passport", use_container_width=True):
            if not pname.strip() or not sku.strip():
                st.error("Product name and SKU are required.")
            else:
                nid = f"PP-{short_id()}"
                np  = {
                    "id": nid, "product_name": pname.strip(), "sku": sku.strip(),
                    "supplier_id": sopts[sch], "batch": batch.strip(),
                    "origin": origin.strip(), "manufacture_date": str(mdate),
                    "certifications": certs, "carbon_kg": carbon,
                    "status": "Active", "created": now_ts(),
                }
                np["hash"] = make_hash(np)
                st.session_state.passports.append(np)
                add_ledger_entry("PASSPORT_CREATE", nid)
                st.success(f"Passport **{nid}** issued and recorded on blockchain.")
                try:
                    buf = _qr_buf(nid)
                    buf.seek(0)
                    st.image(buf, width=150, caption="QR Code — scan to verify")
                    buf.seek(0)
                    st.download_button("Download QR Code", data=buf.read(),
                                       file_name=f"TradeProof_{nid}.png", mime="image/png")
                except Exception:
                    pass
                st.rerun()
