"""Live-platform tests (LYRA §13) — the create→run→decide loop works end-to-end: ABDGP plants the exact
effect the harness then certifies, and the FastAPI lifecycle (DRAFT → RUNNING → … → DECIDED) is real."""

from fastapi.testclient import TestClient

from chassis.app import app
from lyra.dgp import ABDGP
from lyra.harness import harness
from lyra.metrics import ProportionMetric


def test_abdgp_plants_the_exact_effect():
    rep = harness(ProportionMetric(), ABDGP(mu=0.2, effect=0.02, binary=True), R=120, n=20000)
    assert ABDGP(mu=0.2, effect=0.02).ground_truth().ate == 0.02     # planted truth, exact
    assert abs(rep["bias"]) < 0.006 and rep["coverage"] >= 0.88      # estimator recovers + certifies it


def test_create_run_decide_loop():
    c = TestClient(app)
    e = c.post("/api/experiments", json={"name": "t", "metric_type": "proportion", "mu": 0.25,
                                         "true_effect": 0.03, "rel_mde": 0.06, "days": 25, "n_per_day": 1600}).json()
    eid = e["id"]
    assert e["state"] == "DRAFT" and e["power"]["required_n"] > 0
    assert c.post(f"/api/experiments/{eid}/transition", params={"to_state": "RUNNING"}).json()["state"] == "RUNNING"
    sc = c.get(f"/api/experiments/{eid}").json()
    assert sc["truth"]["value"] == 0.03 and sc["truth"]["certified"]      # runs the DGP, certifies the planted truth
    for st in ("STOPPED", "ANALYZED"):
        c.post(f"/api/experiments/{eid}/transition", params={"to_state": st})
    d = c.post(f"/api/experiments/{eid}/transition", params={"to_state": "DECIDED", "ship": "true"}).json()
    assert d["state"] == "DECIDED" and d["decision"]["ship"] is True


def test_illegal_transition_rejected():
    c = TestClient(app)
    e = c.post("/api/experiments", json={"name": "t2", "true_effect": 0.02}).json()
    r = c.post(f"/api/experiments/{e['id']}/transition", params={"to_state": "DECIDED"})   # DRAFT ✗→ DECIDED
    assert r.status_code == 409


def test_all_world_designs_create_run_and_certify():
    """Every design (A/B · cluster · switchback · interference) certifies against its planted truth —
    except the naive marketplace A/B, which the platform refuses to certify (the interference money-shot)."""
    c = TestClient(app)
    specs = [
        ({"name": "ab", "design": "ab", "metric_type": "proportion", "mu": 0.25, "true_effect": 0.03}, True),
        ({"name": "cl", "design": "cluster", "true_effect": 0.5, "G": 60, "n_g": 25}, True),
        ({"name": "sb", "design": "switchback", "mu": 2000, "true_effect": 70, "J": 55, "H": 22, "n_bar": 20}, True),
        ({"name": "if-safe", "design": "interference", "interference_design": "cluster", "boost": 0.6}, True),
        ({"name": "if-naive", "design": "interference", "interference_design": "user", "boost": 0.6}, False),
    ]
    for spec, should_certify in specs:
        eid = c.post("/api/experiments", json=spec).json()["id"]
        c.post(f"/api/experiments/{eid}/transition", params={"to_state": "RUNNING"})
        sc = c.get(f"/api/experiments/{eid}").json()
        assert sc["truth"]["certified"] is should_certify, f"{spec['name']}: certify={sc['truth']['certified']}"
