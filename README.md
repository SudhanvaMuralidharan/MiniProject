# ResilientChain

**Problem statement:** Economic growth is constrained by fragile supply chains, climate pressures, and uneven digital adoption. Design sustainable, tech-enabled systems that create resilient industries and secure, future-ready jobs.

ResilientChain is a decision-support tool for regional planners and MSME clusters. It stress-tests a manufacturing network against climate and logistics shocks and shows how much of the damage, especially to jobs, can be avoided.

## Project structure

```
resilientchain/
├── package.json          # single Node manifest (React, Vite, scripts)
├── vite.config.js        # Vite root = frontend/, proxies /api -> :8000
├── requirements.txt      # Python dependencies
├── pytest.ini
├── backend/              # FastAPI service
│   ├── app/
│   │   ├── main.py       # routes, validation, serves frontend build
│   │   └── engine.py     # risk model, simulation, mitigation, reskilling
│   └── tests/
│       └── test_engine.py
└── frontend/             # React + Vite single-page app
    ├── index.html
    └── src/
        ├── main.jsx, App.jsx, api.js, useSimulation.js, styles.css
        └── components/   # Controls, KpiCards, RegionMap, FirmTable, Recommendations, Reskilling
```

## How it maps to the problem

| Challenge | What the project does |
|---|---|
| Fragile supply chains | Scores each firm on supplier concentration (HHI), geographic concentration and buffer stock. Recommends supplier rebalancing to unaffected regions. |
| Climate pressures | Simulates flood, heatwave, drought and port-strike shocks with distance-decayed spillover across 10 industrial regions. |
| Uneven digital adoption | A "digital uplift" slider shows how higher digital readiness cuts supplier and firm losses. Low-digital regions are visible on the map. |
| Secure, future-ready jobs | Converts output loss into jobs at risk, then maps affected workers to sector-specific reskilling pathways. |

## Setup

Requires Node 18+ and Python 3.9+.

```bash
npm install
python -m venv .venv && source .venv/bin/activate    # optional but recommended
pip install -r requirements.txt
```

## Run

| Goal | Command |
|---|---|
| Development (hot reload) | `npm run dev:all` -> open http://localhost:5173 |
| Backend only | `npm run dev:api` (API docs at http://localhost:8000/docs) |
| Frontend only | `npm run dev` (needs the backend running) |
| Production-style (single port) | `npm start` -> http://localhost:8000 |
| Backend tests | `npm run test:api` |

## API

- `GET /api/meta` – available hazards and regions.
- `GET /api/simulate?hazard=flood&region=Kochi&severity=0.7&boost=0.1` – scenario results. Inputs are validated (422 on bad values).
- `GET /api/health`

## Demo script

1. Flood at **Kochi**, severity 70%: note jobs at risk with no action.
2. Compare with the rebalanced figure and read the supplier moves.
3. Raise **digital uplift** to +20 pts and watch both numbers fall.
4. Switch to **Port strike** at Chennai to show a logistics shock.
5. Show the reskilling list for workers still at risk.

## Model summary

- Regional impact = severity × hazard exposure × exp(−distance / hazard scale).
- Supplier loss = regional impact × (1.25 − 0.7 × digital readiness).
- Firm output loss = worst input shortfall, reduced by buffer days ÷ disruption length, or own-site loss if larger.
- Jobs at risk = workforce × output loss × 0.7.
- Mitigation shifts up to 50% of volume from hit suppliers to the fastest unaffected alternate.

## Data note and next steps

All data is synthetic (seeded, reproducible). Coefficients are illustrative, not calibrated.

To make it real: plug in actual supplier/GST/e-way-bill data, IMD and flood-hazard layers, district employment data (PLFS), and the Skill India course catalogue. Further ideas: cost of mitigation, multi-hazard scenarios, a worker-side app for skill matching.
