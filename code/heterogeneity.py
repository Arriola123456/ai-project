"""Result (d), extended: the sign of d tau / d s when P0(70) > 1/2.

    python code/heterogeneity.py      # writes code/output/heterogeneity.txt
                                      # and code/figures/s_zphi.pdf

With eps = s u and u ~ N(0, 1), the jump of one citizen is
tau = Phi(z1) - Phi(z0), z0 = cbar / s, z1 = (cbar + S) / s, and
d tau / d s = -(1/s) [z1 phi(z1) - z0 phi(z0)]  (derivation, Step 6.6).
Since d/dz [z phi(z)] = phi(z) (1 - z^2), z phi(z) rises on [0, 1] and falls
on [1, inf), so the sign depends on where z0 and z1 sit relative to z = 1.

Three checks:
  (a) SymPy: d/dz [z phi(z)] = phi(z) (1 - z^2);
  (b) the crossing for P0 = 0.78: z0, z0 phi(z0), z1* > 1 with
      z1* phi(z1*) = z0 phi(z0), and P1* = Phi(z1*);
  (c) the result holds citizen by citizen (given eta and h70), so in the
      calibrated model M2 it is evaluated over the distribution of the
      70-year-olds, with s = sigma_eps = sqrt(1 - omega).
"""
from pathlib import Path

import numpy as np
import sympy as sp
from scipy.optimize import brentq
from scipy.special import ndtr, ndtri

import calibrate as cal
from model import AGES, D, FIRST_AGE, N_GRID, N_NODES, THRESHOLD, _gh_w, _gh_x, _split_matrix
import slide_figures as sf

HERE = Path(__file__).resolve().parent
P0_REF = 0.78        # P0(70) in the calibrated model, 2016 (Step 6.8)
PEAK = ndtr(1.0)     # z phi(z) peaks at z = 1, i.e. at a turnout of Phi(1)


def phi(z):
    return np.exp(-0.5 * np.asarray(z) ** 2) / np.sqrt(2 * np.pi)


def zphi(z):
    return np.asarray(z) * phi(z)


def symbolic_check():
    z = sp.symbols("z", real=True)
    ph = sp.exp(-z ** 2 / 2) / sp.sqrt(2 * sp.pi)
    lhs = sp.diff(z * ph, z)
    ok_prod = sp.simplify(lhs - ph * (1 - z ** 2)) == 0
    ok_dphi = sp.simplify(sp.diff(ph, z) + z * ph) == 0
    return ok_prod, ok_dphi, sp.factor(lhs)


def crossing(p0):
    """z0 = Phi^-1(p0) and the z1* > 1 with the same value of z phi(z)."""
    z0 = float(ndtri(p0))
    target = float(zphi(z0))
    if z0 >= 1:
        raise ValueError("p0 must be below Phi(1) for a crossing above z = 1")
    z1 = brentq(lambda z: zphi(z) - target, 1.0, 10.0, xtol=1e-14)
    return z0, target, z1, float(ndtr(z1))


def case_of(p0, p1):
    """Cases a)-d) of Step 6.8 bis, from the individual probabilities."""
    if p0 <= 0.5 < p1:
        return "a"
    if 0.5 < p0 and p1 <= PEAK:
        return "b"
    if p0 >= PEAK:
        return "c"
    if p0 < PEAK < p1 and p0 > 0.5:
        return "d"
    return "otro"     # p1 <= 0.5: both cut-offs below the median, not covered by a)-d)


def citizens_at_70(p, mu, S):
    """Mass of the 70-year-olds over (eta node, habit grid point), with their
    standardized cut-offs z0 (free) and z1 (obliged). The habit at 70 was built
    in the elections at 20, 25, ..., 65, all compulsory."""
    sd_eta, sd_eps = np.sqrt(p.omega), np.sqrt(1.0 - p.omega)
    eta = sd_eta * _gh_x
    grid = np.linspace(0.0, 1.0 / (1.0 - float(np.max(p.rho(AGES)))) + 1e-9, N_GRID)
    entry = FIRST_AGE + (THRESHOLD - FIRST_AGE) % D
    dist = np.zeros((N_NODES, N_GRID))
    dist[:, 0] = 1.0
    for a in range(entry, THRESHOLD, D):
        pv = ndtr((p.b(a) + p.lam * grid[None, :] + S - p_mu(mu) - eta[:, None]) / sd_eps)
        rho = float(p.rho(a))
        dist = (dist * pv) @ _split_matrix(rho * grid + 1.0, grid) \
            + (dist * (1 - pv)) @ _split_matrix(rho * grid, grid)
    mass = _gh_w[:, None] * dist
    z0 = (p.b(THRESHOLD) + p.lam * grid[None, :] - mu - eta[:, None]) / sd_eps
    z1 = z0 + S / sd_eps
    keep = mass > 1e-12
    return mass[keep], z0[keep], z1[keep], sd_eps


