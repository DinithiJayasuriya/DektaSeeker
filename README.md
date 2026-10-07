# Power converter circuits from the Δ-Seeker paper: how do they work?

This folder is for Mayowa. It has everything needed to simulate and understand the four
power converters shown in Fig. 7 of our paper (`docs/Paper_2026_DATE_DeltaSeeker_latest.pdf`,
Section IV, Table III). Nothing else from the project (the generative model, the search loop,
the LLM controller) is included. You do not need them for this goal.

## Goal

When we presented these results, people asked how these circuits actually work. For example
for D1: which switch is the high-side switch, which is the low-side switch, how does the
switching happen. We want to show this in the next update. Your job:

**Step 1. The parent circuits.**
Each of our four discovered circuits was made by adding a few components to a circuit that
already exists in the LaMAGIC training dataset. We call that the parent circuit. For each of
the four parents:
- Simulate it and look at the switching waveforms.
- Find which switches are phase-a switches (`Sa*`, on for the first part of the period) and
  which are phase-b switches (`Sb*`, on for the rest of the period).
- Say which switch is the high-side switch and which is the low-side switch.
- Explain in simple words how the parent converts 100 V to 50 V (or why it does not, two of
  the four parents do not work).

**Step 2. The discovered circuits.**
Then look at the four discovered circuits. Each one is the parent plus some new components
and switches (the red parts in Fig. 7). For each one:
- Simulate it and look at the switching waveforms.
- Show what the new components do: which current flows through them, in which phase, and
  what changes compared to the parent.
- Explain how the new circuit works.

**Step 3. If something does not work.**
If a circuit (parent or discovered) does not work properly, do not stop there. Find out from
the waveforms why it does not work, and find out why our search still picked it as a
candidate. The search results in `runs/` show what the search saw when it accepted the
circuit.

