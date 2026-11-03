"""Figures for the final presentation (slides/final.tex).

    python3 code/slide_figures.py        # also called at the end of code/verify.py

Two kinds of figure:
  * mechanics (habit paths, coupling, steps): ILLUSTRATIVE parameters chosen so
    that each mechanism is visible; the slides say so;
  * results (life cycle, the two objects, decomposition): the CALIBRATED model
    (code/output/params_M*.json) and the aggregate data in code/data/.
Writes code/figures/s_*.pdf.
"""
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import calibrate as cal
from model import D, FIRST_AGE, THRESHOLD, Params, _voluntary_today_only, band_mean, turnout_profile

HERE = Path(__file__).resolve().parent
FIG = HERE / "figures"
FIG.mkdir(exist_ok=True)

# slide palette (validated for colour-blind separation): blue = obliged,
# red = voluntary, amber = a third series; grays for data and the remainder
BLUE, RED, AMBER, GRAY, LIGHT = "#2E6FD8", "#C0392B", "#D98E04", "#7A8699", "#C9CFD8"
INK, INK2, GRID = "#222222", "#5B6170", "#E3E6EC"
W = 5.5   # inches: the text width of a 16:9 beamer frame, so fonts print at size

plt.rcParams.update({
    "font.size": 9, "axes.titlesize": 9, "axes.labelsize": 9, "xtick.labelsize": 8,
    "ytick.labelsize": 8, "legend.fontsize": 8, "legend.frameon": False,
    "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
    "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "lines.linewidth": 1.6, "lines.solid_capstyle": "round", "pdf.fonttype": 42,
    "mathtext.fontset": "dejavusans",
})

RUN = "2016_1V"   # running example in the slides: a typical election with a good fit


def save(fig, name):
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight", pad_inches=0.02,
                metadata={"CreationDate": None})   # same bytes on every run: no spurious diffs
    if os.environ.get("SLIDE_FIG_PREVIEW"):   # PNG copies to look at while editing
        fig.savefig(Path(os.environ["SLIDE_FIG_PREVIEW"]) / f"{name}.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def at(P, a):
    return P[np.asarray(a) - FIRST_AGE]


def illustrative(lam=0.5, rho0=0.6, rho1=0.0):
    """b(a) with its peak at 45 (alpha = 1/2, beta = 2), sd of the cost = 1."""
    kappa, alpha, beta, peak = 1.5, 0.5, 2.0, 45.0
    A = kappa * beta * (peak / 50) ** (beta - alpha) / alpha
    return Params(A=A, alpha=alpha, kappa=kappa, beta=beta, lam=lam, rho0=rho0, rho1=rho1, omega=0.5)


MU_I, S_I = 3.6, 0.5     # cost level and sanction of the illustrative economy


def citizen(p, mu, S, eta, z, entry=18, voluntary_from=THRESHOLD):
    """One citizen's votes and habit; z are standard normal transitory shocks."""
    ages = np.arange(entry, 96, D)
    h, H, V = 0.0, [], []
    for a, e in zip(ages, np.sqrt(1 - p.omega) * z):
        O = 1.0 if a < voluntary_from else 0.0
        v = float(e < p.b(a) + p.lam * h + O * S - mu - eta)
        H.append(h)
        V.append(v)
        h = float(p.rho(a)) * h + v
    return ages, np.array(H), np.array(V)


def mark_threshold(ax, label=True, top=None):
    ax.axvline(69.5, color=INK2, lw=0.8, ls=(0, (2, 2)), zorder=1)
    if label:
        ax.text(69.9, top if top is not None else ax.get_ylim()[1], "70", color=INK2, fontsize=8,
                va="top", ha="left")


# =============================================================================
def fig_theta_exact():
    prof = pd.read_csv(HERE / "data" / "theta_profiles.csv")
    prof = prof[prof.edad.between(20, 80)]
    fig, ax = plt.subplots(figsize=(W, 2.35))
    for t in cal.TAGS:
        if t != RUN:
            d = prof[prof.tag == t]
            ax.plot(d.edad, d.b, color=LIGHT, lw=1.0, zorder=2)
    d = prof[prof.tag == RUN]
    ax.fill_between(d.edad, d.b - 1.96 * d.se, d.b + 1.96 * d.se, color=BLUE, alpha=0.15, lw=0, zorder=3)
    ax.plot(d.edad, d.b, color=BLUE, lw=1.8, zorder=4)
    th = d.set_index("edad").b
    ax.annotate(f"salto en 70: {100 * th[70]:.0f} pp", xy=(70, th[70] / 2), xytext=(63, -0.2),
                fontsize=8, color=INK, ha="right", va="center",
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7, shrinkB=2))
    ax.annotate("", xy=(70, th[70]), xytext=(70, 0), arrowprops=dict(arrowstyle="->", color=INK, lw=1.0))
    slope = (th[80] - th[71]) / 9
    ax.annotate(f"luego {100 * slope:.1f} pp por año", xy=(76, th[76]), xytext=(63, -0.4),
                fontsize=8, color=INK, ha="right", va="center",
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7, shrinkB=2))
    ax.axhline(0, color=INK2, lw=0.6)
    ax.set_ylim(-0.55, 0.3)
    mark_threshold(ax, top=0.3)
    ax.set_xlabel("edad exacta")
    ax.set_ylabel("participación\nmenos la de 69 años")
    ax.legend(handles=[plt.Line2D([], [], color=BLUE, lw=1.8, label=f"{RUN.replace('_', ' ')} (IC 95% sombreado)"),
                       plt.Line2D([], [], color=LIGHT, lw=1.0, label="las otras 5 elecciones")],
              loc="upper left", ncol=2, handlelength=1.6)
    save(fig, "s_theta_exact")
    return {"runJump": f"{100 * th[70]:.0f}", "runSlope": f"{100 * slope:.1f}"}


