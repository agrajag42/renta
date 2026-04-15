# Renta -- Requirements

## Core Requirements

1. **Property vs Market Comparison:** Show breakeven year for rental property investment vs stock market, accounting for all taxes, costs, and returns.

2. **Cross-Border Tax Modeling:** Accurately model US-Spain dual taxation including IRNR, IBI, Schedule E, Foreign Tax Credits, NIIT, depreciation, and capital gains.

3. **ELI5 Education:** Every tax concept, input field, and financial term must have a plain-language explanation accessible via tooltip/expandable card.

4. **Currency Handling:** All monetary values labeled with currency. EUR/USD switcher with live exchange rate. Values shown in both currencies.

5. **Flexible Inputs:** User can adjust all parameters. Auto-calculated values (closing costs, tax amounts) can be overridden.

6. **Visual Style:** Candy Pastel theme -- soft gradients, rounded cards, playful animations, approachable and non-intimidating.

7. **Mobile Responsive:** Must work well on phones (friends/family will share links).

8. **Feedback System:** Users can submit text feedback from the page. Feedback is stored and readable by the developer.

## Input Parameters

### Property
- Purchase price (EUR)
- Region (autonomous community -- affects ITP rate)
- New-build vs resale
- Monthly rent
- Rental type (long-term / short-term / mid-term)
- Occupancy rate
- Management fee %
- Mortgage (optional): LTV, interest rate, term
- Maintenance reserve %
- Community fees
- Insurance estimate
- Annual appreciation rate

### Alternative Investment
- Initial lump sum
- Monthly contribution
- Investment vehicle (S&P 500, World Stock, 60/40, HYSA, Custom)
- Expected annual return
- Capital gains tax rate

### Tax Profile
- Tax residency (US abroad, US domestic, EU/EEA, Other non-EU)
- US marginal tax bracket
- US MAGI (for NIIT)
- Building/land allocation % (for depreciation)

## Output

- Breakeven year (hero number)
- Wealth projection chart (property vs market over 1-30 years)
- Stat pills: breakeven, 15yr advantage, net yield, tax drag, cash-on-cash
- Tax breakdown by country with ELI5 explanations
- Annual cashflow table

## Non-Requirements (Out of Scope for v1)

- Multi-property comparison
- Historical backtesting with real market data
- User accounts / saving scenarios
- PDF export
- Multiple country tax engines (Spain only for v1, architecture should allow extension)
