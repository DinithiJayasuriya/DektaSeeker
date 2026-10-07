#!/usr/bin/env python3
"""Mechanism verification for the 4 child-vs-parent pairs of conv_g20_v6_s0.

For every circuit (child, parent, textbook reference) at the run's nominal point and the child's own
refined duty this measures, per element, from the last 20 switching periods of the same ngspice deck
the bench uses (plus 0 V probe sources in series with each switch):
    RMS / peak / mean current, utilisation U = fraction of the period with |i| > 1 % of I_load,
    peak voltage stress, dissipated power <v*i>  (conduction + ESR; switches are ideal SW models so no
    switching loss is modelled -- stated in the report),
    charge balance <i_C> for capacitors.
Then: a load-step transient (R_out 50 -> 25 -> 50 ohm), line/load sweeps, a +-tolerance grid, a C1-value
sweep for (d), and equivalent-circuit reductions (merge / remove / short the added device).

Outputs results/conv_mech_verify/{mech_verify.json, mech_verify.md, fig_*.png}.
"""
from __future__ import annotations
import os as _os, sys as _sys
_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), ".."))
_sys.path.insert(0, _os.path.join(_ROOT, "converter"))
import os, sys
import os, sys, re, json, tempfile, subprocess, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from multiprocessing import Pool
import numpy as np
import bench, spec

OUT = os.path.join(_ROOT, "results", "conv_mech_verify")
os.makedirs(OUT, exist_ok=True)
NG = bench.NGSPICE

CASES = {
 "a": dict(title="paralleled inductors, cap IN->OUT", added="L1", parent_id="train #9562",
           child="Sb0 n1 0; L0 n1 OUT; Sa0 IN n1; C0 IN OUT; L1 n1 OUT",
           parent="Sb0 n1 0; L0 n1 OUT; Sa0 IN n1; C0 IN OUT", duty=0.5016),
 "b": dict(title="switched output capacitor", added="C0", parent_id="train #19363",
           child="Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 OUT; Sb1 n0 OUT; C1 n0 0",
           parent="Sb0 0 n7; Sa0 IN n7; L0 n7 OUT; Sb1 n0 OUT; C1 n0 0", duty=0.5029),
 "c": dict(title="doubled series high-side switch", added="C0", parent_id="train #415",
           child="Sb0 0 n7; Sa0 n0 n7; L0 n7 OUT; C0 0 OUT; Sa1 n0 IN; Sb1 n0 OUT",
           parent="Sb0 0 n7; Sa0 n0 n7; L0 n7 OUT; Sa1 n0 IN; Sb1 n0 OUT", duty=0.5032),
 "d": dict(title="inductor to OUT through Sa1 || C1", added="C1", parent_id="train #10271",
           child="Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 n8; Sa1 OUT n8; C1 OUT n8",
           parent="Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 n8; Sa1 OUT n8", duty=0.5052),
 "ref": dict(title="textbook buck (train #6935)", added=None, parent_id="-",
           child="Sa0 n3 IN; Sb0 n3 0; L0 OUT n3; C0 0 IN", parent=None, duty=0.5029),
}
SHEET = spec.SpecSheet(eff_floor=0.9)

def parse(s): return [tuple(t.split()) for t in s.split("; ")]

