"""ResilientChain simulation engine (pure standard library).

Models a regional MSME manufacturing network and answers:
  * How resilient is each firm today? (concentration, climate, digital, buffers)
  * What happens to output, revenue and JOBS under a climate / logistics shock?
  * How much does supplier rebalancing and digital uplift reduce the damage?
  * Which future-ready reskilling pathways protect the workers at risk?
"""
import math
import random

REGIONS = {
    #               flood heat  drought port(dist, 0=at port) digital lat    lon
    "Bengaluru":  dict(flood=.35, heat=.40, drought=.30, port=.55, digital=.88, lat=12.97, lon=77.59),
    "Coimbatore": dict(flood=.25, heat=.45, drought=.50, port=.50, digital=.66, lat=11.02, lon=76.96),
    "Pune":       dict(flood=.40, heat=.50, drought=.45, port=.35, digital=.80, lat=18.52, lon=73.86),
    "Surat":      dict(flood=.70, heat=.60, drought=.35, port=.15, digital=.70, lat=21.17, lon=72.83),
    "Ludhiana":   dict(flood=.45, heat=.75, drought=.40, port=.90, digital=.55, lat=30.90, lon=75.85),
    "Kolkata":    dict(flood=.75, heat=.55, drought=.25, port=.10, digital=.62, lat=22.57, lon=88.36),
    "Chennai":    dict(flood=.65, heat=.65, drought=.45, port=.05, digital=.78, lat=13.08, lon=80.27),
    "Hyderabad":  dict(flood=.35, heat=.65, drought=.55, port=.60, digital=.84, lat=17.39, lon=78.49),
    "Nagpur":     dict(flood=.30, heat=.80, drought=.65, port=.80, digital=.48, lat=21.15, lon=79.09),
    "Kochi":      dict(flood=.80, heat=.35, drought=.15, port=.05, digital=.58, lat=9.93,  lon=76.27),
}

HAZARDS = {
    "flood":       dict(key="flood",   scale_km=300,  label="Flood"),
    "heatwave":    dict(key="heat",    scale_km=600,  label="Heatwave"),
    "drought":     dict(key="drought", scale_km=800,  label="Drought"),
    "port_strike": dict(key=None,      scale_km=1500, label="Port / logistics strike"),
}

SECTORS = {
    "Textiles":        ["cotton yarn", "dyes", "packaging"],
    "Electronics":     ["PCBs", "semiconductors", "packaging"],
    "Food Processing": ["raw produce", "packaging", "cold storage"],
    "Auto Components": ["steel", "castings", "semiconductors"],
}

# Future-ready pathways for workers displaced / at risk, per sector.
PATHWAYS = {
    "Textiles":        ("Dye-process automation & sustainable textile technician", 12),
    "Electronics":     ("SMT operator -> Industrial IoT / test-automation technician", 14),
    "Food Processing": ("Cold-chain & traceability data analyst", 10),
    "Auto Components": ("CNC programmer / EV-component quality specialist", 16),
}

FIRMS = [
    ("Kaveri Weaves", "Textiles", "Coimbatore"), ("Surat Dyeworks", "Textiles", "Surat"),
    ("Eastern Fabrics", "Textiles", "Kolkata"), ("NanoBoard Systems", "Electronics", "Bengaluru"),
    ("Deccan Circuits", "Electronics", "Hyderabad"), ("Pune Assemblies", "Electronics", "Pune"),
    ("Malabar Foods", "Food Processing", "Kochi"), ("Punjab Agro Pack", "Food Processing", "Ludhiana"),
    ("Orange City Cold Chain", "Food Processing", "Nagpur"), ("Chennai Castings", "Auto Components", "Chennai"),
    ("Pune Precision", "Auto Components", "Pune"), ("Ludhiana Forge", "Auto Components", "Ludhiana"),
]


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def haversine_km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a["lat"], a["lon"], b["lat"], b["lon"]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))


