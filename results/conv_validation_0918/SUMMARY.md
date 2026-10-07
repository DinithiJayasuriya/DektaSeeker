# Converter validation, 2026-09-18

Three things, all on the existing converter results. No new search, no new figure.

Circuit naming. The paper's converter **(a)** is `conv_g20_v6_s0` discovered **#09**, which is
`mech_verify.md` case **"d"** and key `"b"` in `discovered_converters_table.json` -- four different
letterings of one circuit:

```
Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 n8; Sa1 OUT n8; C1 OUT n8
```

`Sa1` and `C1` are in parallel between the inductor node `n8` and `OUT`. The paper reads that branch
as a new freewheel path for `L0`.

Panels **(b)** and **(c)** of the current figure are *not* from this run: they are
`conv_fnov_rule_s0` #00 and #01 (10 devices each, from the functional-novelty search). Only (a) is
one of the 15 corner-robust converters of `conv_g20_v6`.

---

## 1. Control: replace the `Sa1 || C1` branch with a wire

`converter/ablate_branch_a.py` -> `ablate_branch_a.{md,json}`. Every row is scored the way the run
scored circuits: `spec.evaluate_topology`, `eff_floor` 0.9, duty re-refined per circuit and per
corner, all 4 corners.

| variant | devices | feasible corners | eff median % | eff worst % | ripple max mV |
|---|---|---|---|---|---|
| (a) as discovered | 6 | 4/4 | 98.96 | 97.99 | 88 |
| **control: branch replaced by a wire (`n8` == `OUT`)** | **4** | **4/4** | **99.37** | **98.80** | **87** |
| parent #10271 (`C1` deleted, `Sa1` alone) | 5 | 0/4 | -- | -- | -- |
| `Sa1` deleted, `C1` alone in series | 5 | 0/4 | -- | -- | -- |
| textbook buck (discovered #02, a corpus circuit) | 4 | 4/4 | 99.37 | 98.80 | 87 |

**The good behaviour survives the ablation, and improves.** Shorting the branch costs two devices and
gains +0.41 pp median / +0.81 pp worst-corner efficiency. The control circuit is not merely
buck-like: `decode.canonical` makes it *identical* to the textbook buck, which is itself in the
LaMAGIC training set.

So the branch is not supplying a mechanism. It is a two-device detour around a wire, and the
6.5 A / 7.2 A current peaks through `C1` / `Sa1` at a 1 A load are the price of the detour.

The parent rows show why the branch looked essential: deleting either device alone breaks the
circuit (`Sa1` alone -> no freewheel path; `C1` alone -> a series capacitor blocks DC). Only deleting
*both* -- the ablation the paper did not run -- reveals the wire.

## 2. Sanity check: is `C1`'s 97 % conduction real?

`converter/switch_model_check.py` -> `switch_model_check.{md,json}`. The bench switch is an ngspice
`SW`: a voltage-controlled resistor with no body diode and no `Coss`. Two ways that model could
manufacture the number were tested -- off-state leakage, and the absence of a reverse path. The
diode is added to `Sa1` only; adding one to every switch in a single orientation shorts IN to ground
through `Sa0` + the `Sb0` diode, which says nothing about this circuit.

| switch model | U(C1) | I_rms(C1) A | I_rms(Sa1 body diode) A | child corners | parent corners |
|---|---|---|---|---|---|
| as run: ideal SW, Roff 1 MOhm | 0.97 | 1.467 | -- | 4/4 | 0/4 |
| Roff 10 kOhm (100x leakier) | 0.97 | 1.467 | -- | 4/4 | 0/4 |
| Roff 1 GOhm (1000x tighter) | 0.97 | 1.467 | -- | 4/4 | 0/4 |
| body diode on `Sa1`, blocking orientation | 0.97 | 1.467 | 0.004 | 4/4 | 0/4 |
| **body diode on `Sa1`, conducting orientation** | **0.97** | **1.466** | **0.003** | **4/4** | **4/4** |

**The 97 % is real.** `U(C1)` and `I_rms(C1)` do not move across a 10^5 range of switch off-resistance,
so it is not leakage; and a body diode on `Sa1` never takes over (3-4 mA, U = 0.00, 0.3 % of the load
current) because `C1` holds the branch voltage at 0.6 V peak, below the diode's forward drop. `C1`
really does carry the inductor current, because KCL leaves it nowhere else to go.

**The claim built on it does not survive.** The last column is the problem: with a body diode in the
conducting orientation, the **parent becomes feasible at 4/4 corners at 98.32 %**. The parent's 0/4
and its 813 kV spike -- the evidence for "the parent is not a converter without `C1`", and the basis
for the "new energy-transfer path" verdict in `mech_verify.md` -- exist only in a switch model with
no reverse path. Any real MOSFET, or a diode in that position, freewheels the parent perfectly well.
The LaMAGIC representation carries no device polarity, so the discovered graph does not pick an
orientation; both are legal realisations of it.

Combined with S1: `C1`'s conduction is real behaviour, but it is not a new mechanism. Under a
realistic switch the comparison `C1` wins is no longer "converter vs non-converter" but 98.96 % at
6 devices against 98.32 % at 5 -- and both lose to the wire of S1 at 99.37 % with 4 devices.

Incidental: at Roff 10 kOhm the circuit still meets spec but efficiency falls to 97.05 %, i.e. about
1.9 pp of the reported efficiency is a statement about the assumed off-state resistance.

## 3. All 15 corner-robust designs, classified

`converter/classify_15.py`, `corpus_after_prune.py`, `classify_15_report.py` ->
`classify_15_final.md`, `corpus_after_prune.md`, `classify_15.md`. Evidence per circuit: per-device
`I_rms` from a 0 V ammeter at the circuit's own refined nominal duty; exact WL-canonical isomorphism
against all 37,496 distinct LaMAGIC train/val/test topologies (`train_overlap.py` re-run 2026-09-18,
reproduces the 2026-09-13 result); a 4-corner re-score of each circuit with its zero-current devices
deleted.

| class | meaning | count |
|---|---|---|
| 1 | already in the LaMAGIC corpus | 2 |
| 2a | a corpus circuit + a floating loop (0.00000 A, dead in any bench) | 6 |
| 2b | a corpus circuit + capacitor(s) across the ideal input source (0.00000 A here) | 4 |
| 3 | a corpus circuit + an active device that rescales a passive or filters | 3 |
| 4 | a mechanism the corpus does not contain | **0** |

**12 of 15 are a LaMAGIC training circuit once devices measured at 0.00000 A are deleted** -- and the
match was checked by pulling the actual corpus netlist, not just by hash. The other 3 add one active
device: `s0#00`/`s0#01` put a second inductor in parallel with `L0` (the pair is one inductor of L/2
and DCR/2; the +0.23 pp is the halved winding resistance, already shown in `mech_verify.md` S8), and
`s0#08` adds an output filter capacitor that merges into the bench's own `Cout`.

The 6 of class 2a are the "6 redundant" the paper already reports. The 4 of class 2b are new to this
audit: capacitors that sit across the input rail and carry exactly zero current *because the bench
drives VIN from an ideal voltage source*. They are decoupling capacitors whose job this bench cannot
see -- worth stating that way rather than calling them dead.

### Converter (a) is in class 2b

`s0#09` is converter (a). Its only zero-current device is `C0` (`IN`-`0`), and **deleting it lands the
circuit in the training set**: the pruned form

```
Sb0 0 n7; Sa0 IN n7; L0 n7 n8; Sa1 OUT n8; C1 OUT n8
```

is isomorphic to LaMAGIC `train #23311` (5 copies), device for device, **including the
capacitor-in-parallel-with-a-switch branch**. The `Sa1 || C1` structure the paper presents as a
discovered energy-transfer path is already in the training corpus. The search's own addition on top
of that training circuit is a capacitor across an ideal source.

Both `+1` relations are true -- (a) is one device away from `#10271` (delete `C1`) and one device
away from `#23311` (delete `C0`) -- but only the second deletion removes a device that carries no
current.

---

## What needs changing in the paper

1. **Converter (a) cannot carry a discovery claim.** Its branch is in the corpus (S3), it is worse
   than a wire (S1), and the parent's failure is a switch-model artifact (S2).
2. **`results/conv_mech_verify/mech_verify.md`** case (d) verdict, "YES: new energy-transfer path
   (parent is not a converter without it)", is contradicted by S1 and S2 and should be revised.
3. **`results/conv_section.tex`** is stale in two ways: it describes four converters (a)-(d) rather
   than the current three, and its "What was found" paragraph makes the (d) claim that S1-S3 refute.
4. **The count "6 redundant"** should become 6 floating loops + 4 zero-current input capacitors, and
   the headline for this run is that **0 of 15 are a mechanism the corpus does not already contain**.
5. **Panels (b) and (c) are from a different run** (`conv_fnov_rule_s0`), so "the three converters"
   and "the 15 corner-robust designs" are not the same population; the text should say which run each
   figure panel comes from.

## Files

| file | what |
|---|---|
| `ablate_branch_a.{md,json}` | S1, the branch-to-wire control, 4 corners x 5 variants |
| `switch_model_check.{md,json}` | S2, 5 switch models x child/parent, waveforms + 4 corners |
| `classify_15_final.{md,json}` | S3, the classification table and per-device currents |
| `classify_15.{md,json}` | S3 raw: per-device currents, reduced-circuit 4-corner re-scores |
| `corpus_after_prune.{md,json}` | S3, corpus membership before/after pruning 0 A devices |
| `corpus_match_examples.json` | S3, the matching LaMAGIC netlist for each pruned circuit |
| `train_overlap_rerun.txt` | corpus overlap re-run, reproduces the 2026-09-13 table |

Scripts: `converter/{ablate_branch_a,switch_model_check,classify_15,classify_15_report,corpus_after_prune}.py`.