# ----------------------------------------------------------------------------- probe deck
def probe_deck(netlist, duty, wr_path, params=None, overrides=None, t_end=None, t_start=None,
               pts=None, load_step=None):
    """bench.build_deck with (i) a 0 V source in series with every switch so i(VS#) exists,
    (ii) per-element value overrides {dev: {"L":..,"DCR":..,"C":..,"ESR":..} | "short" | "open"},
    (iii) an optional load step (t_on, width, R_parallel), (iv) wrdata of every element's v and i."""
    P = dict(VIN=bench.VIN, ROUT=bench.ROUT, FSW=bench.FSW, L=bench.L_VAL, C=bench.C_VAL, COUT=bench.COUT,
             RON=bench.RON, ROFF=bench.ROFF, DCR=bench.DCR, ESR=bench.ESR)
    if params: P.update({k: float(v) for k, v in params.items() if k in P})
    ov = overrides or {}
    T = 1.0 / P["FSW"]; ton = max(duty * T, 1e-9)
    pts = pts or bench.PTS_PER_PERIOD
    t_end = t_end if t_end is not None else bench.SETTLE_PERIODS * T
    t_start = t_start if t_start is not None else t_end - bench.MEASURE_PERIODS * T
    L = ["* mech_verify probe deck", f"Vin VIN 0 DC {P['VIN']}",
         f"Vpa PA 0 PULSE(0 1 0 1n 1n {ton:.9g} {T:.9g})", f"Vpb PB 0 PULSE(1 0 0 1n 1n {ton:.9g} {T:.9g})",
         f".model SWMOD SW(ron={P['RON']} roff={P['ROFF']} vt=0.5 vh=0.01)"]
    elems = []   # (dev, kind, a, b, ivec, vexpr)
    ns = nl = nc = 0
    for dev, a, b in netlist:
        a, b = bench._net(a), bench._net(b); o = ov.get(dev)
        if o == "open": continue
        if o == "short":
            L.append(f"Vsh_{dev} {a} {b} 0"); elems.append((dev, "short", a, b, f"i(vsh_{dev})")); continue
        o = o if isinstance(o, dict) else {}
        if dev.startswith("S"):
            ns += 1; ph = "PA" if dev.startswith("Sa") else "PB"
            L.append(f"S{ns} {a} sx{ns} {ph} 0 SWMOD"); L.append(f"VS{ns} sx{ns} {b} 0")
            elems.append((dev, "S", a, b, f"i(vs{ns})"))
        elif dev.startswith("L"):
            nl += 1
            L.append(f"L{nl} {a} lx{nl} {o.get('L', P['L'])}"); L.append(f"RL{nl} lx{nl} {b} {o.get('DCR', P['DCR'])}")
            elems.append((dev, "L", a, b, f"i(l{nl})"))
        elif dev.startswith("C"):
            nc += 1
            L.append(f"C{nc} {a} cx{nc} {o.get('C', P['C'])}"); L.append(f"VC{nc} cx{nc} cy{nc} 0")
            L.append(f"RC{nc} cy{nc} {b} {o.get('ESR', P['ESR'])}")
            elems.append((dev, "C", a, b, f"i(vc{nc})"))
    L.append(f"Rout VOUT 0 {P['ROUT']}")
    L.append(f"Cout VOUT co_x {P['COUT']}"); L.append(f"VCo co_x co_y 0"); L.append(f"RCo co_y 0 {P['ESR']}")
    if load_step:
        t_on, width, rpar = load_step
        L.append(f"Rst VOUT st_x {rpar}"); L.append(f"Sst st_x 0 PST 0 SWMOD")
        L.append(f"Vst PST 0 PULSE(0 1 {t_on:.9g} 1n 1n {width:.9g} 1)")
    nodes = sorted({n for e in elems for n in (e[2], e[3]) if n != "0"} | {"VIN", "VOUT"})
    vecs = ["v(VOUT)", "i(vin)", "i(vco)"] + [e[4] for e in elems] + [f"v({n})" for n in nodes]
    L += [".options gmin=1e-12 reltol=1e-3 abstol=1e-9 vntol=1e-6 itl1=200 itl4=100",
          ".control", "set noaskquit", "set wr_singlescale", "set wr_vecnames",
          f"tran {T/pts:.9g} {t_end:.9g} {t_start:.9g} {T/pts:.9g}",
          f"wrdata {wr_path} " + " ".join(vecs), "quit", ".endc", ".end"]
    return "\n".join(L) + "\n", elems, P

def run_probe(netlist, duty, timeout=300, **kw):
    with tempfile.TemporaryDirectory() as td:
        wr = os.path.join(td, "w.txt"); deck = os.path.join(td, "c.sp")
        text, elems, P = probe_deck(netlist, duty, wr, **kw)
        open(deck, "w").write(text)
        p = subprocess.run([NG, "-b", deck], capture_output=True, text=True, timeout=timeout)
        if not os.path.exists(wr):
            return None, elems, P, (p.stdout + p.stderr)[-300:]
        with open(wr) as f:
            hdr = f.readline().split()
        data = np.loadtxt(wr, skiprows=1)
        cols = {h.lower(): data[:, i] for i, h in enumerate(hdr)}
        return cols, elems, P, ""

