"""
data.py — State management & blockchain simulation for TradeProof v8
"""
import hashlib, datetime, uuid
import streamlit as st


# ── Blockchain helpers ────────────────────────────────────

def make_hash(data: dict) -> str:
    raw = str(sorted(data.items())).encode()
    return "0x" + hashlib.sha256(raw).hexdigest()[:40]


def now_ts() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def short_id() -> str:
    return str(uuid.uuid4())[:8].upper()


# ── Blockchain ledger chaining ────────────────────────────

GENESIS_HASH = "0" * 40


def _chain_hash(block_num, type_, id_, ts, prev_hash):
    return make_hash({"block": block_num, "type": type_, "id": id_,
                      "ts": ts, "prev_hash": prev_hash})


# ── Realistic SA seed data ────────────────────────────────
# These are real companies from TradeProof's Target 50 list.
# Using them as demo data makes the prototype instantly credible
# to any SA audience — they'll recognise these names.

SEED_SUPPLIERS = [
    {
        "id": "SUP-001",
        "name": "Reyneke Wines",
        "location": "Stellenbosch, Western Cape",
        "category": "Wine & Viticulture",
        "certifications": ["WIETA", "IPW", "Fairtrade International",
                           "Demeter", "EU Organic", "WWF Conservation Champion"],
        "esg_score": 94,
        "tax_status": "Compliant",
        "cipc_status": "Active",
        "status": "Verified",
        "registered": "2024-01-08 09:00:00",
    },
    {
        "id": "SUP-002",
        "name": "Carmién Tea",
        "location": "Citrusdal, Western Cape",
        "category": "Rooibos & Tea",
        "certifications": ["EU Organic", "USDA Organic",
                           "Fairtrade International", "Ecocert", "SIZA"],
        "esg_score": 89,
        "tax_status": "Compliant",
        "cipc_status": "Active",
        "status": "Verified",
        "registered": "2024-01-15 10:30:00",
    },
    {
        "id": "SUP-003",
        "name": "TSHEPO Jeans",
        "location": "Johannesburg, Gauteng",
        "category": "Fashion & Apparel",
        "certifications": ["GOTS", "OEKO-TEX Standard 100",
                           "BBBEE Level 1", "B-Corp"],
        "esg_score": 82,
        "tax_status": "Compliant",
        "cipc_status": "Active",
        "status": "Verified",
        "registered": "2024-02-01 08:45:00",
    },
    {
        "id": "SUP-004",
        "name": "Hey Gorgeous",
        "location": "Cape Town, Western Cape",
        "category": "Cosmetics & Beauty",
        "certifications": ["COSMOS Organic", "Cruelty-Free International",
                           "Leaping Bunny", "Vegan Society", "Ecocert"],
        "esg_score": 87,
        "tax_status": "Compliant",
        "cipc_status": "Active",
        "status": "Verified",
        "registered": "2024-02-14 11:00:00",
    },
    # Pending application — for live Verify / Decline demo during presentation
    {
        "id": "SUP-005",
        "name": "Sundays River Citrus Co.",
        "location": "Kirkwood, Eastern Cape",
        "category": "Citrus & Fresh Produce",
        "certifications": ["GlobalGAP", "SIZA", "PPECB", "BRC Global Standard"],
        "esg_score": 76,
        "tax_status": "Compliant",
        "cipc_status": "Active",
        "status": "Pending",
        "registered": "2024-03-01 09:30:00",
    },
]