def p_mu(mu):
    return mu


def calibrated(tag, p, data):
    S = p.s0 + p.q * data[tag]["fine"]
    mu = p.mu[tag]
    m, z0, z1, s = citizens_at_70(p, mu, S)
    m = m / m.sum()
    p0, p1 = ndtr(z0), ndtr(z1)
    bracket = zphi(z1) - zphi(z0)          # d tau / d s = -(1/s) * bracket, citizen by citizen
    cases = np.array([case_of(a, b) for a, b in zip(p0, p1)])
    frac = {c: float(m[cases == c].sum()) for c in ("a", "b", "c", "d", "otro")}
    neg_in_d = float(m[(cases == "d") & (bracket > 0)].sum())
    P0, P1 = float(m @ p0), float(m @ p1)
    rep = float(zphi(ndtri(P1)) - zphi(ndtri(P0)))   # the rule applied to the averages
    return {
        "rep_bracket": rep,
        "tag": tag, "S": S, "s": s, "P0": float(m @ p0), "P1": float(m @ p1), "tau": float(m @ (p1 - p0)),
        "frac": frac, "d_negative": neg_in_d, "E_bracket": float(m @ bracket),
        "dtau_ds": float(-(m @ bracket) / s), "share_negative": float(m[bracket > 0].sum()),
    }


def figure(z0, z1):
    z = np.linspace(0, 3, 400)
    fig, ax = sf.plt.subplots(figsize=(sf.W * 0.62, 2.3))
    ax.plot(z, zphi(z), color=sf.BLUE)
    ax.axhline(zphi(z0), color=sf.INK2, lw=0.7, ls=(0, (1, 2)))
    ax.axvspan(z0, z1, color=sf.GRID, lw=0, zorder=0)
    for x, lab in ((z0, rf"$z_0$ = {z0:.3f}"), (z1, rf"$z_1^*$ = {z1:.3f}")):
        ax.axvline(x, color=sf.RED, lw=1.0, ls=(0, (3, 2)))
        ax.text(x + 0.04, 0.02, lab, fontsize=8, color=sf.INK, rotation=90, va="bottom")
    ax.plot([1], [zphi(1)], "o", color=sf.BLUE, ms=5, mec="white", mew=1.2)
    ax.annotate(rf"máximo: $z$ = 1 ($P$ = {PEAK:.3f})", xy=(1, zphi(1)), xytext=(1.6, 0.262),
                fontsize=8, color=sf.INK, va="center",
                arrowprops=dict(arrowstyle="-", color=sf.INK2, lw=0.7))
    ax.set_xlim(0, 3)
    ax.set_ylim(0, 0.29)
    ax.set_xlabel("$z$ (corte estandarizado)")
    ax.set_ylabel(r"$z\,\phi(z)$")
    sf.save(fig, "s_zphi")