def vnode(cols, n): return cols.get(f"v({n.lower()})", np.zeros_like(cols["time"])) if n != "0" else np.zeros_like(cols["time"])

def trapz_mean(t, y):
    return float(np.trapz(y, t) / (t[-1] - t[0]))

def element_stats(cols, elems, P):
    t = cols["time"]; vout = cols["v(vout)"]
    Vo = trapz_mean(t, vout); Iload = Vo / P["ROUT"]; eps = 0.01 * Iload
    pin = trapz_mean(t, -P["VIN"] * cols["i(vin)"]); pout = trapz_mean(t, vout * vout / P["ROUT"])
    rows = []; total_loss = 0.0
    for dev, kind, a, b, iv in elems:
        i = cols[iv.lower()]; v = vnode(cols, a) - vnode(cols, b)
        Ploss = trapz_mean(t, v * i)
        w = np.diff(t); util = float(np.sum(w * (np.abs(i[:-1]) > eps)) / (t[-1] - t[0]))
        rows.append(dict(dev=dev, kind=kind, i_rms=float(np.sqrt(trapz_mean(t, i * i))), i_peak=float(np.max(np.abs(i))),
                         i_mean=float(trapz_mean(t, i)), i_rms_over_iload=float(np.sqrt(trapz_mean(t, i * i)) / Iload),
                         util=util, v_peak=float(np.max(np.abs(v))), p_loss=float(Ploss)))
        total_loss += Ploss
    p_cout = trapz_mean(t, cols["i(vco)"] ** 2) * P["ESR"]
    return dict(vout=Vo, iload=Iload, pin=pin, pout=pout, eff=pout / pin, ripple=float(vout.max() - vout.min()),
                loss_elements=total_loss, loss_cout_esr=p_cout, loss_pin_minus_pout=pin - pout, elements=rows)

# ----------------------------------------------------------------------------- jobs
def job_probe(args):
    key, role, txt, duty, tag, kw = args
    cols, elems, P, err = run_probe(parse(txt), duty, **kw)
    if cols is None: return key, role, tag, dict(error=err)
    return key, role, tag, element_stats(cols, elems, P)

def job_transient(args):
    key, role, txt, duty = args
    T = 1.0 / bench.FSW; t_on = 20e-3; width = 8e-3
    cols, elems, P, err = run_probe(parse(txt), duty, t_end=t_on + 2 * width, t_start=t_on - 0.4e-3, pts=60,
                                    load_step=(t_on, width, bench.ROUT))   # 50||50 = 25 ohm: load x2
    if cols is None: return key, role, dict(error=err)
    t = cols["time"]; v = cols["v(vout)"]
    def cyc_avg(t0, t1):   # per-period averages between t0 and t1
        edges = np.arange(t0, t1, T); out = []
        for e0, e1 in zip(edges[:-1], edges[1:]):
            m = (t >= e0) & (t < e1)
            if m.sum() > 2: out.append((0.5 * (e0 + e1), float(np.mean(v[m]))))
        return np.array(out)
    def edge_stats(t_edge, t_next):
        pre = float(np.mean(v[(t >= t_edge - 3 * T) & (t < t_edge)]))
        post_final = float(np.mean(v[(t >= t_next - 5 * T) & (t < t_next)]))
        seg = (t >= t_edge) & (t < t_next)
        vmin, vmax = float(v[seg].min()), float(v[seg].max())
        ca = cyc_avg(t_edge, t_next); band = 0.01 * abs(post_final)
        outside = np.where(np.abs(ca[:, 1] - post_final) > band)[0]
        t_settle = float(ca[outside[-1] + 1, 0] - t_edge) if len(outside) and outside[-1] + 1 < len(ca) else (0.0 if not len(outside) else float("nan"))
        return dict(v_pre=pre, v_post=post_final, undershoot=post_final - vmin, overshoot=vmax - post_final, settle_1pct_s=t_settle)
    return key, role, dict(step_up=edge_stats(t_on, t_on + width), step_down=edge_stats(t_on + width, t_on + 2 * width),
                           trace=dict(t=t[::20].tolist(), v=v[::20].tolist()))

