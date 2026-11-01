"""Single entry point: checks every claim of the paper and rebuilds its figures.

    python3 code/verify.py

Exits with an error (SystemExit) as soon as a claim does not hold.
  1. Symbolic (SymPy): Proposition 1 (life-cycle benefit) and the static
     comparative statics (a)-(d), including the threshold condition of (iv).
  2. Numerical (model.py): Propositions 2-5 with the AR(1) habit.
  3. Calibration: reloads code/output/params_M*.json, recomputes each
     objective from code/data/, checks the nesting M0 >= M1 >= M2 >= M3 and
     redraws the figures used in the paper and the slides.
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
print("2. Numerical checks of Propositions 2-5 (habit)")
W = {a_: 1.0 for a_ in range(18, 101)}


def random_params(n, lam_range=(0.2, 1.5), rho1=0.0):
    out = []
    while len(out) < n:
        p = Params(A=rng.uniform(2, 5), alpha=rng.uniform(0.2, 0.8), kappa=rng.uniform(1, 3),
                   beta=rng.uniform(1, 2.5), lam=rng.uniform(*lam_range), rho0=rng.uniform(0.2, 0.8),
                   rho1=rho1, omega=rng.uniform(0.2, 0.8))
        if p.peak_age() <= 60:                      # Proposition 3's condition
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

# P3: the hypothesis is on the TOTAL index b(a) + lam h, not on b alone.
#  (H) compulsory turnout non-increasing on [60, 70] and voluntary turnout with
#      a compulsory history non-increasing on [70, 100].
#  Then Delta >= tau70, ageing >= 0; habit decay >= 0 always (coupling).
from model import _voluntary_today_only  # noqa: E402

n_h, slack_h, slack_hab, found_counter = 0, [], [], 0
for p, mu_, S_ in random_params(150):
    g = gap(p, mu_, S_, W)
    slack_hab.append(g["habit_decay"])
    Pc = turnout_profile(p, mu_, S_, voluntary_from=200)          # compulsory at all ages
    Pf = _voluntary_today_only(p, mu_, S_)
    H_holds = (np.all(np.diff(Pc[60 - FIRST_AGE:71 - FIRST_AGE]) <= 1e-12)
               and np.all(np.diff(Pf[70 - FIRST_AGE:]) <= 1e-12))
    if H_holds:
        n_h += 1
        slack_h.append(min(g["Delta"] - g["tau70"], g["ageing"]))
    elif g["Delta"] < g["tau70"]:
        found_counter += 1
check(n_h > 30 and min(slack_h) > -1e-9,
      f"P3: under (H), Delta >= tau70 and ageing >= 0 on {n_h} draws (min slack {min(slack_h):.2e})")
check(min(slack_hab) > -1e-9, "P3: habit decay >= 0 on every draw (compulsory history dominates)")
check(found_counter > 0,
      f"P3: a* <= 60 alone is NOT enough -- {found_counter} draws with a* <= 60, (H) violated "
      "because the habit is still accumulating at 60-69, and Delta < tau70")

# P4: steps every D years in E[h] after 70; first step = P1(69) - P0(70), any rho
first_steps = []
for rho in (0.3, 0.6, 0.8):
    p = Params(A=3.0, alpha=0.5, kappa=1.8, beta=1.3, lam=0.6, rho0=rho, omega=0.5)
    P, H = turnout_profile(p, 1.0, 0.9, return_parts=True)
    step75 = P_at(H, 74) - P_at(H, 75)
    smooth = P_at(H, 73) - P_at(H, 74)
    first_steps.append(step75 / (P_at(P, 69) - P_at(P, 70)))
    check(step75 > 0 and abs(smooth) < 0.05 * step75,
          f"P4 (rho={rho}): E[h] drops {step75:.3f} between 74 and 75, only {smooth:+.4f} between 73 and 74")
check(all(abs(x - 1) < 0.05 for x in first_steps),
      f"P4: first step / (P1(69)-P0(70)) = {', '.join(f'{x:.3f}' for x in first_steps)} -- equal to the jump, any rho")
# P4 exact identity: H(a+1) - H(a) = sum_k rho^k [P(a+1-(k+1)d) - P(a-(k+1)d)]
p = Params(A=3.0, alpha=0.5, kappa=1.8, beta=1.3, lam=0.6, rho0=0.6, omega=0.5)
P, H = turnout_profile(p, 1.0, 0.9, return_parts=True)
worst = 0.0
for a_ in [a_ for a_ in range(25, 95) if (a_ + 1 - FIRST_AGE) % 5 != 0]:
    rhs = sum(0.6**k * (P_at(P, a_ + 1 - (k + 1) * 5) - P_at(P, a_ - (k + 1) * 5))
              for k in range(20) if a_ - (k + 1) * 5 >= FIRST_AGE)
    worst = max(worst, abs((P_at(H, a_ + 1) - P_at(H, a_)) - rhs))
check(worst < 1e-9, f"P4: exact identity for H(a+1) - H(a) at every age 25-94 (max error {worst:.1e})")
p_nohab = Params(A=3.0, alpha=0.5, kappa=1.8, beta=1.3, lam=0.0, rho0=0.6, omega=0.5)
Pn = turnout_profile(p_nohab, -0.3, 0.9)
d = np.diff(Pn[70 - FIRST_AGE:86 - FIRST_AGE])
check(np.ptp(d[3:6]) < 0.01, "P4: with lam = 0 the profile after 70 has no steps")

# P5: rho rising with age: same first step, slower decay, E[h] rises before 70
pc = Params(A=3.0, alpha=0.5, kappa=1.8, beta=1.3, lam=0.6, rho0=0.5, rho1=0.0, omega=0.5)
pr = Params(**{**pc.__dict__, "rho1": 0.4})
(Pc, Hc), (Pr, Hr) = (turnout_profile(x, -0.3, 0.9, return_parts=True) for x in (pc, pr))
s1c, s1r = P_at(Hc, 74) - P_at(Hc, 75), P_at(Hr, 74) - P_at(Hr, 75)
s2c, s2r = P_at(Hc, 79) - P_at(Hc, 80), P_at(Hr, 79) - P_at(Hr, 80)
check(s2r / s1r > s2c / s1c, f"P5: second/first step {s2r / s1r:.3f} (rho'>0) > {s2c / s1c:.3f} (rho const)")
check(P_at(Hr, 69) > P_at(Hr, 60) and abs(P_at(Hc, 69) - P_at(Hc, 60)) < 0.02,
      "P5: with rho'>0 the habit keeps rising between 60 and 69 (risk for a* <= 60)")
gc, gr = gap(pc, -0.3, 0.9, W), gap(pr, -0.3, 0.9, W)
check(gr["Delta"] >= gr["tau70"] and gc["Delta"] >= gc["tau70"], "P5: Delta >= tau70 also with rho'>0")
# P5 exact identity with rho(a) rising: Pi_m(a) = prod_{j=1..m} rho(a - j d),
#   H(a) = sum_k Pi_{k-1}(a) P(a - k d),
#   H(a+1) - H(a) = sum_k Pi_{k-1}(a+1) [P(a+1-kd) - P(a-kd)] + R(a),  R(a) >= 0.
# (the code's k >= 1 is the paper's k + 1)
# The first draft had no R(a): its error is measured and reported.
Pi = lambda p_, a_, m: float(np.prod([p_.rho(a_ - j * 5) for j in range(1, m + 1)]))
past = lambda a_: [k_ for k_ in range(1, 20) if a_ - k_ * 5 >= FIRST_AGE]
err_H = max(abs(P_at(Hr, a_) - sum(Pi(pr, a_, k_ - 1) * P_at(Pr, a_ - k_ * 5) for k_ in past(a_)))
            for a_ in range(FIRST_AGE, 101))
check(err_H < 1e-9, f"P5: H(a) = sum_k Pi_k(a) P(a-(k+1)d) at every age 18-100 (max error {err_H:.1e})")
worst5, naive5, minR = 0.0, 0.0, np.inf
for a_ in [a_ for a_ in range(25, 95) if (a_ + 1 - FIRST_AGE) % 5 != 0]:
    lhs = P_at(Hr, a_ + 1) - P_at(Hr, a_)
    main_ = sum(Pi(pr, a_ + 1, k_ - 1) * (P_at(Pr, a_ + 1 - k_ * 5) - P_at(Pr, a_ - k_ * 5)) for k_ in past(a_))
    R = sum((Pi(pr, a_ + 1, k_ - 1) - Pi(pr, a_, k_ - 1)) * P_at(Pr, a_ - k_ * 5) for k_ in past(a_))
    worst5, naive5, minR = max(worst5, abs(lhs - main_ - R)), max(naive5, abs(lhs - main_)), min(minR, R)
check(worst5 < 1e-9 and minR >= 0,
      f"P5: H(a+1) - H(a) = sum_k Pi_k(a+1) [one-year differences] + R(a), R(a) >= 0 "
      f"(max error {worst5:.1e}, min R {minR:.1e})")
check(naive5 > 1e-4, f"P5: the first draft's identity without R(a) is off by up to {naive5:.1e}")
w_jump = [Pi(pr, 70 + k_ * 5, k_ - 1) for k_ in (1, 2, 3, 4)]
check(all(w >= float(pr.rho(70)) ** (k_ - 1) for k_, w in zip((1, 2, 3, 4), w_jump)),
      "P5: weight of P(70)-P(69) in the step at 70+(k+1)d is >= rho(70)^k")
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

    # --- table: data vs model and decomposition of the gap ----------------------
    from model import _voluntary_today_only  # noqa: E402
    rows = []
    for t in TAGS:
        d = data[t]
        S_t = pred[t]["S"]
        g = gap(P_best, P_best.mu[t], S_t, d["weights"])
        lev = {int(lo): v for lo, hi, v in d["bands"]}
        delta_data = lev[60] - lev[70]
        th70_data = float(d["theta"][cal.FIT_AGES.index(70)])
        th70_model = float(pred[t]["theta"][cal.FIT_AGES.index(70)])
        Pc = turnout_profile(P_best, P_best.mu[t], S_t, voluntary_from=200)
        Pf = _voluntary_today_only(P_best, P_best.mu[t], S_t)
        H_ok = bool(np.all(np.diff(Pc[60 - FIRST_AGE:71 - FIRST_AGE]) <= 1e-12)
                    and np.all(np.diff(Pf[70 - FIRST_AGE:]) <= 1e-12))
        if H_ok:
            check(g["Delta"] >= g["tau70"] - 1e-9, f"{t}: (H) holds at the calibration and Delta >= tau70")
        else:
            print(f"  note {t}: (H) does not hold at the calibration; Proposition 3 does not apply")
        rows.append({"tag": t, "theta70_data": th70_data, "theta70_model": th70_model,
                     "Delta_data": delta_data, **{k_: float(v) for k_, v in g.items()}, "H": H_ok})
    dec = pd.DataFrame(rows)
    dec.to_csv(HERE / "output" / "gap_decomposition.csv", index=False)
    lines = [r"\begin{tabular}{lrrrrrrr}", r"\toprule",
             r" & \multicolumn{2}{c}{$\theta_{70}$} & \multicolumn{2}{c}{$\Delta$} & \multicolumn{3}{c}{Descomposición de $\Delta$ (modelo)} \\",
             r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-8}",
             r"Elección & datos & modelo & datos & modelo & $\tau^{70}$ & envejec. & hábito \\", r"\midrule"]
    for _, r_ in dec.iterrows():
        lines.append(f"{r_.tag.replace('_', ' ')} & {r_.theta70_data:.3f} & {r_.theta70_model:.3f} & "
                     f"{r_.Delta_data:.3f} & {r_.Delta:.3f} & {r_.tau70:.3f} & {r_.ageing:.3f} & {r_.habit_decay:.3f} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (HERE / "output" / "gap_table.tex").write_text("\n".join(lines), encoding="utf-8")

    # --- numbers quoted in the text of the paper and the slides ---------------
    share = dec["tau70"] / dec["Delta"]
    pb, p1 = load_params(best), load_params(static)
    nums = {
        "tauShareMin": f"{100 * share.min():.0f}", "tauShareMax": f"{100 * share.max():.0f}",
        "tauMin": f"{dec.tau70.min():.2f}", "tauMax": f"{dec.tau70.max():.2f}",
        "DeltaDataMin": f"{dec.Delta_data.min():.2f}", "DeltaDataMax": f"{dec.Delta_data.max():.2f}",
        "habitDecayMax": f"{dec.habit_decay.max():.3f}",
        "objMzero": f"{objs['M0']:,.0f}".replace(",", "{,}"), "objMone": f"{objs['M1']:,.0f}".replace(",", "{,}"),
        "objBest": f"{objs[best]:,.0f}".replace(",", "{,}"), "bestModel": best,
        "betaStatic": f"{p1.beta:.2f}", "betaBest": f"{pb.beta:.2f}", "lamBest": f"{pb.lam:.2f}",
        "rhoBest": f"{pb.rho0:.2f}", "peakBest": f"{pb.peak_age():.0f}",
        "nMoments": f"{sum(len(v['theta']) + len(v['bands']) for v in data.values())}",
        "PfiveNaiveErr": f"{naive5:.1e}".replace("e-0", r"\times10^{-") + "}",
    }
    (HERE / "output" / "numbers.tex").write_text(
        "\n".join(f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in nums.items()) + "\n", encoding="utf-8")
    check(share.max() < 0.5, f"the causal jump is less than half of the model gap in every election "
          f"({100 * share.min():.0f}-{100 * share.max():.0f}%)")
    print(dec.drop(columns="tag").round(3).assign(tag=dec.tag).to_string(index=False))

print("OK: every check passed")
