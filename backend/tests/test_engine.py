import pytest
from fastapi.testclient import TestClient

from backend.app.engine import HAZARDS, REGIONS, build_world, simulate
from backend.app.main import app

W = build_world()
client = TestClient(app)


@pytest.mark.parametrize("hazard", list(HAZARDS))
@pytest.mark.parametrize("region", list(REGIONS))
def test_mitigation_never_worse(hazard, region):
    t = simulate(W, hazard, region, .7)["totals"]
    assert t["jobs_mitigated"] <= t["jobs_unmitigated"]


def test_severity_monotonic():
    lo = simulate(W, "flood", "Kochi", .2)["totals"]["jobs_unmitigated"]
    hi = simulate(W, "flood", "Kochi", .9)["totals"]["jobs_unmitigated"]
    assert hi >= lo


def test_digital_uplift_helps():
    base = simulate(W, "flood", "Kochi", .8)["totals"]["jobs_unmitigated"]
    up = simulate(W, "flood", "Kochi", .8, digital_boost=.3)["totals"]["jobs_unmitigated"]
    assert up <= base


def test_zero_severity_no_impact():
    assert simulate(W, "drought", "Nagpur", 0)["totals"]["jobs_unmitigated"] == 0


def test_scores_in_range():
    assert all(0 <= f["score"] <= 100 for f in simulate(W)["firms"])


def test_world_is_deterministic():
    assert simulate(build_world(), "flood", "Kochi", .5) == simulate(build_world(), "flood", "Kochi", .5)


def test_api_simulate_ok():
    r = client.get("/api/simulate", params=dict(hazard="flood", region="Kochi", severity=.7))
    assert r.status_code == 200 and r.json()["totals"]["total_jobs"] > 0


@pytest.mark.parametrize("params", [dict(hazard="tsunami"), dict(region="Atlantis"),
                                    dict(severity=1.5), dict(boost=-1)])
def test_api_rejects_bad_input(params):
    assert client.get("/api/simulate", params=params).status_code == 422


def test_api_meta():
    assert set(client.get("/api/meta").json()["regions"]) == set(REGIONS)