def fig_lifecycle():
    cal.set_spec("main")
    p = cal.load_params("M2")
    a = np.linspace(18, 100, 300)
    x = a / 50
    ben, cost = p.A * x ** p.alpha, p.kappa * x ** p.beta
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(W, 2.2))
    ax1.fill_between(a, cost, ben, color=BLUE, alpha=0.10, lw=0)
    ax1.plot(a, ben, color=BLUE)
    ax1.plot(a, cost, color=RED)
    ax1.text(60, ben[np.searchsorted(a, 60)] + 1.5, r"lo que suma: $A\,a^{\alpha}$", color=INK, fontsize=8, ha="right")
    ax1.text(70, cost[np.searchsorted(a, 70)] - 9, r"lo que resta: $\kappa\,a^{\beta}$", color=INK, fontsize=8, ha="left")
    ax1.text(33, 11.5, "lo que se gana\n= la distancia", color=INK2, fontsize=7.5, ha="center", va="center")
    ax1.set_xlabel("edad")
    ax1.set_title("dos fuerzas que crecen con la edad", loc="left", color=INK)
    b = ben - cost
    astar = p.peak_age()
    ax2.plot(a, b, color=BLUE)
    ax2.plot([astar], [p.b(astar)], "o", color=BLUE, ms=6, mec="white", mew=1.5)
    ax2.annotate(f"$a^*$ = {astar:.0f} años", xy=(astar, p.b(astar)), xytext=(astar + 8, p.b(astar) + 0.25),
                 fontsize=8, color=INK, va="bottom")
    mark_threshold(ax2, label=False)
    ax2.text(70.8, 9.9, "70", color=INK2, fontsize=8)
    ax2.set_xlabel("edad")
    ax2.set_title(r"lo que se gana, $b(a)$: sube y luego baja", loc="left", color=INK)
    ax2.set_ylim(6.3, 11.9)
    fig.tight_layout(w_pad=2)
    save(fig, "s_lifecycle")


