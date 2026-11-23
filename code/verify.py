"""Single entry point: checks every claim of the paper and rebuilds its figures.

    python3 code/verify.py

Exits with an error (SystemExit) as soon as a claim does not hold.
  1. Symbolic (SymPy): Proposition 1 (life-cycle benefit) and the static
     comparative statics (a)-(d), including the threshold condition of (iv).
  2. Numerical (model.py): Propositions 2-4 with the AR(1) habit (numbering of the final paper).
  3. Calibration: reloads code/output/params_M*.json, recomputes each
     objective from code/data/, checks the nesting M0 >= M1 >= M2 >= M3 and
     redraws the figures used in the paper and the slides (the slide-only
     figures come from code/slide_figures.py).
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sympy as sp
from scipy.stats import norm

from model import FIRST_AGE, Params, gap, tau70, turnout_profile

HERE = Path(__file__).resolve().parent
(HERE / "figures").mkdir(exist_ok=True)
(HERE / "output").mkdir(exist_ok=True)
rng = np.random.default_rng(20261030)


def check(cond, msg):
    if not cond:
        raise SystemExit(f"FAIL: {msg}")
    print(f"  ok  {msg}")


def P_at(P, a):
    return P[a - FIRST_AGE]


# =============================================================================
print("1. Symbolic checks")
a, A, al, k, be = sp.symbols("a A alpha kappa beta", positive=True)
b = A * a**al - k * a**be
b1, b2 = sp.diff(b, a), sp.diff(b, a, 2)
astar = (A * al / (k * be)) ** (1 / (be - al))
check(sp.simplify(sp.powsimp(sp.expand(b1 - a**(al - 1) * (A * al - k * be * a**(be - al))), force=True)) == 0,
      "P1: b'(a) = a^(alpha-1) [A alpha - kappa beta a^(beta-alpha)], so b' = 0 iff a^(beta-alpha) = A alpha/(kappa beta)")
f1, fstar = sp.lambdify((A, al, k, be, a), b1, "numpy"), sp.lambdify((A, al, k, be), astar, "numpy")
dr = rng.uniform([0.5, 0.05, 0.1, 1.0], [5, 0.95, 3, 3], size=(20000, 4))
check(np.max(np.abs(f1(*dr.T, fstar(*dr.T)))) < 1e-8,
      "P1: b'(a*) = 0 at a* = (A alpha/(kappa beta))^(1/(beta-alpha)) on 2e4 random draws")
check(sp.simplify(b2 - (A * al * (al - 1) * a**(al - 2) - k * be * (be - 1) * a**(be - 2))) == 0,
      "P1: b'' = A alpha(alpha-1) a^(alpha-2) - kappa beta(beta-1) a^(beta-2)")
draws = rng.uniform([0.5, 0.05, 0.1, 1.0, 1.0], [5, 0.95, 3, 3, 100], size=(20000, 5))
f2 = sp.lambdify((A, al, k, be, a), b2, "numpy")
check(np.all(f2(*draws.T) < 0), "P1: b'' < 0 for 0<alpha<1<=beta on 2e4 random draws (strict concavity)")
check(sp.limit(b1.subs({be: 1, al: sp.Rational(1, 2)}), a, sp.oo) == -k,
      "P1: beta = 1 -> b'(a) -> -kappa (linear decline; alpha = 1/2, any alpha < 1 by the factorisation)")
check(sp.limit(b1.subs({be: 2, al: sp.Rational(1, 2)}), a, sp.oo) == -sp.oo,
      "P1: beta = 2 -> b'(a) -> -infinity (accelerating decline)")

# static comparative statics at the threshold, G(x) = F((x - mu)/s)
B, S, mu, s = sp.symbols("B S mu s", real=True)
Phi = lambda x: (1 + sp.erf(x / sp.sqrt(2))) / 2
phi = lambda x: sp.exp(-x**2 / 2) / sp.sqrt(2 * sp.pi)
G = lambda x: Phi((x - mu) / s)
tau = G(B + S) - G(B)
z0, z1 = (B - mu) / s, (B + S - mu) / s
check(sp.simplify(sp.diff(tau, S) - phi(z1) / s) == 0, "(a): dtau/dS = g(c1)")
check(sp.simplify(sp.diff(tau, B) - (phi(z1) - phi(z0)) / s) == 0, "(c): dtau/dB = g(c1) - g(c0)")
check(sp.simplify(sp.diff(tau, s) + (z1 * phi(z1) - z0 * phi(z0)) / s) == 0,
      "(d): dtau/ds = -(1/s)[z1 f(z1) - z0 f(z0)]")
zz0, zz1 = -rng.uniform(0, 4, 10**5), rng.uniform(1e-6, 4, 10**5)
check(np.all(zz1 * norm.pdf(zz1) - zz0 * norm.pdf(zz0) > 0), "(d): sign negative when z0 <= 0 < z1")
z1g, z0g = np.array([3.0, -1.0]), np.array([-3.0])
ds = -((z1g * norm.pdf(z1g)).mean() - (z0g * norm.pdf(z0g)).mean())
check(norm.cdf(z1g).mean() > 0.5 and ds > 0,
      f"(iv) counterexample: group-average condition holds but s dDelta/ds = {ds:+.3f} > 0")
check(-0.0947 - 1e-4 < (-2 * norm.pdf(-2) + 3 * norm.pdf(-3)) < -0.0947 + 1e-4,
      "claude.ai turn 5 counterexample: z0=-3, z1=-2 gives s dtau/ds = +0.095 > 0")

# =============================================================================
print("2. Numerical checks of Propositions 2-4 (habit)")
W = {a_: 1.0 for a_ in range(18, 101)}


def random_params(n, lam_range=(0.2, 1.5), rho1=0.0):
    out = []
    while len(out) < n:
        p = Params(A=rng.uniform(2, 5), alpha=rng.uniform(0.2, 0.8), kappa=rng.uniform(1, 3),
                   beta=rng.uniform(1, 2.5), lam=rng.uniform(*lam_range), rho0=rng.uniform(0.2, 0.8),
                   rho1=rho1, omega=rng.uniform(0.2, 0.8))
        if p.peak_age() <= 60:                      # peak by 60, as in the calibration
            out.append((p, rng.uniform(-1.5, 1.5), rng.uniform(0.2, 1.5)))
    return out


# P2: the jump is computed with the habit accumulated under compulsion;
# habit attenuates it when the band of compliers lies above the mode.
n_above, n_neg = 0, 0
for p, mu_, S_ in random_params(60):
    P0 = turnout_profile(p, mu_, S_)
    if P_at(P0, 70) > 0.5:                        # c0 above the mode (normal G)
        n_above += 1
        t_hi = tau70(Params(**{**p.__dict__, "lam": p.lam * 1.05}), mu_, S_)
        n_neg += t_hi < tau70(p, mu_, S_)
check(n_above > 10 and n_neg == n_above,
      f"P2: dtau70/dlam < 0 whenever the band is above the mode ({n_neg}/{n_above} draws)")

# P3: steps every D years in E[h] after 70; first step = P1(69) - P0(70), any rho
first_steps = []
for rho in (0.3, 0.6, 0.8):
    p = Params(A=3.0, alpha=0.5, kappa=1.8, beta=1.3, lam=0.6, rho0=rho, omega=0.5)
    P, H = turnout_profile(p, 1.0, 0.9, return_parts=True)
    step75 = P_at(H, 74) - P_at(H, 75)
    smooth = P_at(H, 73) - P_at(H, 74)
    first_steps.append(step75 / (P_at(P, 69) - P_at(P, 70)))
    check(step75 > 0 and abs(smooth) < 0.05 * step75,
          f"P3 (rho={rho}): E[h] drops {step75:.3f} between 74 and 75, only {smooth:+.4f} between 73 and 74")
check(all(abs(x - 1) < 0.05 for x in first_steps),
      f"P3: first step / (P1(69)-P0(70)) = {', '.join(f'{x:.3f}' for x in first_steps)} -- equal to the jump, any rho")
# P3 exact identity: H(a+1) - H(a) = sum_k rho^k [P(a+1-(k+1)d) - P(a-(k+1)d)]
p = Params(A=3.0, alpha=0.5, kappa=1.8, beta=1.3, lam=0.6, rho0=0.6, omega=0.5)
P, H = turnout_profile(p, 1.0, 0.9, return_parts=True)
worst = 0.0
for a_ in [a_ for a_ in range(25, 95) if (a_ + 1 - FIRST_AGE) % 5 != 0]:
    rhs = sum(0.6**k * (P_at(P, a_ + 1 - (k + 1) * 5) - P_at(P, a_ - (k + 1) * 5))
              for k in range(20) if a_ - (k + 1) * 5 >= FIRST_AGE)
    worst = max(worst, abs((P_at(H, a_ + 1) - P_at(H, a_)) - rhs))
check(worst < 1e-9, f"P3: exact identity for H(a+1) - H(a) at every age 25-94 (max error {worst:.1e})")
p_nohab = Params(A=3.0, alpha=0.5, kappa=1.8, beta=1.3, lam=0.0, rho0=0.6, omega=0.5)
Pn = turnout_profile(p_nohab, -0.3, 0.9)
d = np.diff(Pn[70 - FIRST_AGE:86 - FIRST_AGE])
check(np.ptp(d[3:6]) < 0.01, "P3: with lam = 0 the profile after 70 has no steps")

# P4: rho rising with age: same first step, slower decay, E[h] rises before 70
pc = Params(A=3.0, alpha=0.5, kappa=1.8, beta=1.3, lam=0.6, rho0=0.5, rho1=0.0, omega=0.5)
pr = Params(**{**pc.__dict__, "rho1": 0.4})
(Pc, Hc), (Pr, Hr) = (turnout_profile(x, -0.3, 0.9, return_parts=True) for x in (pc, pr))
s1c, s1r = P_at(Hc, 74) - P_at(Hc, 75), P_at(Hr, 74) - P_at(Hr, 75)
s2c, s2r = P_at(Hc, 79) - P_at(Hc, 80), P_at(Hr, 79) - P_at(Hr, 80)
check(s2r / s1r > s2c / s1c, f"P4: second/first step {s2r / s1r:.3f} (rho'>0) > {s2c / s1c:.3f} (rho const)")
check(P_at(Hr, 69) > P_at(Hr, 60) and abs(P_at(Hc, 69) - P_at(Hc, 60)) < 0.02,
      "P4: with rho'>0 the habit keeps rising between 60 and 69 (risk for a* <= 60)")
# P4 exact identity with rho(a) rising: Pi_m(a) = prod_{j=1..m} rho(a - j d),
#   H(a) = sum_k Pi_{k-1}(a) P(a - k d),
#   H(a+1) - H(a) = sum_k Pi_{k-1}(a+1) [P(a+1-kd) - P(a-kd)] + R(a),  R(a) >= 0.
# (the code's k >= 1 is the paper's k + 1)
# The first draft had no R(a): its error is measured and reported.
Pi = lambda p_, a_, m: float(np.prod([p_.rho(a_ - j * 5) for j in range(1, m + 1)]))
past = lambda a_: [k_ for k_ in range(1, 20) if a_ - k_ * 5 >= FIRST_AGE]
err_H = max(abs(P_at(Hr, a_) - sum(Pi(pr, a_, k_ - 1) * P_at(Pr, a_ - k_ * 5) for k_ in past(a_)))
            for a_ in range(FIRST_AGE, 101))
check(err_H < 1e-9, f"P4: H(a) = sum_k Pi_k(a) P(a-(k+1)d) at every age 18-100 (max error {err_H:.1e})")
worst5, naive5, minR = 0.0, 0.0, np.inf
for a_ in [a_ for a_ in range(25, 95) if (a_ + 1 - FIRST_AGE) % 5 != 0]:
    lhs = P_at(Hr, a_ + 1) - P_at(Hr, a_)
    main_ = sum(Pi(pr, a_ + 1, k_ - 1) * (P_at(Pr, a_ + 1 - k_ * 5) - P_at(Pr, a_ - k_ * 5)) for k_ in past(a_))
    R = sum((Pi(pr, a_ + 1, k_ - 1) - Pi(pr, a_, k_ - 1)) * P_at(Pr, a_ - k_ * 5) for k_ in past(a_))
    worst5, naive5, minR = max(worst5, abs(lhs - main_ - R)), max(naive5, abs(lhs - main_)), min(minR, R)
check(worst5 < 1e-9 and minR >= 0,
      f"P4: H(a+1) - H(a) = sum_k Pi_k(a+1) [one-year differences] + R(a), R(a) >= 0 "
      f"(max error {worst5:.1e}, min R {minR:.1e})")
check(naive5 > 1e-4, f"P4: the first draft's identity without R(a) is off by up to {naive5:.1e}")
w_jump = [Pi(pr, 70 + k_ * 5, k_ - 1) for k_ in (1, 2, 3, 4)]
check(all(w >= float(pr.rho(70)) ** (k_ - 1) for k_, w in zip((1, 2, 3, 4), w_jump)),
      "P4: weight of P(70)-P(69) in the step at 70+(k+1)d is >= rho(70)^k")
# Identification paragraph: the normal density moves by at most 21% between
# turnout levels 0.73 and 0.3-0.5, so G alone cannot make the fall four times steeper
dens = norm.pdf(norm.ppf(np.linspace(0.3, 0.5, 201))) / norm.pdf(norm.ppf(0.73))
check(dens.max() < 1.21, f"identification: g(G^-1(u)) / g(G^-1(0.73)) <= {dens.max():.3f} for u in [0.3, 0.5]")

# =============================================================================
print("3. Calibration")
import calibrate as cal  # noqa: E402

done = {}
for spec in ["full", "main"]:
    cal.set_spec(spec)
    suffix = cal.SPECS[spec]["suffix"]
    files = [HERE / "output" / f"params_{m}{suffix}.json" for m in ["M0", "M1", "M2", "M3"]]
    files = [f for f in files if f.exists()]
    if not files:
        print(f"  ({spec}: no calibration saved yet -- run code/calibrate.py{' --full' if spec == 'full' else ''})")
        continue
    data = cal.load_data()
    objs = {}
    for f in files:
        m = f.stem.split("_")[1]
        p = cal.load_params(m)
        saved = json.loads(f.read_text())["objective"]
        obj = float(np.sum(cal.residuals(p, data) ** 2))
        check(abs(obj - saved) <= 1e-6 * max(1.0, saved), f"{spec}/{m}: objective {obj:,.1f} reproduced from code/data")
        objs[m] = obj
    order = [m for m in ["M0", "M1", "M2", "M3"] if m in objs]
    check(all(objs[x] >= objs[y] - 1e-6 * objs[x] for x, y in zip(order, order[1:])),
          f"{spec}: objective non-increasing from M0 to M3 (nesting)")
    done[spec] = (data, objs, order)

if "main" in done:
    cal.set_spec("main")
    data, objs, order = done["main"]
    FREE, TAGS, load_params, predictions = cal.FREE, cal.TAGS, cal.load_params, cal.predictions
    # the most parsimonious model within 0.01% of the best objective
    best = next(m for m in order if objs[m] <= min(objs.values()) * (1 + 1e-4))
    static = "M1" if "M1" in objs else order[0]
    P_best, P_static = load_params(best), load_params(static)
    pred, pred_s = predictions(P_best, data), predictions(P_static, data)

    # --- table: nested models -------------------------------------------------
    names = {"M0": r"estático, $\beta=1$", "M1": r"estático, $\beta$ libre",
             "M2": r"hábito, $\rho$ constante", "M3": r"hábito, $\rho(a)$ creciente"}
    lines = [r"\begin{tabular}{lrrrrrrrrr}", r"\toprule",
             r"Modelo & Objetivo & $a^*$ & $\alpha$ & $\beta$ & $\lambda$ & $\rho_0$ & $\rho_1$ & $s_0$ & $q$ \\",
             r"\midrule"]
    for m in order:
        q_ = load_params(m)
        free = FREE[m]
        cell = lambda k_, v: f"{v:.2f}" if k_ in free or (k_ == "A") else "--"
        lines.append(f"{m}: {names[m]} & {objs[m]:,.0f} & {q_.peak_age():.1f} & "
                     + " & ".join(cell(k_, getattr(q_, k_)) for k_ in ["alpha", "beta", "lam", "rho0", "rho1", "s0", "q"])
                     + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (HERE / "output" / "calib_models.tex").write_text("\n".join(lines).replace(",", "{,}"), encoding="utf-8")

    # --- figure: fit by election, static vs habit -----------------------------
    fig, axes = plt.subplots(2, 3, figsize=(11, 6), sharex=True, sharey=True)
    ages = np.arange(20, 81)
    prof = pd.read_csv(HERE / "data" / "theta_profiles.csv")
    theta_all = lambda P: P[ages - FIRST_AGE] - P[69 - FIRST_AGE]
    for ax, t in zip(axes.flat, TAGS):
        d = data[t]
        dp = prof[(prof.tag == t) & prof.edad.between(20, 80)]
        ax.axvspan(cal.FIT_AGES[0] - 0.5, 80.5, color="#EEF2FA", zorder=0)
        ax.errorbar(dp.edad, dp.b, yerr=1.96 * dp.se, fmt="o", ms=2.5, lw=0.6,
                    color="#7a8699", label="ONPE, IC 95%")
        ax.plot(ages, theta_all(pred_s[t]["P"]), color="#C0392B", lw=1.4, ls="--", label=f"{static} (sin hábito)")
        ax.plot(ages, theta_all(pred[t]["P"]), color="#1E3A8A", lw=1.8, label=f"{best}")
        ax.axvline(69.5, color="0.5", ls=":", lw=0.8)
        ax.axhline(0, color="0.85", lw=0.6)
        ax.set_title(t.replace("_", " "), fontsize=10)
        ax.spines[["top", "right"]].set_visible(False)
    for ax in axes[1]:
        ax.set_xlabel("edad")
    for ax in axes[:, 0]:
        ax.set_ylabel(r"$\theta_a = P(a)-P(69)$")
    axes[0, 0].legend(frameon=False, fontsize=8, loc="lower left")
    fig.tight_layout()
    fig.savefig(HERE / "figures" / "fit_profiles.pdf")
    plt.close(fig)

    # --- table: the jump at 70 and the gap, data vs model -----------------------
    rows = []
    for t in TAGS:
        d = data[t]
        S_t = pred[t]["S"]
        g = gap(P_best, P_best.mu[t], S_t, d["weights"])
        lev = {int(lo): v for lo, hi, v in d["bands"]}
        rows.append({"tag": t, "theta70_data": float(d["theta"][cal.FIT_AGES.index(70)]),
                     "theta70_model": float(pred[t]["theta"][cal.FIT_AGES.index(70)]),
                     "Delta_data": lev[60] - lev[70], **{k_: float(v) for k_, v in g.items()}})
    dec = pd.DataFrame(rows)
    dec.to_csv(HERE / "output" / "gap_decomposition.csv", index=False)
    lines = [r"\begin{tabular}{lrrrrr}", r"\toprule",
             r" & \multicolumn{2}{c}{Salto medido, $\theta_{70}$} & Efecto, $\tau^{70}$ & \multicolumn{2}{c}{Brecha de grupos, $\Delta$} \\",
             r"\cmidrule(lr){2-3}\cmidrule(lr){4-4}\cmidrule(lr){5-6}",
             r"Elección & datos & modelo & modelo & datos & modelo \\", r"\midrule"]
    for _, r_ in dec.iterrows():
        lines.append(f"{r_.tag.replace('_', ' ')} & {r_.theta70_data:.3f} & {r_.theta70_model:.3f} & "
                     f"{r_.tau70:.3f} & {r_.Delta_data:.3f} & {r_.Delta:.3f} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (HERE / "output" / "gap_table.tex").write_text("\n".join(lines), encoding="utf-8")
    # the measured jump is the effect plus one year of ageing under compulsion (Section 3):
    # in the model, |theta70| >= tau70 when compulsory turnout does not rise from 69 to 70
    check(all(-r_.theta70_model >= r_.tau70 - 1e-9 for _, r_ in dec.iterrows()),
          "model: |theta70| >= tau70 in every election (one year of ageing on top of the effect)")

    # --- Proposition 3 against the data: steps at 75 and 80 -------------------------
    # one-year changes of theta_a after 70; the step ages are compared with the mean
    # change at the other ages 71-79 (descriptive: the thesis reports only one se per age)
    prof = pd.read_csv(HERE / "data" / "theta_profiles.csv")
    srows = []
    for t in TAGS:
        s_ = prof[prof.tag == t].set_index("edad").b
        dlt = s_.diff()
        other = dlt[[a_ for a_ in range(71, 80) if a_ != 75]].mean()
        srows.append({"tag": t, "d75": dlt[75], "d80": dlt[80], "other": other})
    steps = pd.DataFrame(srows)
    steps.to_csv(HERE / "output" / "steps_data.csv", index=False)
    lines = [r"\begin{tabular}{lrrr}", r"\toprule",
             r"Elección & cambio 74$\to$75 & cambio 79$\to$80 & cambio medio en 71--79 (sin 75) \\", r"\midrule"]
    for _, r_ in steps.iterrows():
        lines.append(f"{r_.tag.replace('_', ' ')} & {100 * r_.d75:+.1f} & {100 * r_.d80:+.1f} & {100 * r_.other:+.1f} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (HERE / "output" / "steps_table.tex").write_text("\n".join(lines), encoding="utf-8")
    n75 = int((steps.d75 < steps.other).sum())
    n80 = int((steps.d80 < steps.other).sum())
    print(steps.round(3).to_string(index=False))
    # the steps in the calibrated model (2016)
    P16 = pred["2016_1V"]["P"]
    m75 = (P_at(P16, 75) - P_at(P16, 74)) - np.mean([P_at(P16, a_) - P_at(P16, a_ - 1) for a_ in (72, 73, 74, 76, 77, 78)])

    # --- numbers quoted in the text of the paper and the slides ---------------
    share = dec["tau70"] / dec["Delta"]
    pb, p1 = load_params(best), load_params(static)
    nums = {
        "tauShareMin": f"{100 * share.min():.0f}", "tauShareMax": f"{100 * share.max():.0f}",
        "tauMin": f"{dec.tau70.min():.2f}", "tauMax": f"{dec.tau70.max():.2f}",
        "DeltaDataMin": f"{dec.Delta_data.min():.2f}", "DeltaDataMax": f"{dec.Delta_data.max():.2f}",
        "objMzero": f"{objs['M0']:,.0f}".replace(",", "{,}"), "objMone": f"{objs['M1']:,.0f}".replace(",", "{,}"),
        "objBest": f"{objs[best]:,.0f}".replace(",", "{,}"), "bestModel": best,
        "betaStatic": f"{p1.beta:.2f}", "betaBest": f"{pb.beta:.2f}", "lamBest": f"{pb.lam:.2f}",
        "rhoBest": f"{pb.rho0:.2f}", "peakBest": f"{pb.peak_age():.0f}", "peakStatic": f"{p1.peak_age():.0f}",
        "sZeroBest": f"{pb.s0:.2f}", "omegaBest": f"{pb.omega:.2f}", "alphaBest": f"{pb.alpha:.2f}",
        "nMoments": f"{sum(len(v['theta']) + len(v['bands']) for v in data.values())}",
        "PfiveNaiveErr": f"{naive5:.1e}".replace("e-0", r"\times10^{-") + "}",
        "stepsN": f"{n75}", "stepsNeighty": f"{n80}", "stepsElections": f"{len(steps)}",
        "stepModel": f"{100 * m75:.1f}",
    }
    (HERE / "output" / "numbers.tex").write_text(
        "\n".join(f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in nums.items()) + "\n", encoding="utf-8")
    check(share.max() < 0.5, f"the jump is less than half of the group gap in every election "
          f"({100 * share.min():.0f}-{100 * share.max():.0f}%)")
    check(m75 < 0, f"P3 in the calibrated model (2016): extra fall of {100 * m75:.1f} pp between 74 and 75")
    print(dec.drop(columns="tag").round(3).assign(tag=dec.tag).to_string(index=False))

    # --- figures and numbers of the final presentation ------------------------
    import slide_figures  # noqa: E402
    slide_figures.main()

# =============================================================================
print("4. Remark (heterogeneity): sign of dtau/ds when P0(70) > 1/2")
import heterogeneity  # noqa: E402

ok_prod, ok_dphi, _ = heterogeneity.symbolic_check()
check(ok_prod and ok_dphi, "d/dz [z phi(z)] = phi(z)(1 - z^2) and phi'(z) = -z phi(z) (SymPy)")
z0_, v0_, z1_, P1s_ = heterogeneity.crossing(0.78)
check(abs(z1_ * norm.pdf(z1_) - v0_) < 1e-12 and z1_ > 1 and abs(P1s_ - 0.8938) < 1e-3,
      f"crossing for P0 = 0.78: z0 = {z0_:.4f}, z1* = {z1_:.4f}, P1* = {P1s_:.4f}")
het = heterogeneity.main()
check(all(np.sign(r_["E_bracket"]) == np.sign(r_["rep_bracket"]) for r_ in het.values()),
      "the rule on group averages gets the sign of the exact (citizen by citizen) effect in every election")
check(abs(het["2016_1V"]["dtau_ds"]) < 0.01,
      f"2016: the exact effect is close to zero (dtau/ds = {het['2016_1V']['dtau_ds']:+.4f})")

print("OK: every check passed")