def job_spec(args):
    key, role, txt, tag, params = args
    s = spec.evaluate_topology(parse(txt), SHEET, timeout_s=120.0, params=params)
    return key, role, tag, dict(feasible=bool(s.feasible), duty=s.duty, vout=s.vout, eff=s.eff, ripple=s.ripple, reason=s.reason)

def circuits():
    for k, c in CASES.items():
        yield k, "child", c["child"], c["duty"]
        if c["parent"]: yield k, "parent", c["parent"], c["duty"]

if __name__ == "__main__":
    probe_jobs, tran_jobs, spec_jobs = [], [], []
    for k, role, txt, D in circuits():
        probe_jobs.append((k, role, txt, D, "nominal", {}))
        tran_jobs.append((k, role, txt, D))
        for R in (200.0, 100.0, 50.0, 33.333):
            spec_jobs.append((k, role, txt, f"load_R{R:g}", dict(ROUT=R)))
        for V in (90.0, 110.0):
            spec_jobs.append((k, role, txt, f"line_V{V:g}", dict(VIN=V)))
        for (ls, cs, rs) in itertools.product((0.9, 1.1), (0.8, 1.2), (0.5, 2.0)):
            spec_jobs.append((k, role, txt, f"tol_L{ls}_C{cs}_R{rs}",
                              dict(L=bench.L_VAL * ls, C=bench.C_VAL * cs, COUT=bench.COUT * cs, RON=bench.RON * rs)))
    # (d): C1 value sweep at fixed duty, child only
    for sc in (0.1, 0.25, 0.5, 2.0, 4.0, 10.0):
        probe_jobs.append(("d", "child", CASES["d"]["child"], CASES["d"]["duty"], f"C1x{sc}",
                           dict(overrides={"C1": {"C": bench.C_VAL * sc}})))
    # (a): L1 value sweep (does the gain need matched inductors?)
    for sc in (0.5, 2.0):
        probe_jobs.append(("a", "child", CASES["a"]["child"], CASES["a"]["duty"], f"L1x{sc}",
                           dict(overrides={"L1": {"L": bench.L_VAL * sc}})))
    # equivalent-circuit reductions at the child's duty
    probe_jobs += [
        ("a", "parent", CASES["a"]["parent"], CASES["a"]["duty"], "merged_L0=250uH_DCR0.125",
         dict(overrides={"L0": {"L": bench.L_VAL / 2, "DCR": bench.DCR / 2}})),
        ("a", "parent", CASES["a"]["parent"], CASES["a"]["duty"], "merged_L0=250uH_DCR0.25",
         dict(overrides={"L0": {"L": bench.L_VAL / 2}})),
        ("c", "parent", CASES["c"]["parent"], CASES["c"]["duty"], "merged_Cout=20uF", dict(params=dict(COUT=2 * bench.COUT))),
        ("d", "child", CASES["d"]["child"], CASES["d"]["duty"], "C1_shorted", dict(overrides={"C1": "short"})),
        ("d", "child", CASES["d"]["child"], CASES["d"]["duty"], "Sa1_open", dict(overrides={"Sa1": "open"})),
        ("b", "child", CASES["b"]["child"], CASES["b"]["duty"], "C0_open", dict(overrides={"C0": "open"})),
        ("c", "child", CASES["c"]["child"], CASES["c"]["duty"], "Sb1_open", dict(overrides={"Sb1": "open"})),
    ]
    R = {k: dict(meta=c, probe={}, transient={}, spec={}) for k, c in CASES.items()}
    with Pool(40) as pool:
        for k, role, tag, rec in pool.imap_unordered(job_probe, probe_jobs):
            R[k]["probe"].setdefault(role, {})[tag] = rec; print("probe", k, role, tag, "ok" if "error" not in rec else rec["error"][:80], flush=True)
        for k, role, rec in pool.imap_unordered(job_transient, tran_jobs):
            R[k]["transient"][role] = rec; print("tran", k, role, "ok" if "error" not in rec else rec["error"][:80], flush=True)
        for k, role, tag, rec in pool.imap_unordered(job_spec, spec_jobs):
            R[k]["spec"].setdefault(role, {})[tag] = rec
    print("spec jobs done:", len(spec_jobs))
    json.dump(R, open(f"{OUT}/mech_verify.json", "w"), indent=1)
    print("saved", f"{OUT}/mech_verify.json")