def fig_static_index():
    """Step 5: without habit, P(a) is the index b(a) + O_a S - mu passed through G."""
    cal.set_spec("main")
    data = cal.load_data()
    p = cal.load_params("M1")
    S, mu = p.s0 + p.q * data[RUN]["fine"], p.mu[RUN]
    ages = np.arange(40, 96)
    z = p.b(ages) + np.where(ages < THRESHOLD, S, 0.0) - mu
    zc = p.b(ages) + S - mu
    P = turnout_profile(p, mu, S)
    Pc = turnout_profile(p, mu, S, voluntary_from=200)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(W, 2.2))
    for ax, y, yc in ((ax1, z, zc), (ax2, at(P, ages), at(Pc, ages))):
        pre, post = ages < THRESHOLD, ages >= THRESHOLD
        ax.plot(ages[pre], y[pre], color=BLUE)
        ax.plot(ages[post], y[post], color=RED)
        ax.plot(ages[post], yc[post], color=BLUE, ls=(0, (3, 2)), lw=1.3)
        mark_threshold(ax, label=False)
        ax.set_xlabel("edad")
    ax1.set_title("lo que gana + sanción", loc="left", color=INK)
    ax1.annotate("", xy=(70.6, z[ages == 70][0]), xytext=(70.6, zc[ages == 70][0]),
                 arrowprops=dict(arrowstyle="->", color=INK, lw=1.0))
    ax1.text(72, (z[ages == 70][0] + zc[ages == 70][0]) / 2, "pierde la\nsanción $S$", fontsize=8, color=INK,
             va="center")
    ax2.set_title("participación", loc="left", color=INK)
    t70 = at(Pc, 70) - at(P, 70)
    ax2.annotate("", xy=(70.6, at(P, 70)), xytext=(70.6, at(Pc, 70)),
                 arrowprops=dict(arrowstyle="->", color=INK, lw=1.0))
    ax2.text(68.8, 0.74, rf"$\tau^{{70}}$ = {t70:.2f}", fontsize=8, color=INK, ha="right", va="center")
    ax2.annotate("si siguiera\nobligado", xy=(84, at(Pc, 84)), xytext=(85, 0.78), fontsize=8, color=INK2,
                 arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7, shrinkB=2))
    ax2.set_ylim(0, 1)
    fig.tight_layout(w_pad=2)
    save(fig, "s_static_index")


def fig_habit_paths():
    """Step 6: two citizens, same transitory shocks, different persistent cost."""
    p = illustrative()
    z = np.random.default_rng(11).standard_normal(20)
    fig, ax = plt.subplots(figsize=(W, 2.3))
    for eta, col, name in ((-0.3, BLUE, "A: costo persistente bajo"), (0.55, AMBER, "B: costo persistente alto")):
        ages, H, V = citizen(p, MU_I, S_I, eta, z)
        ax.plot(ages, H, color=col, lw=1.4, zorder=2)
        ax.scatter(ages[V == 1], H[V == 1], s=30, color=col, edgecolor="white", lw=1.2, zorder=3)
        ax.scatter(ages[V == 0], H[V == 0], s=30, facecolor="white", edgecolor=col, lw=1.4, zorder=3)
        ax.text(ages[-1] + 1.2, H[-1], name.split(":")[0], color=INK, fontsize=8, va="center")
    mark_threshold(ax, label=False)
    ax.text(70, -0.1, " libre desde 70", fontsize=8, color=INK2, va="bottom")
    ax.set_ylim(-0.15, 2.8)
    ax.set_xlim(16, 99)
    ax.set_xlabel("edad en cada elección (cada 5 años)")
    ax.set_ylabel("costumbre $h$")
    dot = dict(ls="none", marker="o", ms=5.5)
    ax.legend(handles=[plt.Line2D([], [], color=BLUE, lw=1.4, label="A: costo persistente bajo"),
                       plt.Line2D([], [], color=AMBER, lw=1.4, label="B: costo persistente alto"),
                       plt.Line2D([], [], color=INK2, mec="white", label="votó", **dot),
                       plt.Line2D([], [], mfc="white", mec=INK2, mew=1.4, label="no votó", **dot)],
              loc="lower left", bbox_to_anchor=(0, 1.0), ncol=4, handlelength=1.6, columnspacing=1.2,
              borderaxespad=0.2)
    save(fig, "s_habit_paths")


