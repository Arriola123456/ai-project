"""Calibrate the model to the ONPE age profiles (minimum distance).

    python code/calibrate.py            # all four nested models
    python code/calibrate.py M2         # one model
    python code/calibrate.py --full     # robustness: every age 20-80 and every band
    python code/calibrate.py --refine M2  # restart a model from its saved optimum

Targets, per election (first rounds 2006-2026 and the 2001 run-off):
  * theta_a = P(a) - P(69) for a = 20..80, a != 69, weighted by 1/se^2
    (code/data/theta_profiles.csv, mesa fixed effects, from the thesis);
  * turnout by ONPE band (18-19, ..., 70+), elector-weighted, with a nominal
    standard error SE_LEVEL (code/data/band_levels.csv).
External: the fine F_t in % of the UIT, elector-weighted (code/data/fines.csv),
enters through S_t = s0 + q F_t.

Nested models:
  M0  static, linear cost        (beta = 1, lam = 0)
  M1  static, power cost         (beta free, lam = 0)
  M2  habit, constant rho        (beta free, lam, rho0, omega free)
  M3  habit, rho rising with age (M2 + rho1 >= 0)
Writes code/output/params_<M>.json and code/output/fit_<M>.csv.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

from model import AGE_SCALE, FIRST_AGE, Params, band_mean, turnout_profile

HERE = Path(__file__).resolve().parent
DATA, OUT = HERE / "data", HERE / "output"
OUT.mkdir(exist_ok=True)

TAGS = ["2001_2V", "2006_1V", "2011_1V", "2016_1V", "2021_1V", "2026_1V"]
SE_LEVEL = 0.01
# Targeted moments. "main": the window the thesis is about -- ages 45-80 and the
# levels of the 60-69 and 70+ bands. "full": every age 20-80 and every band
# (robustness; young ages carry election-specific mobilisation that a single
# life cycle cannot fit, and within-mesa theta_a and aggregate band levels
# disagree there).
SPECS = {"main": {"ages": [a for a in range(45, 81) if a != 69], "bands": [6, 7], "suffix": ""},
         "full": {"ages": [a for a in range(20, 81) if a != 69], "bands": [1, 2, 3, 4, 5, 6, 7],
                  "suffix": "_full"}}
FIT_AGES, BANDS_USED, SUFFIX = SPECS["main"]["ages"], SPECS["main"]["bands"], ""


def set_spec(name):
    global FIT_AGES, BANDS_USED, SUFFIX
    FIT_AGES, BANDS_USED, SUFFIX = SPECS[name]["ages"], SPECS[name]["bands"], SPECS[name]["suffix"]


def load_data():
    th = pd.read_csv(DATA / "theta_profiles.csv")
    lev = pd.read_csv(DATA / "band_levels.csv")
    aw = pd.read_csv(DATA / "age_weights.csv")
    fines = pd.read_csv(DATA / "fines.csv").set_index("tag")["fine_pct_uit"]
    data = {}
    for t in TAGS:
        d = th[(th.tag == t) & th.edad.isin(FIT_AGES)].set_index("edad").loc[FIT_AGES]
        data[t] = {
            "theta": d["b"].to_numpy(), "se": d["se"].to_numpy(),
            "bands": lev[(lev.tag == t) & lev.banda.isin(BANDS_USED)].sort_values("banda")[
                ["edad_min", "edad_max", "turnout"]].to_numpy(),
            "weights": dict(zip(aw[aw.tag == t].edad, aw[aw.tag == t].electores)),
            "fine": float(fines[t]),
        }
    return data


# ---- parameter vector <-> Params ---------------------------------------------
def _logit(lo, hi):
    return (lambda x: lo + (hi - lo) / (1 + np.exp(-x)),
            lambda y: np.log((y - lo) / (hi - y)))


# b(a) is parameterised by its peak age a* (Proposition 1): A is implied by
# A = kappa * beta * (a*/AGE_SCALE)^(beta - alpha) / alpha. This removes the
# near-cancellation between A and kappa that the raw (A, kappa) pair allows.
SPEC = {   # name: (transform, inverse) -- maps R to the admissible range
    "kappa": (np.exp, np.log), "s0": _logit(0.0, 5.0), "q": _logit(0.0, 2.0),
    "lam": (np.exp, np.log), "rho1": _logit(0.0, 1.0),   # rho1 is a SHARE of 0.95 - rho0 (see to_params)
    "astar": _logit(20.0, 90.0), "alpha": _logit(0.02, 0.98), "beta": _logit(1.0, 6.0),
    "rho0": _logit(0.0, 0.95), "omega": _logit(0.05, 0.95),
}
FREE = {
    "M0": ["astar", "alpha", "kappa", "s0", "q"],
    "M1": ["astar", "alpha", "kappa", "beta", "s0", "q"],
    "M2": ["astar", "alpha", "kappa", "beta", "s0", "q", "lam", "rho0", "omega"],
    "M3": ["astar", "alpha", "kappa", "beta", "s0", "q", "lam", "rho0", "omega", "rho1"],
}
FIXED = {"M0": {"beta": 1.0, "lam": 0.0, "omega": 0.5}, "M1": {"lam": 0.0, "omega": 0.5},
         "M2": {"rho1": 0.0}, "M3": {}}


def to_params(model, x):
    names = FREE[model]
    kw = {n: float(SPEC[n][0](v)) for n, v in zip(names, x[:len(names)])}
    kw.update(FIXED[model])
    if "rho1" in names:   # rho(100) = rho0 + rho1 <= 0.95, so M3 nests M2 and never hits the clip
        kw["rho1"] = kw["rho1"] * (0.95 - kw["rho0"])
    astar = kw.pop("astar")
    kw["A"] = kw["kappa"] * kw["beta"] * (astar / AGE_SCALE) ** (kw["beta"] - kw["alpha"]) / kw["alpha"]
    kw["mu"] = dict(zip(TAGS, x[len(names):]))
    return Params(**kw)


def to_vector(model, p: Params):
    names = FREE[model]
    clip = {"beta": (1.0 + 1e-3, 6.0 - 1e-3), "alpha": (0.02 + 1e-3, 0.98 - 1e-3),
            "astar": (20.0 + 1e-3, 90.0 - 1e-3), "rho0": (1e-3, 0.95 - 1e-3),
            "omega": (0.05 + 1e-3, 0.95 - 1e-3), "s0": (1e-4, 5.0 - 1e-3), "q": (1e-4, 2.0 - 1e-3)}
    vals = []
    for n in names:
        v = p.peak_age() if n == "astar" else getattr(p, n)
        if n == "rho1":
            v = min(max(v / max(0.95 - p.rho0, 1e-6), 1e-4), 1 - 1e-4)
        if n in clip:
            v = min(max(v, clip[n][0]), clip[n][1])
        if n in ("lam", "rho1", "kappa"):
            v = max(v, 1e-4)
        vals.append(float(SPEC[n][1](v)))
    return np.array(vals + [p.mu[t] for t in TAGS])


def predictions(p: Params, data):
    out = {}
    for t, d in data.items():
        S = p.s0 + p.q * d["fine"]
        P = turnout_profile(p, p.mu[t], S)
        theta = P[np.array(FIT_AGES) - FIRST_AGE] - P[69 - FIRST_AGE]
        bands = np.array([band_mean(P, d["weights"], int(lo), int(hi)) for lo, hi, _ in d["bands"]])
        out[t] = {"P": P, "theta": theta, "bands": bands, "S": S}
    return out


def residuals(p: Params, data):
    pred = predictions(p, data)
    r = []
    for t, d in data.items():
        r.append((pred[t]["theta"] - d["theta"]) / d["se"])
        r.append((pred[t]["bands"] - d["bands"][:, 2]) / SE_LEVEL)
    return np.concatenate(r)


def calibrate(model, data, start: Params):
    x0 = to_vector(model, start)
    sol = least_squares(lambda x: residuals(to_params(model, x), data), x0,
                        method="trf", x_scale="jac", max_nfev=400, verbose=0)
    p = to_params(model, sol.x)
    return p, float(sol.cost * 2), sol


def default_start(data):
    mu = {t: -1.0 for t in data}
    return Params(A=3.0, alpha=0.5, kappa=1.5, beta=1.0, lam=0.0, rho0=0.5, rho1=0.0,
                  omega=0.5, s0=0.6, q=0.05, mu=mu)   # peak age 50


def save(model, p: Params, obj, data):
    pd_ = p.__dict__.copy()
    pd_["objective"] = obj
    pd_["n_moments"] = int(sum(len(d["theta"]) + len(d["bands"]) for d in data.values()))
    pd_["n_params"] = len(FREE[model]) + len(TAGS)
    pd_["peak_age"] = float(p.peak_age())
    (OUT / f"params_{model}{SUFFIX}.json").write_text(json.dumps(pd_, indent=2))
    pred = predictions(p, data)
    rows = []
    for t, d in data.items():
        for a, th, se, m in zip(FIT_AGES, d["theta"], d["se"], pred[t]["theta"]):
            rows.append({"tag": t, "edad": a, "theta_data": th, "se": se, "theta_model": m})
    pd.DataFrame(rows).to_csv(OUT / f"fit_{model}{SUFFIX}.csv", index=False)


def load_params(model) -> Params:
    d = json.loads((OUT / f"params_{model}{SUFFIX}.json").read_text())
    keys = Params.__dataclass_fields__.keys()
    return Params(**{k: d[k] for k in keys})


def main(models, refine=False):
    data = load_data()
    start = default_start(data)
    for m in ["M0", "M1", "M2", "M3"]:
        if m not in models:
            if (OUT / f"params_{m}{SUFFIX}.json").exists():
                start = load_params(m)
            continue
        if refine:   # restart from the saved optimum: least_squares stops at max_nfev
            p0 = load_params(m)
            obj0 = float(np.sum(residuals(p0, data) ** 2))
            p, obj, sol = calibrate(m, data, p0)
            print(f"  {m} refine: {obj0:,.2f} -> {obj:,.2f} (status {sol.status}, nfev {sol.nfev})", flush=True)
            if obj < obj0:
                save(m, p, obj, data)
            start = load_params(m)
            continue
        best = None
        starts = [start]
        full = OUT / f"params_{m}{SPECS['full']['suffix']}.json"
        if SUFFIX != SPECS["full"]["suffix"] and full.exists():   # warm start from the robustness run
            d_ = json.loads(full.read_text())
            warm = Params(**{k: d_[k] for k in Params.__dataclass_fields__})
            starts = [warm] if m == "M0" else [start, warm]   # a cold M0 start crawls for ~1000 evaluations
        if m == "M2":   # habit: a few starting points for (lam, rho0, omega)
            for lam, rho0, om in [(0.3, 0.5, 0.5), (1.0, 0.3, 0.3), (0.1, 0.8, 0.7)]:
                starts.append(Params(**{**start.__dict__, "lam": lam, "rho0": rho0, "omega": om}))
        if m == "M3":
            starts += [Params(**{**s.__dict__, "rho1": r}) for s in list(starts) for r in (0.05, 0.3)]
            starts += [Params(**{**start.__dict__, "rho0": r0, "rho1": r1}) for r0, r1 in ((0.6, 0.3), (0.3, 0.6))]
        for s in starts:
            p, obj, sol = calibrate(m, data, s)
            print(f"  {m} start -> objective {obj:,.1f} (status {sol.status}, nfev {sol.nfev})", flush=True)
            if best is None or obj < best[1]:
                best = (p, obj)
        p, obj = best
        save(m, p, obj, data)
        print(f"{m}: objective {obj:,.1f}  peak age {p.peak_age():.1f}  "
              + " ".join(f"{k}={(p.peak_age() if k == 'astar' else getattr(p, k)):.3f}" for k in FREE[m]), flush=True)
        start = p


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--full" in args:
        set_spec("full")
        args.remove("--full")
    refine = "--refine" in args
    if refine:
        args.remove("--refine")
    main(args or ["M0", "M1", "M2", "M3"], refine=refine)
