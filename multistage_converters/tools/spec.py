#!/usr/bin/env python3
"""v70 COPY (+ switch rating cap, CON_NAMES + "rating"). What counts as a good converter, and how a topology is scored.

The chain test exposed the degenerate solution of this domain: a topology that
simply wires VIN to VOUT measures efficiency 0.999 with zero ripple and is
completely insensitive to duty cycle. It converts nothing. Maximising efficiency
alone would hand the search a pass-through and call it a win -- the converter-side
analogue of the op-amp run that discovered the test bench's shunt resistors.

So feasibility is defined by CONVERSION, not by efficiency:

    feasible  <=>  |Vout - target| <= tol * |target|        at some duty
                   and ripple <= ripple_frac * |Vout|
                   and the topology actually responds to duty
                   and efficiency >= eff_floor                 (0 = off)

Objectives, minimised, in the same shape the op-amp side uses:

    [-efficiency, 1 - novelty]

with the conversion error handled as a constraint rather than an objective, so
the Pareto front is not filled with efficient circuits that miss the spec.

DUTY REFINEMENT (added for the search loop). LaMAGIC's five-point duty grid is
what the corpus was labelled on, but a converter is regulated by adjusting its
duty cycle, and a 2:1 step-down sits exactly on the D=0.5 grid point only for
a buck at nominal line. With the grid alone a buck fails the same spec at
VIN=90 V. So after the sweep, if the target lies between two adjacent grid
points, up to `refine_steps` secant steps on Vout(D) are simulated. That is
the converter's "inner sizing": duty is the one free operating variable.

CORNERS (robustness). The op-amp loop re-scores a topology on k fresh sizing
seeds; a converter has no sizing seeds, so k here indexes OPERATING CORNERS:
nominal, heavy load, light load, and low line with -20% passive tolerance. A
robust converter meets the spec (at its own duty) at every corner. `k` in the
fit dict means "corners evaluated" everywhere the op-amp code says "seeds".
"""
from __future__ import annotations

import os
import statistics as st
from dataclasses import dataclass, field

import bench

# LaMAGIC sweeps these five; the bench accepts any duty in (0, 1).
DUTY_VALUES = (0.1, 0.3, 0.5, 0.7, 0.9)
# dutyfloor fork (11/10): the duty cycle must stay inside [DUTY_MIN, 1 - DUTY_MIN] (minimum on-time AND off-time). Env CONV_DUTY_MIN,
# 0 = off = the v70 evaluator. A circuit whose target is only reachable outside the window fails on vout_error at the window edge.
DUTY_MIN = float(os.environ.get("CONV_DUTY_MIN", 0.0) or 0.0)

# Operating corners for the k-corner robustness re-score. Index 0 is the
# nominal point every in-loop evaluation uses. Load steps are the standard
# converter qualification; corner 3 combines a 10% line droop with -20% L/C.
CORNERS = (
    dict(name="nominal"),
    dict(name="heavy_load", ROUT=bench.ROUT / 2),
    dict(name="light_load", ROUT=bench.ROUT * 2),
    dict(name="low_line_tol", VIN=bench.VIN * 0.9, L=bench.L_VAL * 0.8,
         C=bench.C_VAL * 0.8, COUT=bench.COUT * 0.8),
)
CON_NAMES = ("vout_error", "ripple", "duty_response", "efficiency", "rating")   # v70: + switch rating


@dataclass
class SpecSheet:
    vin: float = 100.0
    target_vout: float = 50.0        # 2:1 step-down; a pass-through cannot pass
    tol: float = 0.05                # +-5% of target
    ripple_frac: float = 0.05        # <=5% of Vout, peak-to-peak
    # v70: fixed-ratio stages (switched-capacitor pre-dividers) are legitimate rungs and are duty-INDEPENDENT by design, so the
    # anti-passthrough rule is OFF by default on the rail (env CONV_MIN_DUTY_RESPONSE, volts; 0 = off). Conversion feasibility
    # (|Vout - target| <= tol, ripple, eff floor, switch rating) already excludes a wire: it cannot hit a target below Vin.
    min_duty_response: float = float(os.environ.get("CONV_MIN_DUTY_RESPONSE", 0.0) or 0.0)
    eff_floor: float = 0.0           # feasibility floor on efficiency (0 = off)
    duties: tuple = DUTY_VALUES
    refine_steps: int = 2            # secant steps on Vout(D) toward the target
    # v70: switch rating cap (V). A point is infeasible if any switch blocks more than this (peak |Vds|, bench.Result.stress).
    # 0 = off. Default from env CONV_RATING_MAX so the campaign driver / judge pick it up without a flag.
    rating_max: float = float(os.environ.get("CONV_RATING_MAX", 0.0) or 0.0)