def fig_coupling():
    """Lemma 1: same citizen and shocks, observed regime vs compulsory forever."""
    p = illustrative()
    z = np.random.default_rng(7).standard_normal(20)
    eta = 0.4
    ages, Ho, Vo = citizen(p, MU_I, S_I, eta, z)
    _, Hc, Vc = citizen(p, MU_I, S_I, eta, z, voluntary_from=200)
    split = int(np.argmax(Vo != Vc))              # first election where the two worlds differ
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(W, 2.7), sharex=True,
                                   gridspec_kw={"height_ratios": [1, 1.7], "hspace": 0.15})
    # top: did the same person vote, in each world?
    for y, V, col in ((1, Vc, BLUE), (0, Vo, RED)):
        ax1.scatter(ages[V == 1], np.full((V == 1).sum(), y), s=34, color=col, edgecolor=col, lw=1.4, zorder=3)
        ax1.scatter(ages[V == 0], np.full((V == 0).sum(), y), s=34, facecolor="white", edgecolor=col, lw=1.4,
                    zorder=3)
    ax1.set_yticks([1, 0], ["si siguiera obligado", "vida real (libre desde 70)"])
    ax1.set_ylim(-0.6, 1.6)
    ax1.grid(False)
    ax1.spines["left"].set_visible(False)
    ax1.tick_params(axis="y", length=0)
    ax1.annotate(f"a los {ages[split]}: sin sanción no va; obligado, sí", xy=(ages[split] - 1, 0.5),
                 xytext=(ages[split] - 4, 0.5), fontsize=7.5, color=INK, va="center", ha="right",
                 arrowprops=dict(arrowstyle="->", color=INK2, lw=0.7))
    ax1.set_title("¿votó? (relleno = sí, vacío = no) — misma persona, mismos días buenos y malos",
                  loc="left", color=INK, fontsize=8)
    # bottom: the habit, identical until the worlds split, then always higher if obliged
    same = ages <= ages[split]
    ax2.plot(ages[same], Ho[same], color=INK2, lw=1.6)
    ax2.plot(ages[split:], Hc[split:], color=BLUE, lw=1.6)
    ax2.plot(ages[split:], Ho[split:], color=RED, lw=1.6)
    ax2.text(56, 1.5, "igual en los dos mundos", fontsize=7.5, color=INK2, ha="center")
    ax2.text(ages[-1] + 1.5, Hc[-1], "obligado", fontsize=7.5, color=INK, va="center")
    ax2.text(ages[-1] + 1.5, Ho[-1], "real", fontsize=7.5, color=INK, va="center")
    k = split + 1
    ax2.annotate("", xy=(ages[k], Ho[k]), xytext=(ages[k], Hc[k]),
                 arrowprops=dict(arrowstyle="<->", color=INK, lw=0.9, shrinkA=1, shrinkB=1))
    ax2.annotate("más costumbre\nsi siguiera obligado", xy=(ages[k] - 0.3, (Ho[k] + Hc[k]) / 2),
                 xytext=(ages[k] - 18, 0.6), fontsize=7.5, color=INK, va="center", ha="center",
                 arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7))
    for ax in (ax1, ax2):
        ax.axvline(69.5, color=INK2, lw=0.8, ls=(0, (2, 2)), zorder=1)
    ax2.set_ylim(-0.15, 2.8)
    ax2.set_xlim(14, 101)
    ax2.set_xticks(range(20, 100, 10))
    ax2.set_xlabel("edad en cada elección (cada 5 años)")
    ax2.set_ylabel("costumbre $h$")
    save(fig, "s_coupling")


def _calibrated_run():
    cal.set_spec("main")
    data = cal.load_data()
    p = cal.load_params("M2")
    d = data[RUN]
    S, mu = p.s0 + p.q * d["fine"], p.mu[RUN]
    P = turnout_profile(p, mu, S)
    Pc = turnout_profile(p, mu, S, voluntary_from=200)
    Pf = _voluntary_today_only(p, mu, S)
    return p, d, P, Pc, Pf