def build_world(seed=42):
    rnd = random.Random(seed)
    names = list(REGIONS)
    inputs = sorted({i for ins in SECTORS.values() for i in ins})
    suppliers = []
    for inp in inputs:
        for _ in range(5):
            region = rnd.choice(names)
            suppliers.append(dict(
                id=f"S{len(suppliers) + 1:02d}", input=inp, region=region,
                capacity=rnd.randint(40, 120), lead_days=rnd.randint(4, 25),
                digital=round(clamp(REGIONS[region]["digital"] + rnd.uniform(-.2, .15)), 2)))
    by_id = {s["id"]: s for s in suppliers}

    firms = []
    for idx, (name, sector, region) in enumerate(FIRMS):
        sourcing = {}
        for inp in SECTORS[sector]:
            pool = [s for s in suppliers if s["input"] == inp]
            weights = [3 if s["region"] == region else 1 for s in pool]
            n = rnd.choice([1, 1, 2, 3])
            chosen = []
            while len(chosen) < n:
                pick = rnd.choices(pool, weights)[0]
                if pick not in chosen:
                    chosen.append(pick)
            raw = [rnd.uniform(.3, 1) for _ in chosen]
            tot = sum(raw)
            sourcing[inp] = {s["id"]: r / tot for s, r in zip(chosen, raw)}
        firms.append(dict(
            id=f"F{idx + 1:02d}", name=name, sector=sector, region=region,
            workforce=rnd.randint(80, 400), revenue_cr=rnd.randint(20, 250),
            buffer_days=rnd.randint(4, 30),
            digital=round(clamp(REGIONS[region]["digital"] + rnd.uniform(-.25, .1)), 2),
            sourcing=sourcing))
    return dict(suppliers=suppliers, by_id=by_id, firms=firms)


def region_impact(hazard, epicentre, severity):
    h = HAZARDS[hazard]
    out = {}
    for name, r in REGIONS.items():
        exp = (1 - r["port"]) if hazard == "port_strike" else r[h["key"]]
        d = haversine_km(REGIONS[epicentre], r)
        out[name] = clamp(severity * exp * math.exp(-d / h["scale_km"]) * 1.6)
    return out


def resilience_score(firm, world):
    """0-100 structural score, independent of any scenario."""
    hhi, exposure, regions = [], 0.0, set()
    for inp, shares in firm["sourcing"].items():
        hhi.append(sum(v * v for v in shares.values()))
        for sid, v in shares.items():
            r = REGIONS[world["by_id"][sid]["region"]]
            regions.add(world["by_id"][sid]["region"])
            exposure += v * (r["flood"] + r["heat"] + r["drought"]) / 3 / len(firm["sourcing"])
    own = REGIONS[firm["region"]]
    exposure = .7 * exposure + .3 * (own["flood"] + own["heat"] + own["drought"]) / 3
    geo_conc = 1 / max(1, len(regions))
    score = 100 * (.30 * (1 - sum(hhi) / len(hhi)) + .25 * (1 - exposure) + .20 * firm["digital"]
                   + .15 * min(firm["buffer_days"] / 30, 1) + .10 * (1 - geo_conc))
    return round(score, 1)


def _firm_effect(firm, sup_loss, duration, own_loss):
    worst, worst_input = 0.0, None
    for inp, shares in firm["sourcing"].items():
        shortfall = sum(v * sup_loss[sid] for sid, v in shares.items())
        eff = clamp(shortfall - firm["buffer_days"] / duration)
        if eff > worst:
            worst, worst_input = eff, inp
    return max(worst, own_loss), worst_input


def _rebalance(firm, world, sup_loss):
    """Shift up to 50% of share away from hit suppliers to unaffected alternates."""
    new, moves = {}, []
    for inp, shares in firm["sourcing"].items():
        shares = dict(shares)
        alts = sorted((s for s in world["suppliers"]
                       if s["input"] == inp and s["id"] not in shares and sup_loss[s["id"]] < .15),
                      key=lambda s: s["lead_days"])
        hit = [sid for sid in shares if sup_loss[sid] >= .15]
        if alts and hit:
            for sid in hit:
                moved = shares[sid] * .5
                shares[sid] -= moved
                alt = alts[0]
                shares[alt["id"]] = shares.get(alt["id"], 0) + moved
                moves.append(dict(firm=firm["name"], input=inp, from_supplier=sid,
                                  from_region=world["by_id"][sid]["region"],
                                  to_supplier=alt["id"], to_region=alt["region"],
                                  lead_days=alt["lead_days"], shift_pct=round(moved * 100)))
        new[inp] = shares
    return new, moves


