# Renta -- Project Instructions

## Overview

International rental property investment calculator at `ethanpease.com/friends/renta`. Compares buying rental property abroad vs investing in the stock market, with full cross-border tax modeling (US-Spain focus, extensible to other countries).

## Tech Stack

- Single-page HTML/CSS/JS app (no framework)
- Chart.js for visualizations
- FastAPI micro-endpoint for feedback collection
- nginx:alpine + Python container on Cloud Run
- Candy Pastel visual theme (Nunito font, lavender/peach/mint palette)

## Deploy

```bash
./deploy.sh
```

Deploys to Cloud Run service `friends-renta` in GCP project `punchline-ethan-20260308`, region `us-west1`.

## Key Patterns

- All financial calculations run client-side in JS
- Tax rates are constants at top of the calculation engine section
- Every user-facing number must show currency label (EUR/USD)
- Every tax/financial concept must have an ELI5 tooltip
- Feedback POSTs to `/friends/renta/api/feedback` (FastAPI on port 8081, proxied by nginx)

## Pitfalls

- IRNR for non-EU residents: 24% on GROSS rent, no expense deductions
- NIIT (3.8%) cannot be offset by foreign tax credits -- separate tax under IRC 1411
- Depreciation for foreign property uses 30-year ADS, not 27.5-year standard
- Cadastral value is typically 30-50% of market value, not the purchase price
- Cloud Run containers are ephemeral -- feedback.json must be logged to stdout for persistence via Cloud Logging