SEED_PASSPORTS = [
    {
        "id": "PP-001",
        "product_name": "Reyneke Organic Syrah 2022",
        "sku": "RW-SYR-22",
        "supplier_id": "SUP-001",
        "batch": "BATCH-2024-RW01",
        "origin": "Stellenbosch Wine of Origin, Western Cape",
        "manufacture_date": "2022-04-15",
        "certifications": ["EU Organic", "Fairtrade International", "Demeter"],
        "carbon_kg": 1.4,
        "status": "Active",
        "created": "2024-03-05 09:00:00",
    },
    {
        "id": "PP-002",
        "product_name": "Carmién Rooibos Green 40 Bags",
        "sku": "CT-RG-40B",
        "supplier_id": "SUP-002",
        "batch": "BATCH-2024-CT02",
        "origin": "Cederberg / Citrusdal, Western Cape",
        "manufacture_date": "2024-02-10",
        "certifications": ["EU Organic", "USDA Organic", "Fairtrade International"],
        "carbon_kg": 0.3,
        "status": "Active",
        "created": "2024-02-22 14:00:00",
    },
    {
        "id": "PP-003",
        "product_name": "TSHEPO The Joburg Jean - Slim",
        "sku": "TSH-JB-SLM",
        "supplier_id": "SUP-003",
        "batch": "BATCH-2024-TSH03",
        "origin": "Johannesburg, Gauteng",
        "manufacture_date": "2024-01-20",
        "certifications": ["GOTS", "OEKO-TEX Standard 100"],
        "carbon_kg": 8.2,
        "status": "Active",
        "created": "2024-02-01 08:00:00",
    },
    {
        "id": "PP-004",
        "product_name": "Hey Gorgeous Rose Hip Face Oil 30ml",
        "sku": "HG-RH-30",
        "supplier_id": "SUP-004",
        "batch": "BATCH-2024-HG04",
        "origin": "Cape Town, Western Cape",
        "manufacture_date": "2024-03-05",
        "certifications": ["COSMOS Organic", "Cruelty-Free International", "Vegan Society"],
        "carbon_kg": 0.2,
        "status": "Active",
        "created": "2024-03-12 10:00:00",
    },
]

SEED_JOURNEYS = [
    {
        "passport_id": "PP-001",
        "milestones": [
            {"stage": "Grapes Harvested",      "location": "Reyneke Estate, Stellenbosch", "ts": "2022-04-02 06:00", "verified": True},
            {"stage": "Fermentation",           "location": "Reyneke Cellar, Stellenbosch", "ts": "2022-04-10 10:00", "verified": True},
            {"stage": "Barrel Maturation",      "location": "Reyneke Cellar, Stellenbosch", "ts": "2022-06-01 08:00", "verified": True},
            {"stage": "Bottling",               "location": "Stellenbosch Bottling Co.",    "ts": "2022-11-20 09:00", "verified": True},
            {"stage": "Quality & Lab Tested",   "location": "Wineland Lab, Paarl",          "ts": "2022-12-01 11:00", "verified": True},
            {"stage": "Dispatched for Export",  "location": "Cape Town Port",               "ts": "2024-03-06 05:00", "verified": True},
            {"stage": "Delivered — EU Buyer",   "location": "Rotterdam, Netherlands",       "ts": "2024-03-22 14:00", "verified": True},
        ]
    },
    {
        "passport_id": "PP-002",
        "milestones": [
            {"stage": "Rooibos Harvested",      "location": "Cederberg Mountains, WC",     "ts": "2024-01-15 06:00", "verified": True},
            {"stage": "Sun-Dried & Fermented",  "location": "Carmién Farm, Citrusdal",     "ts": "2024-01-20 08:00", "verified": True},
            {"stage": "Graded & Blended",       "location": "Carmién Processing, Citrusdal","ts": "2024-02-01 10:00", "verified": True},
            {"stage": "Packaged",               "location": "Carmién Factory, Citrusdal",  "ts": "2024-02-10 08:00", "verified": True},
            {"stage": "Quality Checked",        "location": "SGS Lab, Cape Town",          "ts": "2024-02-12 13:00", "verified": True},
            {"stage": "Dispatched",             "location": "Cape Town Depot",             "ts": "2024-02-22 07:00", "verified": True},
            {"stage": "Delivered to Retailer",  "location": "Johannesburg DC",             "ts": "2024-02-25 10:00", "verified": True},
        ]
    },
    {
        "passport_id": "PP-003",
        "milestones": [
            {"stage": "Organic Cotton Sourced", "location": "GOTS-Certified Mill, India",  "ts": "2024-01-05 08:00", "verified": True},
            {"stage": "Fabric Cut & Sewn",      "location": "TSHEPO Studio, Joburg",       "ts": "2024-01-18 09:00", "verified": True},
            {"stage": "Quality Inspection",     "location": "TSHEPO QC, Joburg",           "ts": "2024-01-20 14:00", "verified": True},
            {"stage": "Tagged & Packaged",      "location": "TSHEPO Warehouse, Joburg",    "ts": "2024-01-21 08:00", "verified": True},
            {"stage": "Dispatched",             "location": "Joburg Distribution Centre",  "ts": "2024-02-01 07:00", "verified": True},
            {"stage": "Delivered to Store",     "location": "TSHEPO Sandton, Joburg",      "ts": "2024-02-02 10:00", "verified": True},
        ]
    },
    {
        "passport_id": "PP-004",
        "milestones": [
            {"stage": "Rose Hip Oil Sourced",   "location": "Organic Farm, Overberg WC",   "ts": "2024-02-20 07:00", "verified": True},
            {"stage": "Cold-Pressed",           "location": "Hey Gorgeous Lab, Cape Town", "ts": "2024-03-01 09:00", "verified": True},
            {"stage": "Formulated & Blended",   "location": "Hey Gorgeous Lab, Cape Town", "ts": "2024-03-03 10:00", "verified": True},
            {"stage": "Safety & Stability Test","location": "Intertek Lab, Cape Town",     "ts": "2024-03-04 13:00", "verified": True},
            {"stage": "Bottled & Labelled",     "location": "Hey Gorgeous Factory, CT",    "ts": "2024-03-05 08:00", "verified": True},
            {"stage": "Dispatched",             "location": "CT Distribution Centre",      "ts": "2024-03-12 06:00", "verified": True},
            {"stage": "Delivered to Retailer",  "location": "Joburg DC",                  "ts": "2024-03-14 11:00", "verified": True},
        ]
    },
]