def fig_two_objects():
    p, d, P, Pc, Pf = _calibrated_run()
    w = d["weights"]
    m60, m70 = band_mean(P, w, 60, 69), band_mean(P, w, 70, 130)
    lev = {int(lo): v for lo, hi, v in d["bands"]}
    ages = np.arange(40, 96)
    pre, post = ages < THRESHOLD, ages >= THRESHOLD
    fig, ax = plt.subplots(figsize=(W, 2.45))
    ax.plot(ages[pre], at(P, ages[pre]), color=BLUE)
    ax.plot(ages[post], at(P, ages[post]), color=RED)
    ax.plot(ages[post], at(Pc, ages[post]), color=BLUE, ls=(0, (3, 2)), lw=1.3)
    ax.plot([60, 69.5], [m60, m60], color=INK, lw=2.2, solid_capstyle="butt")
    ax.plot([70, 95], [m70, m70], color=INK, lw=2.2, solid_capstyle="butt")
    ax.plot([64.75], [lev[60]], "D", color=GRAY, ms=5, mec="white", zorder=4)
    ax.plot([82.5], [lev[70]], "D", color=GRAY, ms=5, mec="white", zorder=4)
    ax.text(71, m70 - 0.025, "media 70+", fontsize=8, color=INK, va="top")
    ax.text(59.5, m60 + 0.03, "media 60–69", fontsize=8, color=INK, ha="right", va="bottom")
    t70 = at(Pc, 70) - at(P, 70)
    ax.annotate("", xy=(70.8, at(P, 70)), xytext=(70.8, at(Pc, 70)),
                arrowprops=dict(arrowstyle="->", color=INK, lw=1.0))
    ax.text(68.8, 0.76, rf"$\tau^{{70}}$ = {t70:.2f}", fontsize=8.5, color=INK, ha="right", va="center")
    ax.plot([69.5, 99], [m60, m60], color=INK2, lw=0.6, ls=(0, (1, 2)))
    ax.plot([95, 99], [m70, m70], color=INK2, lw=0.6, ls=(0, (1, 2)))
    ax.annotate("", xy=(98.5, m70), xytext=(98.5, m60), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.0))
    ax.text(99.3, (m60 + m70) / 2, rf"$\Delta$ = {m60 - m70:.2f}", fontsize=8.5, color=INK, va="center")
    ax.annotate("si siguiera\nobligado", xy=(84, at(Pc, 84)), xytext=(87, 0.72), fontsize=8, color=INK2,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7, shrinkB=2))
    ax.legend(handles=[plt.Line2D([], [], color=INK, lw=2.2, label="media del grupo, modelo M2"),
                       plt.Line2D([], [], color=GRAY, marker="D", ls="none", ms=5, mec="white",
                                  label="media del grupo, ONPE " + RUN.replace("_", " "))],
              loc="lower left", handlelength=1.6)
    mark_threshold(ax, label=False)
    ax.set_xlim(40, 105)
    ax.set_xticks(range(40, 100, 10))
    ax.set_ylim(0, 1.0)
    ax.set_xlabel("edad")
    ax.set_ylabel("participación")
    save(fig, "s_two_objects")


def fig_p3_decomp():
    """Proposition 3 on the calibrated model: Delta = E1 + tau + E2 + D, drawn as a
    waterfall at the very levels of the curves."""
    p, d, P, Pc, Pf = _calibrated_run()
    w = d["weights"]
    m60, m70, mf70 = band_mean(P, w, 60, 69), band_mean(P, w, 70, 130), band_mean(Pf, w, 70, 130)
    P1_70, Pf_70 = at(Pc, 70), at(Pf, 70)
    ages = np.arange(55, 96)
    pre, post = ages < THRESHOLD, ages >= THRESHOLD
    fig, ax = plt.subplots(figsize=(W, 2.5))
    ax.plot(ages[pre], at(P, ages[pre]), color=BLUE)
    ax.plot([69, 70], [at(P, 69), P1_70], color=BLUE, ls=(0, (3, 2)), lw=1.3)
    ax.plot([70], [P1_70], "o", color=BLUE, ms=4.5, mec="white", mew=1.0)
    ax.annotate("a los 70,\nsi siguiera obligado", xy=(70, P1_70), xytext=(57, 0.66), fontsize=8, color=INK,
                va="center", arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7, shrinkB=3))
    ax.plot(ages[post], at(Pf, ages[post]), color=AMBER, lw=1.5, ls=(0, (3, 1.5)))
    ax.plot(ages[post], at(P, ages[post]), color=RED)
    ax.annotate("libre hoy, pero\ncon su costumbre\nde obligado", xy=(86, at(Pf, 86)), xytext=(97.5, 0.38),
                fontsize=8, color=INK, va="center",
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7, shrinkB=2))
    ax.annotate("lo observado", xy=(90, at(P, 90)), xytext=(97.5, 0.14), fontsize=8, color=INK, va="center",
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7, shrinkB=2))
    ax.plot([60, 69.5], [m60, m60], color=INK, lw=2.2, solid_capstyle="butt")
    ax.plot([70, 95], [m70, m70], color=INK, lw=2.2, solid_capstyle="butt")
    ax.text(59.5, m60 - 0.03, "promedio\n60–69", fontsize=8, color=INK, ha="right", va="top")
    ax.text(84, m70 + 0.02, "promedio 70+", fontsize=8, color=INK, va="bottom")
    # waterfall column right of the curves: from the 60-69 mean down to the 70+ mean
    x0, wd = 98, 2.4
    pieces = [(m60, P1_70, LIGHT, "edad, dentro de 60–69"),
              (P1_70, Pf_70, BLUE, "salto por la obligación"),
              (Pf_70, mf70, LIGHT, "edad, dentro de 70+"),
              (mf70, m70, AMBER, "costumbre perdida")]
    ylab, last = [], None
    for top, bot, *_ in pieces:          # label heights, at least 0.075 apart
        y = (top + bot) / 2 if last is None else min((top + bot) / 2, last - 0.075)
        ylab.append(y)
        last = y
    for (top, bot, col, lab), y in zip(pieces, ylab):
        ax.bar(x0, top - bot, bottom=bot, width=wd, color=col, edgecolor="white", lw=1.0, align="edge")
        ax.annotate(f"{lab}: {top - bot:.3f}", xy=(x0 + wd, (top + bot) / 2), xytext=(x0 + wd + 2.5, y),
                    fontsize=7.5, color=INK, va="center",
                    arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6, shrinkA=0, shrinkB=0))
    ax.plot([69.5, x0], [m60, m60], color=INK2, lw=0.6, ls=(0, (1, 2)))
    ax.plot([95, x0], [m70, m70], color=INK2, lw=0.6, ls=(0, (1, 2)))
    ax.text(x0 + wd / 2, m60 + 0.03, f"brecha = {m60 - m70:.3f}", fontsize=8, color=INK, ha="center", va="bottom")
    mark_threshold(ax, label=False)
    ax.set_xlim(55, 132)
    ax.set_xticks(range(55, 100, 5))
    ax.set_ylim(0.0, 1.02)
    ax.set_xlabel("edad")
    ax.set_ylabel("participación")
    ax.xaxis.set_label_coords((95 - 55) / 2 / (132 - 55), -0.12)
    ax.spines["bottom"].set_bounds(55, 95)
    save(fig, "s_p3_decomp")
    return {"runTau": f"{P1_70 - Pf_70:.3f}", "runDelta": f"{m60 - m70:.3f}", "runEone": f"{m60 - P1_70:.3f}",
            "runEtwo": f"{Pf_70 - mf70:.3f}", "runD": f"{mf70 - m70:.3f}"}


