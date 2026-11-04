"""Calculus of voting with a life-cycle benefit, an AR(1) voting habit and a
compulsory-voting threshold at 70.

A citizen of age a votes in an election iff

    c_it < b(a) + lam * h_it + O_a * S_t,      O_a = 1[a < 70]
    b(a) = A x^alpha - kappa x^beta,           x = a / AGE_SCALE, 0 < alpha < 1 <= beta
    c_it = mu_t + eta_i + eps_it,              eta ~ N(0, omega), eps ~ N(0, 1 - omega)
    h_{i,t+1} = rho(a_it) h_it + v_it,         h = 0 before the first election

Elections are D = 5 years apart. A citizen first votes at an age between 18 and
22, so citizens of the same exact age share the ages at which they voted
before. The model is stationary within an election: a cross-section at t is
computed as if mu_t and S_t had always been in force (a declared
simplification).

The habit distribution is propagated on a grid with linear splitting, so P(a)
is a smooth function of the parameters (no simulation noise): the calibration
objective can be minimised with a gradient-based least-squares routine.
"""
from dataclasses import dataclass, field

import numpy as np
from scipy.special import ndtr

AGE_SCALE = 50.0      # b is written in x = a / 50 so that A and kappa are O(1)
D = 5                 # years between presidential elections
FIRST_AGE = 18
THRESHOLD = 70
AGES = np.arange(FIRST_AGE, 101)
N_NODES = 15          # Gauss-Hermite nodes for the persistent cost eta
N_GRID = 121          # habit grid


@dataclass
class Params:
    A: float = 2.0
    alpha: float = 0.5
    kappa: float = 1.0
    beta: float = 1.0
    lam: float = 0.0          # weight of the habit in the benefit
    rho0: float = 0.0         # habit persistence at 18
    rho1: float = 0.0         # rise of persistence between 18 and 100 (rho'(a) > 0 if > 0)
    omega: float = 0.5        # share of the cost variance that is persistent
    s0: float = 0.5           # non-monetary sanction (duty, procedures)
    q: float = 0.0            # weight of the fine, S_t = s0 + q * F_t (F in % of the UIT)
    mu: dict = field(default_factory=dict)   # cost level per election

    def rho(self, a):
        return np.clip(self.rho0 + self.rho1 * (np.asarray(a, float) - FIRST_AGE) / (100 - FIRST_AGE),
                       0.0, 0.98)

    def b(self, a):
        x = np.asarray(a, float) / AGE_SCALE
        return self.A * x ** self.alpha - self.kappa * x ** self.beta

    def peak_age(self):
        """Age that maximises b (Proposition 1)."""
        r = self.A * self.alpha / (self.kappa * self.beta)
        return AGE_SCALE * r ** (1.0 / (self.beta - self.alpha))


_gh_x, _gh_w = np.polynomial.hermite_e.hermegauss(N_NODES)
_gh_w = _gh_w / _gh_w.sum()


def _split_matrix(values, grid):
    """Matrix that sends a point mass at grid[g] to `values[g]`, split linearly
    between the two neighbouring grid points."""
    n = len(grid)
    dh = grid[1] - grid[0]
    pos = np.clip(values / dh, 0, n - 1 - 1e-12)
    lo = np.floor(pos).astype(int)
    frac = pos - lo
    M = np.zeros((n, n))
    M[np.arange(n), lo] += 1 - frac
    M[np.arange(n), np.minimum(lo + 1, n - 1)] += frac
    return M


