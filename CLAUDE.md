# Renta -- Project Instructions

## Overview

International rental property investment calculator at `ethanpease.com/apps/renta`. Compares buying rental property abroad vs investing in the stock market, with full cross-border tax modeling (US-Spain focus, extensible to other countries).

## Current Version

**v0.4.0** -- displayed in the footer of index.html

## Version Numbering

Uses 3-part `MAJOR.MINOR.PATCH`:
- MAJOR: fundamental redesign or new calculation engine
- MINOR: new features (new inputs, new export capabilities, new sections)
- PATCH: bug fixes, label changes, style tweaks

**On every deploy, you MUST:**
1. Bump the version in `index.html` footer (`v0.X.X` in the `<footer>` section)
2. Update `Current Version` in this file to match
3. Include the version in the git commit message

## Tech Stack

- Single-page HTML/CSS/JS app (no framework)
- Chart.js for visualizations
- SheetJS (xlsx) for spreadsheet export with formulas
- FastAPI micro-endpoint for feedback collection
- Python container on Cloud Run
- Warm International Investment color theme (cream/amber/sage/terracotta, Nunito font)

## Deploy

```bash
./deploy.sh
```

Deploys to Cloud Run service `friends-renta` in GCP project, region `us-west1`.
Firebase Hosting routes `ethanpease.com/apps/renta` to this service.
Deploy script auto-registers in the site manifest (GCS).

## Key Patterns

- All financial calculations run client-side in JS
- Tax rates are constants at top of the calculation engine section
- Every user-facing number must show currency label (EUR/USD)
- Every tax/financial concept must have an ELI5 tooltip
- Feedback POSTs to `/apps/renta/api/feedback` (FastAPI), stored in GCS (`gs://ethanpease-site-manifest/renta-feedback.jsonl`)
- User settings persisted to localStorage, restored on page load
- Spreadsheet export generates .xlsx with full cell formulas (SheetJS), not flat values

## Input Modes

- **Rental Strategy** (top-level): Long-term, Short-term/Airbnb, Mid-term
  - Long-term: monthly rent + occupancy % slider (default 90%, 10% mgmt)
  - Airbnb: nightly rate + nights/year (default 95 EUR, 220 nights, 25% mgmt)
  - Mid-term: monthly rent + occupancy % slider (default 80%, 15% mgmt)
- **Mortgage**: "With mortgage" or "No mortgage (cash purchase)" -- sets LTV to 0
- **Investment comparison**: Auto (from down payment/mortgage) or Manual override
- **Tax residency**: auto-fills bracket/MAGI/filing defaults per profile

## Pitfalls

- IRNR for non-EU residents: 24% on GROSS rent, no expense deductions
- NIIT (3.8%) cannot be offset by foreign tax credits -- separate tax under IRC 1411
- Depreciation for foreign property uses 30-year ADS, not 27.5-year standard
- Cadastral value is typically 30-50% of market value, not the purchase price
- Cloud Run containers are ephemeral -- feedback persists to GCS, not local disk