def _excluded(a1):
    """Ages a+1 at which one more past election enters (outside the identity)."""
    return (a1 - FIRST_AGE) % D == 0


def fig_p4_steps():
    """Proposition 4: the jump P(70) - P(69) comes back as a step in E[h] at 75,
    and through E[h] as steps in P at 75, 80, 85 (illustrative economy)."""
    a1 = np.arange(71, 91)                       # change between a1 - 1 and a1
    keep = ~_excluded(a1)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(W, 2.3))
    P, H = turnout_profile(illustrative(), MU_I, S_I, return_parts=True)
    ages = np.arange(60, 91)
    ax1.plot(ages, at(H, ages), color=RED, marker="o", ms=3.2, mec="white", mew=0.6, lw=1.2)
    ax1.annotate(f"escalón 74→75: {at(H, 75) - at(H, 74):.3f}\nsalto 69→70: {at(P, 70) - at(P, 69):.3f}",
                 xy=(74.6, (at(H, 75) + at(H, 74)) / 2), xytext=(61, at(H, 88)), fontsize=8, color=INK,
                 va="center", arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7, shrinkB=2))
    ax1.axvline(69.5, color=INK2, lw=0.8, ls=(0, (2, 2)))
    ax1.set_title("costumbre promedio por edad", loc="left", color=INK)
    for lam, col, ls in ((0.5, RED, "-"), (0.0, GRAY, (0, (3, 2)))):
        P = turnout_profile(illustrative(lam=lam), MU_I if lam else MU_I - 1.1, S_I)
        dP = np.where(keep, at(P, a1) - at(P, a1 - 1), np.nan)
        ax2.plot(a1, dP, color=col, ls=ls, lw=1.2, marker="o", ms=3.2, mec="white", mew=0.6,
                 label="sin costumbre" if lam == 0 else "con costumbre")
    ax2.set_title("cambio de la participación\nde un año al siguiente", loc="left", color=INK)
    ax2.legend(loc="upper right", handlelength=1.6, borderaxespad=0.1, fontsize=7.5)
    for s in (75, 80, 85, 90):
        for ax in (ax1, ax2):
            ax.axvspan(s - 0.6, s + 0.6, color=GRID, lw=0, zorder=0)
    ax1.set_xticks([60, 65, 70, 75, 80, 85, 90])
    ax1.set_xlim(59.5, 90.8)
    ax2.set_xticks([75, 80, 85, 90])
    ax2.set_xlim(70.5, 90.8)
    for ax in (ax1, ax2):
        ax.set_xlabel("edad $a$")
    fig.tight_layout(w_pad=2)
    save(fig, "s_p4_steps")