def turnout_profile(p: Params, mu: float, S: float, voluntary_from=THRESHOLD,
                    return_parts=False):
    """P(a) for a in AGES, with O_a = 1[a < voluntary_from].

    voluntary_from=200 gives the counterfactual with compulsory voting at all
    ages; voluntary_from=0 the one with voluntary voting at all ages."""
    sd_eta, sd_eps = np.sqrt(p.omega), np.sqrt(1.0 - p.omega)
    eta = sd_eta * _gh_x                                  # (K,)
    rho_max = float(np.max(p.rho(AGES)))
    grid = np.linspace(0.0, 1.0 / (1.0 - rho_max) + 1e-9, N_GRID)
    P = np.empty(len(AGES))
    Ehab = np.empty(len(AGES))
    for r in range(D):                                    # entry age 18 + r
        dist = np.zeros((N_NODES, N_GRID))
        dist[:, 0] = 1.0                                  # h = 0 before the first vote
        for a in range(FIRST_AGE + r, AGES[-1] + 1, D):
            O = 1.0 if a < voluntary_from else 0.0
            z = (p.b(a) + p.lam * grid[None, :] + O * S - mu - eta[:, None]) / sd_eps
            pv = ndtr(z)                                  # (K, G) vote prob given eta, h
            i = a - FIRST_AGE
            P[i] = _gh_w @ (dist * pv).sum(axis=1)
            Ehab[i] = _gh_w @ (dist * grid[None, :]).sum(axis=1)
            rho = float(p.rho(a))
            M1 = _split_matrix(rho * grid + 1.0, grid)
            M0 = _split_matrix(rho * grid, grid)
            dist = (dist * pv) @ M1 + (dist * (1 - pv)) @ M0
    if return_parts:
        return P, Ehab
    return P


def tau70(p: Params, mu: float, S: float):
    """Causal effect at the threshold: same citizens at 70, with and without the
    obligation (their habit is the one accumulated under compulsion)."""
    i = THRESHOLD - FIRST_AGE
    P1 = turnout_profile(p, mu, S, voluntary_from=THRESHOLD + 1)[i]   # obliged at 70
    P0 = turnout_profile(p, mu, S, voluntary_from=THRESHOLD)[i]
    return P1 - P0


def band_mean(P, weights, lo, hi):
    """Elector-weighted mean of P over exact ages lo..hi (weights: dict age->w)."""
    ages = [a for a in range(lo, min(hi, AGES[-1]) + 1) if weights.get(a, 0) > 0]
    w = np.array([weights[a] for a in ages])
    return float(w @ P[np.array(ages) - FIRST_AGE] / w.sum())


def gap(p: Params, mu: float, S: float, weights):
    """Observed-type gap Delta = mean P(60-69) - mean P(70+), and its
    decomposition into causal jump, ageing and habit decay."""
    P, _ = turnout_profile(p, mu, S, return_parts=True)
    delta = band_mean(P, weights, 60, 69) - band_mean(P, weights, 70, 130)
    t70 = tau70(p, mu, S)
    # ageing only: voluntary 70+ with the habit frozen at its 70 level is not a
    # model object; use the no-habit-loss counterfactual: everyone keeps voting
    # under compulsion in the history, voluntary only in the current election.
    P_frozen = _voluntary_today_only(p, mu, S)
    ageing = (band_mean(P, weights, 60, 69) - band_mean(P_frozen, weights, 70, 130)) - t70
    habit = band_mean(P_frozen, weights, 70, 130) - band_mean(P, weights, 70, 130)
    return {"Delta": delta, "tau70": t70, "ageing": ageing, "habit_decay": habit}


def _voluntary_today_only(p: Params, mu: float, S: float):
    """P(a) for a >= 70 if the citizen had been obliged in all PAST elections and
    is free only today: removes the habit-decay channel, keeps ageing."""
    P_comp, _ = turnout_profile(p, mu, S, voluntary_from=200, return_parts=True)
    # same histories as under compulsion, but today's obligation removed:
    sd_eta, sd_eps = np.sqrt(p.omega), np.sqrt(1.0 - p.omega)
    eta = sd_eta * _gh_x
    rho_max = float(np.max(p.rho(AGES)))
    grid = np.linspace(0.0, 1.0 / (1.0 - rho_max) + 1e-9, N_GRID)
    out = np.empty(len(AGES))
    for r in range(D):
        dist = np.zeros((N_NODES, N_GRID)); dist[:, 0] = 1.0
        for a in range(FIRST_AGE + r, AGES[-1] + 1, D):
            z_today = (p.b(a) + p.lam * grid[None, :] + (S if a < THRESHOLD else 0.0)
                       - mu - eta[:, None]) / sd_eps
            out[a - FIRST_AGE] = _gh_w @ (dist * ndtr(z_today)).sum(axis=1)
            z_hist = (p.b(a) + p.lam * grid[None, :] + S - mu - eta[:, None]) / sd_eps
            pv = ndtr(z_hist)
            rho = float(p.rho(a))
            dist = (dist * pv) @ _split_matrix(rho * grid + 1.0, grid) \
                + (dist * (1 - pv)) @ _split_matrix(rho * grid, grid)
    return out