def simulate(world, hazard="flood", epicentre="Kochi", severity=.7, digital_boost=0.0):
    duration = round(7 + 45 * severity)
    impact = region_impact(hazard, epicentre, severity)

    sup_loss = {}
    for s in world["suppliers"]:
        dig = clamp(s["digital"] + digital_boost)
        sup_loss[s["id"]] = clamp(impact[s["region"]] * (1.25 - .7 * dig))

    firms_out, moves_all = [], []
    totals = dict(jobs_unmitigated=0, jobs_mitigated=0, rev_unmitigated=0.0, rev_mitigated=0.0)
    reskill = {}
    for f in world["firms"]:
        dig = clamp(f["digital"] + digital_boost)
        own_loss = clamp(impact[f["region"]] * .5 * (1.1 - .6 * dig))
        eff, bottleneck = _firm_effect(f, sup_loss, duration, own_loss)
        new_sourcing, moves = _rebalance(f, world, sup_loss)
        eff_m, _ = _firm_effect(dict(f, sourcing=new_sourcing), sup_loss, duration, own_loss)
        jobs, jobs_m = round(f["workforce"] * eff * .7), round(f["workforce"] * eff_m * .7)
        rev, rev_m = f["revenue_cr"] * eff * duration / 365, f["revenue_cr"] * eff_m * duration / 365
        totals["jobs_unmitigated"] += jobs; totals["jobs_mitigated"] += jobs_m
        totals["rev_unmitigated"] += rev;  totals["rev_mitigated"] += rev_m
        if jobs_m > 0:
            role, weeks = PATHWAYS[f["sector"]]
            r = reskill.setdefault(f["sector"], dict(sector=f["sector"], role=role, weeks=weeks, workers=0))
            r["workers"] += jobs_m
        moves_all += moves
        firms_out.append(dict(
            id=f["id"], name=f["name"], sector=f["sector"], region=f["region"],
            workforce=f["workforce"], score=resilience_score(f, world), digital=round(dig, 2),
            buffer_days=f["buffer_days"], output_loss_pct=round(eff * 100, 1),
            output_loss_mitigated_pct=round(eff_m * 100, 1), jobs_at_risk=jobs,
            jobs_at_risk_mitigated=jobs_m, bottleneck=bottleneck))

    firms_out.sort(key=lambda x: -x["jobs_at_risk"])
    return dict(
        scenario=dict(hazard=hazard, label=HAZARDS[hazard]["label"], epicentre=epicentre,
                      severity=severity, digital_boost=digital_boost, duration_days=duration),
        regions=[dict(name=n, impact=round(impact[n], 3), digital=REGIONS[n]["digital"],
                      lat=REGIONS[n]["lat"], lon=REGIONS[n]["lon"]) for n in REGIONS],
        firms=firms_out,
        totals=dict(jobs_unmitigated=totals["jobs_unmitigated"], jobs_mitigated=totals["jobs_mitigated"],
                    rev_unmitigated_cr=round(totals["rev_unmitigated"], 1),
                    rev_mitigated_cr=round(totals["rev_mitigated"], 1),
                    avg_resilience=round(sum(f["score"] for f in firms_out) / len(firms_out), 1),
                    total_jobs=sum(f["workforce"] for f in world["firms"])),
        recommendations=sorted(moves_all, key=lambda m: -m["shift_pct"])[:12],
        reskilling=sorted(reskill.values(), key=lambda r: -r["workers"]),
    )


if __name__ == "__main__":
    import json
    print(json.dumps(simulate(build_world())["totals"], indent=2))
