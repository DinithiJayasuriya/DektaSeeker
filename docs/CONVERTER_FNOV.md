# Converter search with FUNCTIONAL NOVELTY (built 2026-09-15)

Why: 117 feasible converters from every earlier run looked up to 3 device edits from the 37,496 LaMAGIC
topologies, but after pruning dead parts and merging series/parallel duplicates all were <= 1 away
(results/conv_novel_survey). The WL-cosine novelty objective rewarded padding.

## Metric (converter/conv_functional.py)
1. reduce_structural: dead (dangling / closed loop / off-rail), ideal_src_cap (C across IN-0), antiphase (Sa-Sb
   series, never conducts), always_on (Sa||Sb, a wire: nets contracted), parallel (same kind, same nets), series
   (same kind through a private 2-device net). The corpus is reduced the same way once: 37,496 -> 20,625 distinct.
2. distance = min(i + j) deleting i devices from the candidate and j from a reduced training topology to a common
   canonical circuit. i <= 4, j <= 3 => exact up to 4; reported 0..4 (`fd_ge` = at least 4).
   raw_distance = same on the unreduced circuit vs the unreduced corpus (novel_survey.py's number).
3. audit (simulation, feasible circuits with reduced distance >= 1): leave-one-device-out -> essential (breaks
   feasibility) / performance (removal LOWERS eff > 0.05 pp or RAISES ripple > 10 %, or changes Vout(D) > 2 % VIN) / redundant; greedy core removes
   redundant devices one at a time (re-pruning stranded partners, re-simulating). functional_distance = distance(core).
   In-loop audit = corner 0; readout audit = all 4 corners.
4. novelty = 0.9 * clip(fd - 0.5 * redundant, 0, 4) / 4 + 0.1 * WL(reduced). Old WL kept as novelty_wl.
   Index: converter/conv_fnov_index.pkl (rebuild: `python conv_functional.py --build`).

## Structural moves (converter/conv_moves.py)
sc_branch, lc_path, transfer_L, switch_path, insert_series, rewire, cell_graft (buck/boost/buckboost/Cuk cells).
A move is rejected before SPICE unless the child passes the strict gate AND its reduced circuit differs from the
parent's AND reduction removes no more devices from the child than from the parent.

## Memory (converter/conv_memory.py, --v8)
ViolationMemory interface (MemoryGuidance tilt reused unchanged). Outcomes: invalid, dead, collapse, cosmetic,
redundant, perf_hurt (penalty) and success (bonus, weight fd). Corpus reduction outcomes as a 0.1-weight prior.
Per-operator move outcomes -> move_weights() for the mover.

## Controller (agentic_add/controller_v6.py, fnov=...; backup .pre_fnov)
State block `functional_novelty` (best/median fd, feasible fd>=2, children raw-minus-functional gap, cosmetic
fraction, redundant-device rate, repeated-topology rate, stall, diagnoses COSMETIC_NOVELTY / FUNCTIONAL_STALL /
REDUNDANCY_HIGH / REPEATING / NOVEL_BUT_INFEASIBLE). New action STRUCT (budget = children, moves subset); STEER
struct_frac (persistent). Rule/random/fixed policies get the same tool (rule: STRUCT on stall at odd gens, STEER
struct_frac +0.15 on cosmetic/stall/repeat, RESCUE on novel-but-infeasible). Op-amp runs: unchanged (fnov=None).

## Driver (scripts/run_outer_nsga_conv.py; backup .pre_fnov)
--fnov --fnov_lambda --fnov_audit_max --fnov_struct_frac --fnov_struct_cap --v8 --v8_lambda --v8_lambda_max
--v8_per_sample --v6_policy. Per gen: SDEdit on (1 - struct_frac) of parents + structural children for the rest ->
annotate -> audit -> memory -> controller -> audit tool outputs -> survival -> genXX_fnov.json + fnov_archive.json.
Records carry `origin` (sdedit with steering state and last action / struct_move op + trigger / rescue / repair).

## Launch / readout
agents/steering_dev/launch_conv_fnov.sh <seed> [out]   POLICY=llm|rule|random GENS BUDGET GPU WORKERS SMOKE NOV8
converter/fnov_readout.py --runs <run...>  -> results/conv_fnov_readout/readout.{md,json} (4-corner re-audit, READOUT cost)

## Tested 9/15
selftest (survey N4 3->0, N1 3->1, N7 2->0, N5 2->0, paralleled L 1->0); audit on survey circuits (N3 raw 3 -> fd 0,
2 redundant); harness (buck + survey circuits -> STRUCT children 5/8 feasible, one feasible fd 3 after audit);
smoke rule s0 and smoke llm s1 end to end (0 controller failures; LLM chose STEER struct_frac 0.45 and STRUCT).