Please read `results/conv_validation_0918/SUMMARY.md` before you start. We already found
some problems there (for example D2's new branch can be replaced by a wire, and D2's parent
only fails because the simulator's switch has no body diode). Build on that, do not redo it.

## What each directory contains

```
converter/   The simulator and the analysis scripts.
             bench.py            netlist + duty -> Vout, efficiency, ripple (ngspice transient)
             spec.py             the 4 operating corners and the pass/fail rules the search used
             decode.py           puts a circuit in a standard form so two circuits can be compared
             plot_waveforms.py   START HERE. Plots gate signals, switching node, every current.
             mech_verify.py      per-component current, utilisation, voltage stress, loss, sweeps
             mech_report.py      turns mech_verify.json into a markdown table + figure
             parent_compare.py   parent vs discovered, all 4 corners, side by side
             ablate_added_devices.py / ablate_added_chain.py / ablate_branch_a.py
                                 remove or short the new components and see what changes
             switch_model_check.py   adds a body diode to the switch, changes off-resistance
             classify_15.py / classify_15_report.py   why the search accepted each circuit

circuits/    The four circuits of the paper figure and their parents, in one JSON file.
             discovered_converters_table.json   netlists + 4-corner results, keys a|b|c|d
             discovered_converters_probe.json   per-component numbers behind the figure labels
             discovered_converters_1col.png/.pdf   Fig. 7 of the paper
             make_four_converters_1col.py          the script that draws Fig. 7

runs/        The search runs the circuits came from. Each has:
             discovered.json     every circuit the search found and kept (the discovered set)
             final_audit.json    the final check of each discovered circuit
             genNN_front0.json   the best circuits at every generation
             *.log               the full log of the run
             conv_g20_v6_s0      20-generation run, seed 0. D1 and D2 come from here.
             conv_g20_v6_s1      same run, seed 1 (for comparison)
             conv_fnov_rule_s0   functional-novelty run. D3 and D4 come from here.

results/     Analysis we already did. Read these, they save you time.
             conv_validation_0918/   the audit from 18 Sep. SUMMARY.md first.
             conv_mech_verify/       component currents and sweeps from 13 Sep
             conv_parent_compare/    parent vs discovered corner table
             conv_g20_train_overlap.md   which discovered circuits are already in the dataset
             conv_section.tex        the paper text for the converter section
             waveforms/              output of plot_waveforms.py (D1 and D2 already there)

docs/        The paper PDF, and two notes on how the search scores and selects circuits
             (CONVERTER_V6.md, CONVERTER_FNOV.md).

corpus/      Scripts for the LaMAGIC dataset. Not needed for this goal, see corpus/README.md.

setup/       Our full converter search setup (diffusion model, search loop, controller,
             trained lamagic_v1 checkpoint, LaMAGIC graphs). Same folder layout as on our box.
```

## Parent circuits (LaMAGIC samples)

**All LaMAGIC samples.** The training set has 176,738 circuits (37,514 different topologies),
stored in `setup/CCT_Generation/DiGress/topology_generation/lamagic_graphs/train.pt`
(338 MB, too big for GitHub, so we share it separately). You do not need it for this goal:
the four parents are already in `circuits/discovered_converters_table.json`.

**The four samples we analyse.** Key = the key in the JSON file. Id = position in `train.pt`.

| Circuit | Key | LaMAGIC id | Netlist | Works? |
|---|---|---|---|---|
| D1 parent | `a\|train` | 9562  | `Sb0 n1 0; L0 n1 OUT; Sa0 IN n1; C0 IN OUT` | yes, 4/4 corners |
| D2 parent | `b\|train` | 10271 | `Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 n8; Sa1 OUT n8` | no, Vout 29 V |
| D3 parent | `c\|train` | 55863 | `L0 n7 OUT; L1 OUT n9; Sa0 n7 n9; Sb0 IN n7; Sa1 0 n9` | 1/4 corners, eff 88 % |
| D4 parent | `d\|train` | 4397  | `L0 n11 OUT; C0 OUT 0; Sa1 0 n8; Sb0 n8 IN; Sa0 n8 n11` | no, Vout 0 V |

**How to simulate them.**

```bash
cd converter
python plot_waveforms.py a --parent     # D1 parent   (b, c, d for the others)
```

## Discovered circuits

**All discovered circuits.** Each search run saves the circuits it kept in
`runs/<run>/discovered.json`.

| Run | Number of circuits |
|---|---|
| `runs/conv_g20_v6_s0/discovered.json` | 10 |
| `runs/conv_g20_v6_s1/discovered.json` | 5 |
| `runs/conv_fnov_rule_s0/discovered.json` | 9 |

**The four samples we analyse.** Index = position in that run's `discovered.json` (starts at 0).
The new parts are the components that are not in the parent.

| Circuit | Key | Run | Index | New parts | Netlist |
|---|---|---|---|---|---|
| D1 | `a\|disc` | conv_g20_v6_s0 | 0 | L1 | `Sb0 n1 0; L0 n1 OUT; Sa0 IN n1; C0 IN OUT; L1 n1 OUT` |
| D2 | `b\|disc` | conv_g20_v6_s0 | 9 | C1 | `Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 n8; Sa1 OUT n8; C1 OUT n8` |
| D3 | `c\|disc` | conv_fnov_rule_s0 | 0 | C0, Sb1, Sa0, L1, C1 | `L0 OUT n13; Sb0 IN n13; L1 OUT n13; C0 n13 n14; Sa0 0 n14; L2 OUT n15; Sa1 0 n15; Sb1 n14 n15; Sa2 n13 n15; C1 OUT 0` |
| D4 | `d\|disc` | conv_fnov_rule_s0 | 1 | L2, C0, Sb0, Sa0, L1 | `L0 OUT n13; L1 OUT n13; C0 n13 n14; Sa0 0 n14; L2 OUT n15; Sa1 0 n15; Sb0 n14 n15; Sa2 n13 n15; C1 OUT 0; Sb1 IN n15` |

**How to simulate them.**

```bash
cd converter
python plot_waveforms.py a              # D1   (b, c, d for the others)
```

To simulate any other circuit from a `discovered.json`, copy its netlist (replace the newlines
with `; `) and run:

```bash
python plot_waveforms.py --netlist "Sb0 n1 0; L0 n1 OUT; Sa0 IN n1; C0 IN OUT" --duty 0.5
```

## How to read a netlist and the output

- Format is `Device node node; ...`. `IN` = 100 V input, `OUT` = output with 50 Ω load,
  `0` = ground, `n1`, `n7`, ... = internal nodes.
- `Sa*` switches are on in phase a (duty D). `Sb*` switches are on in phase b (1 - D).
- `plot_waveforms.py` prints Vout, efficiency, and current, voltage and loss for every
  component. It saves a figure in `results/waveforms/`: gate signals, switching node voltage,
  inductor, switch and capacitor currents over three periods.
- After the waveforms, use `parent_compare.py` (parent vs discovered at 4 corners) and
  `ablate_added_devices.py` (remove each new part) to see what the new parts do.

## Simulator settings (so you know what the numbers mean)

- ngspice 36. Ideal switch model (`SW`): a resistor that is 50 mΩ when on and 1 MΩ when off.
  No body diode, no output capacitance. This matters, see the caveats below.
- VIN 100 V, load 50 Ω (so 1 A at 50 V), fsw 100 kHz, L 500 µH, C 10 µF, inductor DCR
  0.25 Ω, capacitor ESR 30 mΩ.
- Target: 50 V output (2:1 step down). A circuit passes a corner if Vout is within 5 % of
  50 V, ripple is below 5 %, efficiency is at least 90 %, and the output responds to duty.
- The 4 corners: nominal, half load resistance, double load resistance, 90 % input with L and
  C 20 % smaller.

## Already known, carry these into every conclusion

- D1 is a synchronous buck. Sa0 is the high-side switch (IN to n1), Sb0 is the low-side
  switch (n1 to ground). L0 and L1 are in parallel and share the load current equally. C0
  from IN to OUT works as the output capacitor because IN is an ideal source.
  See `results/waveforms/waveforms_a_discovered.png`.
- D2's new branch (`Sa1` in parallel with `C1`) can be replaced by a wire and the circuit
  gets better (99.37 % vs 98.96 %). See `results/conv_validation_0918/ablate_branch_a.md`.
- D2's parent fails only because the switch has no body diode. With a diode on Sa1 in the
  conducting direction the parent passes 4/4 corners. See `switch_model_check.md`.
- Many discovered circuits have components that carry zero current. The validity check does
  not catch them and novelty rewards them. 12 of 15 corner-robust circuits are a LaMAGIC
  training circuit once the 0 A components are deleted. See `classify_15_final.md`.
- The duty-refined efficiency from `spec.py` can read above 99.99 % or even above 100 % on
  bad circuits. Trust the fixed-duty numbers from `plot_waveforms.py` / `mech_verify.py`.
- In the paper: the Fig. 7 caption says three topologies but the figure has four, Table III
  says `Fig. ??`, and the text uses (a)(b)(c) while the table uses D1..D4. These need fixing.