@dataclass
class Score:
    feasible: bool
    reason: str = ""
    duty: float = float("nan")
    vout: float = float("nan")
    eff: float = float("nan")
    ripple: float = float("nan")
    duty_response: float = float("nan")
    passthrough: bool = False
    sweep: list = field(default_factory=list)   # [(duty, vout, eff, ripple)]
    con_vec: list = field(default_factory=list)  # violations >= 0, CON_NAMES order
    n_sims: int = 0
    stress_max: float = float("nan")             # v70: peak |Vds| at the reported duty
    stress_dev: str = ""

    def objectives(self):
        """Minimised. Matches the op-amp side's [-performance, 1-novelty] shape;
        novelty is appended by the caller, which owns the corpus."""
        return [-self.eff if self.feasible else 0.0]


def _violations(sheet, vout, ripple, response, eff, stress=float("nan")):
    """Graded distance to the spec, one non-negative term per constraint.
    Units are chosen so 1.0 means 'clearly violated' the way a 1 dB gain
    shortfall does on the op-amp side: percent of target for Vout, percentage
    points for ripple and efficiency, volts for duty response."""
    tgt = abs(sheet.target_vout)
    v_err = 100.0 * abs(vout - sheet.target_vout) / max(tgt, 1e-9)
    c_v = max(0.0, v_err - 100.0 * sheet.tol)
    r_frac = 100.0 * abs(ripple) / max(abs(vout), 1e-9)
    c_r = max(0.0, r_frac - 100.0 * sheet.ripple_frac)
    c_d = max(0.0, sheet.min_duty_response - response)
    c_e = max(0.0, 100.0 * (sheet.eff_floor - eff)) if sheet.eff_floor > 0 else 0.0
    cap = getattr(sheet, "rating_max", 0.0) or 0.0
    c_s = max(0.0, 100.0 * (stress - cap) / cap) if (cap > 0 and stress == stress) else 0.0   # % over the rating
    return [round(c_v, 4), round(c_r, 4), round(c_d, 4), round(c_e, 4), round(c_s, 4)]


def _refine(netlist, sheet, sweep, params, timeout_s, stress_of=None):
    stress_of = stress_of if stress_of is not None else {}
    """Secant steps on Vout(D) between the two grid points bracketing the target."""
    pts = sorted(sweep)
    tgt = sheet.target_vout
    brackets = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)
                if (pts[i][1] - tgt) * (pts[i + 1][1] - tgt) < 0]
    if brackets:
        # prefer the bracket whose better-efficiency endpoint is higher
        (d1, v1, e1, _), (d2, v2, e2, _) = max(brackets, key=lambda b: max(b[0][2], b[1][2]))
    else:
        # v70: high-ratio rungs sit BELOW the lowest grid duty (48:1 -> D ~ 0.02-0.04 while the grid starts at 0.1).
        # Extrapolate with a secant through the two points nearest the target (as the rulemaker evaluator does); the
        # loop below then brackets normally. Needs >= 2 points.
        near = sorted(pts, key=lambda s: abs(s[1] - tgt))[:2]
        if len(near) < 2:
            return []
        (d1, v1, e1, _), (d2, v2, e2, _) = sorted(near)
    extra = []
    for _ in range(int(sheet.refine_steps)):
        if abs(v2 - v1) < 1e-9:
            break
        d = d1 + (tgt - v1) * (d2 - d1) / (v2 - v1)
        d = min(max(d, max(0.005, DUTY_MIN)), min(0.99, 1.0 - DUTY_MIN))   # dutyfloor fork: refinement stays inside the duty window
        r = bench.evaluate(netlist, d, timeout_s=timeout_s, params=params)
        if not r.ok:
            break
        extra.append((round(d, 4), r.vout, r.eff, r.ripple))
        stress_of[round(d, 4)] = (r.stress_max, r.stress_dev)
        if abs(r.vout - tgt) <= sheet.tol * abs(tgt):
            break
        if (r.vout - tgt) * (v1 - tgt) < 0:
            d2, v2 = d, r.vout
        else:
            d1, v1 = d, r.vout
    return extra


