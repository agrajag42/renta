# Renta -- Architecture

## System Design

```
Browser (index.html)
  |
  |-- All calculations: client-side JS
  |-- Charts: Chart.js
  |-- Currency rates: fetched on load from exchangerate-api (fallback: hardcoded)
  |
  |-- POST /friends/renta/api/feedback --> nginx proxy --> FastAPI (port 8081)
  |                                                          |
  |                                                          +--> stdout (JSON line)
  |                                                          +--> Cloud Logging
  |
  +-- Static assets served by nginx from /friends/renta/
```

## Container Architecture

Single Docker container running two processes:
1. **nginx** (port 8080) -- serves static files, proxies /api/* to FastAPI
2. **uvicorn** (port 8081) -- FastAPI feedback endpoint

`start.sh` launches both processes. nginx is the primary listener (Cloud Run routes to 8080).

## Key Decisions

- **No database:** Feedback is appended as JSON lines to stdout, captured by Cloud Logging. This avoids managing persistent storage on ephemeral Cloud Run containers.
- **Client-side calculation:** All tax math runs in the browser for instant reactivity. No server round-trips for calculations.
- **Single HTML file:** Keeps deployment simple and matches the-ledger pattern. All CSS and JS are inline.
- **Currency switching:** EUR is primary. USD shown as secondary. Exchange rate fetched once on page load with sensible fallback.

## Tax Engine Design

The calculation engine models two parallel timelines over N years:

**Property Timeline:**
- Year 0: Purchase price + closing costs (ITP/IVA, notary, registry, lawyer, gestor)
- Each year: Gross rent * occupancy - Spanish taxes - operating costs - mortgage payments + equity buildup + appreciation
- Sale year: Sale price - capital gains tax (ES + US) - 3% retention - plusvalia

**Market Timeline:**
- Year 0: Lump sum investment (= property down payment + closing costs)
- Each year: Previous balance * (1 + return rate) + monthly contributions * 12 - capital gains tax on withdrawals

**Breakeven:** The year where property cumulative net worth exceeds market cumulative net worth.