# ── Session state init ─────────────────────────────────────

def init_state():
    if "suppliers" not in st.session_state:
        suppliers = []
        for s in SEED_SUPPLIERS:
            s = s.copy()
            s["hash"] = make_hash(s)
            suppliers.append(s)
        st.session_state.suppliers = suppliers

    if "passports" not in st.session_state:
        passports = []
        for p in SEED_PASSPORTS:
            p = p.copy()
            p["hash"] = make_hash(p)
            passports.append(p)
        st.session_state.passports = passports

    if "journeys" not in st.session_state:
        journeys = []
        for j in SEED_JOURNEYS:
            j = j.copy()
            j["hash"] = make_hash(j)
            journeys.append(j)
        st.session_state.journeys = journeys

    if "ledger" not in st.session_state:
        seed_events = [
            ("SUPPLIER_REG",      "SUP-001", "2024-01-08 09:00:00"),
            ("SUPPLIER_VERIFIED", "SUP-001", "2024-01-09 10:00:00"),
            ("SUPPLIER_REG",      "SUP-002", "2024-01-15 10:30:00"),
            ("SUPPLIER_VERIFIED", "SUP-002", "2024-01-16 11:00:00"),
            ("SUPPLIER_REG",      "SUP-003", "2024-02-01 08:45:00"),
            ("SUPPLIER_VERIFIED", "SUP-003", "2024-02-02 09:00:00"),
            ("SUPPLIER_REG",      "SUP-004", "2024-02-14 11:00:00"),
            ("SUPPLIER_VERIFIED", "SUP-004", "2024-02-15 09:00:00"),
            ("SUPPLIER_REG",      "SUP-005", "2024-03-01 09:30:00"),  # pending
            ("PASSPORT_CREATE",   "PP-001",  "2024-03-05 09:00:00"),
            ("PASSPORT_CREATE",   "PP-002",  "2024-02-22 14:00:00"),
            ("PASSPORT_CREATE",   "PP-003",  "2024-02-01 08:00:00"),
            ("PASSPORT_CREATE",   "PP-004",  "2024-03-12 10:00:00"),
            ("JOURNEY_LOG",       "PP-001",  "2024-03-06 09:00:00"),
            ("JOURNEY_LOG",       "PP-002",  "2024-02-25 10:00:00"),
            ("JOURNEY_LOG",       "PP-003",  "2024-02-02 10:00:00"),
            ("JOURNEY_LOG",       "PP-004",  "2024-03-14 11:00:00"),
        ]
        ledger, prev_hash = [], GENESIS_HASH
        for i, (type_, id_, ts) in enumerate(seed_events, start=1):
            h = _chain_hash(i, type_, id_, ts, prev_hash)
            ledger.append({"block": i, "type": type_, "id": id_, "ts": ts,
                           "prev_hash": prev_hash, "hash": h})
            prev_hash = h
        st.session_state.ledger = ledger

    if "editing_ids" not in st.session_state:
        st.session_state.editing_ids = set()
    if "pending_delete_ids" not in st.session_state:
        st.session_state.pending_delete_ids = set()