def evaluate_topology(netlist, sheet: SpecSheet = None, timeout_s: float = 90.0,
                      params=None):
    """Sweep duty (+ refine toward the target), pick the best feasible operating
    point, diagnose the rest. `params` = bench operating-point override (a
    CORNERS entry); None = nominal."""
    sheet = sheet or SpecSheet()
    p = {k: v for k, v in (params or {}).items() if k != "name"} or None
    sweep, n_sims = [], 0
    stress_of = {}                                   # v70: duty -> (peak |Vds|, switch)
    for d in sheet.duties:
        r = bench.evaluate(netlist, d, timeout_s=timeout_s, params=p)
        n_sims += 1
        if r.ok:
            sweep.append((d, r.vout, r.eff, r.ripple))
            stress_of[d] = (r.stress_max, r.stress_dev)
    cap = sheet.rating_max or 0.0
    def _st(s):
        return stress_of.get(s[0], (float("nan"), ""))
    def _rated(s):
        sm = _st(s)[0]
        return cap <= 0 or (sm == sm and sm <= cap)
    if not sweep:
        return Score(False, reason="no duty simulated", sweep=[], n_sims=n_sims,
                     con_vec=[100.0, 100.0, sheet.min_duty_response, 100.0, 0.0])

    vouts = [v for _, v, _, _ in sweep]
    response = max(vouts) - min(vouts)
    # A pass-through is defined by behaviour, not by wiring: its output ignores
    # the switches entirely.
    passthrough = sheet.min_duty_response > 0 and response < sheet.min_duty_response
    if not passthrough and sheet.refine_steps > 0:
        extra = _refine(netlist, sheet, sweep, p, timeout_s, stress_of)
        n_sims += len(extra)
        sweep = sweep + extra

    if DUTY_MIN > 0:                                 # dutyfloor fork: points outside the duty window do not exist for the judge
        sweep = [s for s in sweep if DUTY_MIN - 1e-9 <= s[0] <= 1.0 - DUTY_MIN + 1e-9]
        if not sweep:
            return Score(False, reason="no duty inside the window simulated", sweep=[], n_sims=n_sims,
                         con_vec=[100.0, 100.0, sheet.min_duty_response, 100.0, 0.0])
    lo = sheet.target_vout * (1 - sheet.tol)
    hi = sheet.target_vout * (1 + sheet.tol)
    if sheet.target_vout < 0:
        lo, hi = hi, lo
    # A lossy converter cannot exceed unity efficiency: points above 1.0 are the bench's
    # measurement artefact (input-current sampling / settling), not a discovery. They are
    # dropped from the feasible set so an unphysical point can never win the objective.
    art = [s for s in sweep if s[2] > 1.0]
    conv_ok = [s for s in sweep if lo <= s[1] <= hi
               and s[3] <= sheet.ripple_frac * abs(s[1])
               and (sheet.eff_floor <= 0 or s[2] >= sheet.eff_floor)
               and s[2] <= 1.0]
    ok = [s for s in conv_ok if _rated(s)]          # v70: conversion-feasible AND every switch within its rating

    if passthrough:
        d, v, e, rp = max(sweep, key=lambda s: s[2])
        sm, sd = _st((d, v, e, rp))
        return Score(False, "passthrough: output ignores duty", d, v, e, rp,
                     response, True, sweep, _violations(sheet, v, rp, response, e, sm), n_sims, sm, sd)
    if conv_ok and not ok:
        # v70: converts fine but a switch is over-rated -> infeasible on 'rating' (graded by % over the cap)
        d, v, e, rp = max(conv_ok, key=lambda s: s[2]); sm, sd = _st((d, v, e, rp))
        return Score(False, f"rating: {sd} blocks {sm:.1f} V > {cap:g} V", d, v, e, rp, response, False, sweep,
                     _violations(sheet, v, rp, response, e, sm), n_sims, sm, sd)
    if not ok:
        # closest to the target by Vout; among near ones prefer the best efficiency
        clean = [s for s in sweep if s[2] <= 1.0] or sweep
        d, v, e, rp = min(clean, key=lambda s: (abs(s[1] - sheet.target_vout), -s[2]))
        near = abs(v - sheet.target_vout) <= hi - sheet.target_vout
        if art and near and e > sheet.eff_floor:
            why = f"efficiency above 100% at {len(art)} duty point(s): bench artefact"
        elif near and rp > sheet.ripple_frac * abs(v):
            why = "ripple"
        elif near:
            why = f"efficiency {e:.3f} below floor {sheet.eff_floor}"
        else:
            why = f"Vout {v:.1f} misses {sheet.target_vout}" + (f" with duty limited to [{DUTY_MIN:g}, {1 - DUTY_MIN:g}]" if DUTY_MIN > 0 else "")
        sm, sd = _st((d, v, e, rp))
        return Score(False, why, d, v, e, rp, response, False, sweep,
                     _violations(sheet, v, rp, response, e, sm), n_sims, sm, sd)

    d, v, e, rp = max(ok, key=lambda s: s[2])       # best efficiency among feasible
    sm, sd = _st((d, v, e, rp))
    return Score(True, "", d, v, e, rp, response, False, sweep, [0.0] * len(CON_NAMES), n_sims, sm, sd)


def summarise(scores):
    fe = [s for s in scores if s.feasible]
    pt = [s for s in scores if s.passthrough]
    out = [f"topologies scored : {len(scores)}",
           f"  feasible        : {len(fe)} ({100*len(fe)/max(len(scores),1):.0f}%)",
           f"  pass-through    : {len(pt)} ({100*len(pt)/max(len(scores),1):.0f}%)"]
    if fe:
        effs = sorted(s.eff for s in fe)
        out += [f"  efficiency among feasible: min {effs[0]:.3f} "
                f"median {st.median(effs):.3f} max {effs[-1]:.3f}"]
    return "\n".join(out)
