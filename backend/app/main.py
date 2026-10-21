"""FastAPI application.

Run from the project root:  uvicorn backend.app.main:app --reload --port 8000
"""
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .engine import HAZARDS, REGIONS, build_world, simulate

app = FastAPI(title="ResilientChain API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"],
                   allow_methods=["GET"], allow_headers=["*"])

WORLD = build_world()
HazardName = Literal["flood", "heatwave", "drought", "port_strike"]
RegionName = Literal[tuple(REGIONS)]  # type: ignore[valid-type]


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/meta")
def meta():
    return {"hazards": {k: v["label"] for k, v in HAZARDS.items()}, "regions": list(REGIONS)}


@app.get("/api/simulate")
def run_simulation(
    hazard: HazardName = "flood",
    region: RegionName = "Kochi",
    severity: float = Query(0.7, ge=0.0, le=1.0),
    boost: float = Query(0.0, ge=0.0, le=0.4, description="Digital adoption uplift (0-0.4)"),
):
    return simulate(WORLD, hazard, region, severity, boost)


# Serve the production frontend build (npm run build) if it exists.
DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if DIST.exists():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str):
        file = DIST / path
        return FileResponse(file if path and file.is_file() else DIST / "index.html")