def reset_demo():
    """Wipe session state and reload seed data — one-click demo recovery."""
    for key in ["suppliers", "passports", "journeys", "ledger",
                "editing_ids", "pending_delete_ids"]:
        if key in st.session_state:
            del st.session_state[key]
    init_state()


# ── Getters ───────────────────────────────────────────────

def get_supplier(supplier_id):
    return next((s for s in st.session_state.suppliers if s["id"] == supplier_id), None)


def get_passport(passport_id):
    return next((p for p in st.session_state.passports if p["id"] == passport_id), None)


def get_journey(passport_id):
    return next((j for j in st.session_state.journeys if j["passport_id"] == passport_id), None)


# ── Ledger ────────────────────────────────────────────────

def add_ledger_entry(type_, id_):
    blocks = st.session_state.ledger
    next_block = (blocks[-1]["block"] + 1) if blocks else 1
    prev_hash  = blocks[-1]["hash"] if blocks else GENESIS_HASH
    ts = now_ts()
    entry = {
        "block": next_block, "type": type_, "id": id_, "ts": ts,
        "prev_hash": prev_hash,
        "hash": _chain_hash(next_block, type_, id_, ts, prev_hash),
    }
    st.session_state.ledger.append(entry)
    return entry


def verify_chain():
    blocks = st.session_state.ledger
    prev_hash = GENESIS_HASH
    for b in blocks:
        expected = _chain_hash(b["block"], b["type"], b["id"], b["ts"], prev_hash)
        if b.get("prev_hash") != prev_hash or b["hash"] != expected:
            return False, b["block"]
        prev_hash = b["hash"]
    return True, None


# ── Edit / delete helpers ─────────────────────────────────

def update_supplier(supplier_id, **fields):
    idx = next((i for i, s in enumerate(st.session_state.suppliers)
                if s["id"] == supplier_id), None)
    if idx is None:
        return None
    st.session_state.suppliers[idx].update(fields)
    st.session_state.suppliers[idx]["hash"] = make_hash(st.session_state.suppliers[idx])
    return st.session_state.suppliers[idx]


def delete_supplier(supplier_id):
    st.session_state.suppliers = [s for s in st.session_state.suppliers
                                   if s["id"] != supplier_id]


def update_passport(passport_id, **fields):
    idx = next((i for i, p in enumerate(st.session_state.passports)
                if p["id"] == passport_id), None)
    if idx is None:
        return None
    st.session_state.passports[idx].update(fields)
    st.session_state.passports[idx]["hash"] = make_hash(st.session_state.passports[idx])
    return st.session_state.passports[idx]


def delete_passport(passport_id):
    st.session_state.passports = [p for p in st.session_state.passports
                                   if p["id"] != passport_id]
    st.session_state.journeys  = [j for j in st.session_state.journeys
                                   if j["passport_id"] != passport_id]


def update_milestone(passport_id, index, **fields):
    j = get_journey(passport_id)
    if not j or not (0 <= index < len(j["milestones"])):
        return
    j["milestones"][index].update(fields)
    j["hash"] = make_hash(j)


def delete_milestone(passport_id, index):
    j = get_journey(passport_id)
    if not j or not (0 <= index < len(j["milestones"])):
        return
    j["milestones"].pop(index)
    j["hash"] = make_hash(j)