def fig_p5_rho():
    pc, pr = illustrative(rho0=0.5), illustrative(rho0=0.5, rho1=0.4)
    (Pc, Hc), (Pr, Hr) = (turnout_profile(x, MU_I, S_I, return_parts=True) for x in (pc, pr))
    ages = np.arange(18, 96)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(W, 2.2), gridspec_kw={"width_ratios": [1.35, 1]})
    ax1.plot(ages, at(Hc, ages), color=BLUE, label="se borra igual a toda edad")
    ax1.plot(ages, at(Hr, ages), color=AMBER, label="se borra más lento con la edad")
    ax1.axvspan(60, 69.5, color=GRID, lw=0, zorder=0)
    ax1.text(64.7, 0.2, "60–69", fontsize=7.5, color=INK2, ha="center")
    mark_threshold(ax1, label=False)
    ax1.set_title("costumbre promedio por edad", loc="left", color=INK)
    ax1.set_xlabel("edad")
    ax1.legend(loc="upper left")
    ax1.set_ylim(0, 4.6)
    steps = [75, 80, 85, 90]
    rel = lambda H: np.array([at(H, s) - at(H, s - 1) for s in steps]) / (at(H, 75) - at(H, 74))
    x = np.arange(len(steps))
    ax2.bar(x - 0.19, rel(Hc), width=0.36, color=BLUE, edgecolor="white", lw=1.0)
    ax2.bar(x + 0.19, rel(Hr), width=0.36, color=AMBER, edgecolor="white", lw=1.0)
    ax2.set_xticks(x, [str(s) for s in steps])
    ax2.set_title("tamaño de cada escalón\n(el de los 75 = 1)", loc="left", color=INK)
    ax2.set_xlabel("edad del escalón")
    ax2.set_ylim(0, 1.15)
    fig.tight_layout(w_pad=1.5)
    save(fig, "s_p5_rho")


def fig_decomp_bars():
    dec = pd.read_csv(HERE / "output" / "gap_decomposition.csv")
    x = np.arange(len(dec))
    fig, ax = plt.subplots(figsize=(W, 2.3))
    wd = 0.5
    ax.bar(x, dec.tau70, width=wd, color=BLUE, edgecolor="white", lw=1.0, label=r"salto por la obligación $\tau^{70}$")
    ax.bar(x, dec.ageing, bottom=dec.tau70, width=wd, color=LIGHT, edgecolor="white", lw=1.0,
           label="diferencia de edad entre grupos")
    ax.bar(x, dec.habit_decay, bottom=dec.tau70 + dec.ageing, width=wd, color=AMBER, edgecolor="white", lw=1.0,
           label="costumbre perdida")
    ax.plot(x, dec.Delta_data, "D", color=INK, ms=4.5, mec="white", label="brecha en los datos (ONPE)")
    ax.set_xticks(x, [f"{t.replace('_', ' ')}\n{100 * r.tau70 / r.Delta:.0f}%" for t, r in zip(dec.tag, dec.itertuples())])
    ax.text(-0.72, -0.105, "salto / brecha:", transform=ax.get_xaxis_transform(), ha="right", va="center",
            fontsize=8, color=INK2)
    ax.set_ylabel("puntos de participación")
    ax.set_ylim(0, 0.5)
    ax.set_xlim(-0.6, len(dec) - 0.4)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=7.5, handlelength=1.2,
              columnspacing=1.2, borderaxespad=0.2)
    save(fig, "s_decomp_bars")