def main():
    lines = []
    out = lines.append
    ok_prod, ok_dphi, expr = symbolic_check()
    out("(a) SymPy")
    out(f"    d/dz [z phi(z)] = {expr}")
    out(f"    igual a phi(z) (1 - z^2): {ok_prod};  phi'(z) = -z phi(z): {ok_dphi}")
    out(f"    z phi(z) alcanza su máximo en z = 1, participación Phi(1) = {PEAK:.6f}")

    z0, v0, z1, P1s = crossing(P0_REF)
    out("")
    out(f"(b) Cruce para P0 = {P0_REF}")
    out(f"    z0 = Phi^-1(P0)        = {z0:.6f}")
    out(f"    phi(z0)                = {phi(z0):.6f}")
    out(f"    z0 phi(z0)             = {v0:.6f}")
    out(f"    z1* > 1 (brentq)       = {z1:.6f}   (comprobación: z1* phi(z1*) = {zphi(z1):.6f})")
    out(f"    P1* = Phi(z1*)         = {P1s:.6f}")
    out(f"    tau* = P1* - P0        = {P1s - P0_REF:.6f}")

    cal.set_spec("main")
    p = cal.load_params("M2")
    data = cal.load_data()
    out("")
    out("(c) Modelo calibrado M2, ciudadanos de 70 años (resultado por ciudadano, dado eta y h70)")
    out(f"    s = sigma_eps = sqrt(1 - omega) = {np.sqrt(1 - p.omega):.4f}  (omega = {p.omega:.4f})")
    out("    casos: a) P0<=0.50<P1   b) 0.50<P0, P1<=0.841   c) P0>=0.841   d) 0.50<P0<0.841<P1   otro) P1<=0.50")
    out(f"    {'elección':9s} {'P0':>6s} {'P1':>6s} {'tau':>6s} {'a':>6s} {'b':>6s} {'c':>6s} {'d':>6s} {'otro':>6s}"
        f" {'d,neg':>6s} {'neg':>6s} {'E[z1f-z0f]':>11s} {'dtau/ds':>8s} {'regla':>8s}")
    res = {}
    for t in cal.TAGS:
        r = calibrated(t, p, data)
        res[t] = r
        f = r["frac"]
        out(f"    {t:9s} {r['P0']:6.3f} {r['P1']:6.3f} {r['tau']:6.3f} {f['a']:6.3f} {f['b']:6.3f} {f['c']:6.3f}"
            f" {f['d']:6.3f} {f['otro']:6.3f} {r['d_negative']:6.3f} {r['share_negative']:6.3f}"
            f" {r['E_bracket']:11.4f} {r['dtau_ds']:8.4f} {r['rep_bracket']:8.4f}")
    out("    d,neg: fracción en el caso d) con dtau/ds < 0;  neg: fracción total con dtau/ds < 0")
    out("    regla: z1 phi(z1) - z0 phi(z0) con z = Phi^-1 de los PROMEDIOS P0 y P1 (ciudadano representativo)")
    out("    E[z1f-z0f] > 0  <=>  dtau/ds < 0 (más heterogeneidad achica el salto)")
    r = res[sf.RUN]
    out("")
    out(f"    {sf.RUN}: P1(70) = {r['P1']:.3f} frente a P1* = {P1s:.3f} con P0 = {P0_REF}; "
        f"E[z1 phi(z1) - z0 phi(z0)] = {r['E_bracket']:.4f}, signo de dtau/ds: {'negativo' if r['E_bracket'] > 0 else 'positivo'}")

    figure(z0, z1)
    text = "\n".join(lines) + "\n"
    (HERE / "output" / "heterogeneity.txt").write_text(text, encoding="utf-8")
    nums = {"hetZzero": f"{z0:.3f}", "hetVzero": f"{v0:.3f}", "hetZone": f"{z1:.3f}", "hetPone": f"{P1s:.3f}",
            "hetPeak": f"{PEAK:.3f}", "hetRunPzero": f"{r['P0']:.2f}", "hetRunPone": f"{r['P1']:.3f}",
            "hetRunNeg": f"{100 * r['share_negative']:.0f}", "hetRunE": f"{r['E_bracket']:.4f}", "hetRunDtds": f"{r['dtau_ds']:.4f}",
            "hetRunCaseA": f"{100 * r['frac']['a']:.0f}", "hetRunCaseB": f"{100 * r['frac']['b']:.0f}",
            "hetRunCaseC": f"{100 * r['frac']['c']:.0f}", "hetRunCaseD": f"{100 * r['frac']['d']:.0f}",
            "hetRunCaseO": f"{100 * r['frac']['otro']:.0f}", "hetRunDneg": f"{100 * r['d_negative']:.0f}"}
    (HERE / "output" / "heterogeneity_numbers.tex").write_text(
        "".join(f"\\newcommand{{\\{k}}}{{{v}}}\n" for k, v in nums.items()), encoding="utf-8")
    print(text)
    return res


if __name__ == "__main__":
    main()
