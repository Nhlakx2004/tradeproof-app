# TradeProof (Pty) Ltd — v8.1
**Blockchain traceability for South African supply chains.**

## Run the App
```bash
pip install streamlit plotly qrcode pillow reportlab
python -m streamlit run app.py
```

## What's New in v8

### Demo data — real SA companies
Seed suppliers are now real brands from TradeProof's Target 50:
- **Reyneke Wines** (Stellenbosch) — Demeter, Fairtrade, EU Organic, WWF Champion
- **Carmién Tea** (Citrusdal) — USDA Organic, EU Organic, Fairtrade, Ecocert
- **TSHEPO Jeans** (Johannesburg) — GOTS, OEKO-TEX Standard 100, BBBEE Level 1, B-Corp
- **Hey Gorgeous** (Cape Town) — COSMOS Organic, Leaping Bunny, Cruelty-Free International
- **Sundays River Citrus Co.** (Kirkwood) — Pending, for live Verify/Decline demo

### Verify + Decline supplier applications
Pending suppliers now show two buttons side-by-side: **Verify Supplier** and
**Decline Application**. Both actions are sealed on-chain and appear in the ledger.
Perfect for a live presentation demo.

### Grouped real certifications (46 options)
All certifications are real, independently verifiable bodies — grouped into 8 categories:
South Africa, Food Safety, Organic & Natural, Ethical Trade, Textile & Fashion,
Cosmetics, Management Systems, ESG & Corporate.

### Fixed QR code URL
QR codes now point to `localhost:8501/verify/[ID]` — scannable in the room during demo.
Change `QR_BASE_URL` in `pages/passports.py` to `https://tradeproof.co.za/verify/` for production.

### Pending applications alert
Dashboard and Suppliers page both show a yellow alert banner when applications are waiting.

### Pending applications KPI
Dashboard now shows a dedicated "Pending Applications" metric alongside Verified count.

### Demo Reset button
Dashboard has a "Reset Demo Data" button (under Demo Tools) — one click restores all
seed suppliers, passports, and journeys if anything goes wrong mid-presentation.

### SA-relevant supplier categories
Categories now match your actual target market: Wine & Viticulture, Rooibos & Tea,
Citrus & Fresh Produce, Macadamia & Nuts, Fashion & Apparel, Cosmetics & Beauty, etc.

## Pages
- **Dashboard** — KPIs + pending alert + charts + blockchain integrity + demo reset
- **Suppliers** — grouped cert picker, Verify/Decline buttons, Declined status
- **Product Passports** — issue/edit/delete, real product certs, QR → localhost
- **Journey Tracker** — log milestones, remove individually
- **Verify Product** — consumer-facing scan simulation
- **ESG Report** — per-supplier PDF export