def fig_counter_p3():
    """Where I did not believe the AI (1): a* <= 60 and still Delta < tau70.
    Parameters from a random search like the one in verify.py (b peaks at 57,
    strong and persistent habit), with the 2016 elector weights."""
    from model import gap
    p = Params(A=2.87, alpha=0.633, kappa=1.433, beta=1.18, lam=0.79, rho0=0.93, omega=0.43)
    mu, S = 2.81, 0.72
    cal.set_spec("main")
    g = gap(p, mu, S, cal.load_data()[RUN]["weights"])
    if not (p.peak_age() <= 60 and g["Delta"] < g["tau70"]):
        raise SystemExit("slide_figures: the P3 counterexample no longer has a* <= 60 and Delta < tau70")
    Pc, Hc = turnout_profile(p, mu, S, voluntary_from=200, return_parts=True)
    P = turnout_profile(p, mu, S)
    ages = np.arange(40, 91)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(W, 2.2))
    b60 = p.b(60)
    idx = p.b(ages) + p.lam * at(Hc, ages)
    ax1.plot(ages, p.b(ages) - b60, color=GRAY, lw=1.4, ls=(0, (3, 2)),
             label=f"lo que se gana: máximo a los {p.peak_age():.0f}")
    ax1.plot(ages, idx - (b60 + p.lam * at(Hc, 60)), color=BLUE, label="lo que se gana + costumbre")
    ax1.axvspan(60, 69.5, color=GRID, lw=0, zorder=0)
    ax1.axhline(0, color=INK2, lw=0.6)
    ax1.legend(loc="lower left", bbox_to_anchor=(0, 1.0), handlelength=1.6, fontsize=7.5, borderaxespad=0.2)
    ax1.set_ylim(-1.6, 2.6)
    ax1.set_ylabel("razones para votar\n(0 = a los 60)")
    ax1.set_xlabel("edad")
    pre, post = ages < THRESHOLD, ages >= THRESHOLD
    ax2.plot(ages[pre], at(P, ages[pre]), color=BLUE)
    ax2.plot(ages[post], at(P, ages[post]), color=RED)
    ax2.plot(ages[post], at(Pc, ages[post]), color=BLUE, ls=(0, (3, 2)), lw=1.3)
    ax2.axvspan(60, 69.5, color=GRID, lw=0, zorder=0)
    ax2.set_title(f"brecha {g['Delta']:.3f} < salto {g['tau70']:.3f}", loc="left", color=INK)
    ax2.set_xlabel("edad")
    ax2.set_ylim(0, 1.0)
    for ax in (ax1, ax2):
        ax.axvline(69.5, color=INK2, lw=0.8, ls=(0, (2, 2)))
    fig.tight_layout(w_pad=2)
    save(fig, "s_counter_p3")
    return {"cxPeak": f"{p.peak_age():.0f}", "cxDelta": f"{g['Delta']:.3f}", "cxTau": f"{g['tau70']:.3f}"}


def fig_fine_theta():
    fines = pd.read_csv(HERE / "data" / "fines.csv").set_index("tag")["fine_pct_uit"]
    dec = pd.read_csv(HERE / "output" / "gap_decomposition.csv")
    fig, ax = plt.subplots(figsize=(W * 0.75, 2.2))
    ax.grid(axis="x")
    left = {"2011_1V", "2016_1V"}            # these two sit at the same fine as 2026
    for r in dec.itertuples():
        f = fines[r.tag]
        ax.plot([f], [r.theta70_data], "o", color=BLUE, ms=6, mec="white", mew=1.2)
        ax.text(f - 0.07 if r.tag in left else f + 0.07, r.theta70_data, r.tag.replace("_", " "), fontsize=8,
                color=INK, va="center", ha="right" if r.tag in left else "left")
    ax.set_xlabel("multa media (% de la UIT)")
    ax.set_ylabel("salto a los 70 (datos)")
    ax.set_xlim(0.9, 4.7)
    ax.set_ylim(-0.13, -0.04)
    save(fig, "s_fine_theta")


def main():
    """Draw every slide figure and write the numbers the slides quote."""
    nums = {"runTag": RUN.replace("_", " ")}
    for fig_fn in (fig_theta_exact, fig_lifecycle, fig_static_index, fig_habit_paths, fig_coupling,
                   fig_two_objects, fig_p3_decomp, fig_p4_steps, fig_p5_rho, fig_decomp_bars, fig_counter_p3,
                   fig_fine_theta):
        nums.update(fig_fn() or {})
    (HERE / "output" / "slide_numbers.tex").write_text(
        "".join(f"\\newcommand{{\\{k}}}{{{v}}}\n" for k, v in nums.items()), encoding="utf-8")
    return nums


if __name__ == "__main__":
    nums = main()
    print(f"slide figures written to {FIG}: " + ", ".join(f"{k}={v}" for k, v in nums.items()))
