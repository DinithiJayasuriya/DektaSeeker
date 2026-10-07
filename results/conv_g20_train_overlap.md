# conv_g20_v6 discovered set vs LaMAGIC corpus (exact isomorphism, 2026-09-13)

Method: converter/train_overlap.py decodes every LaMAGIC train/val/test graph with decode.to_netlist and
compares decode.canonical() signatures (WL colouring of the device/net bipartite graph, rails fixed).
Corpus: 196,107 graphs decoded -> 37,496 distinct topologies. Then for each non-match, test whether
deleting 1 or 2 devices yields a corpus circuit.

| seed | gen | eff % | ncomp | in corpus? | relation to corpus | electrical reading |
|---|---|---|---|---|---|---|
| 0 | 0  | 99.37 | 4 | YES (5 copies) | textbook buck | buck |
| 0 | 17 | 99.37 | 4 | YES (5 copies) | textbook buck (C OUT-IN) | buck |
| 0 | 8  | 99.60 | 5 | no | buck + 1 L | paralleled inductor (alive) |
| 0 | 15 | 99.60 | 5 | no | buck + 1 L | paralleled inductor, C OUT-0 (alive) |
| 0 | 7  | 99.37 | 6 | no | corpus + 1 | switched output cap Sb1/C1 (alive) |
| 0 | 17 | 99.32 | 6 | no | corpus + 1 | high-side switch doubled in series (alive, more loss) |
| 0 | 13 | 98.96 | 6 | no | corpus + 1 | series C in freewheel path (alive, more loss) |
| 0 | 2  | 99.37 | 6 | no | buck + 2 | L1,Sa1 loop n3-IN: FLOATING, dead |
| 0 | 4  | 99.37 | 6 | no | buck + 2 | Sa1,C1 loop n0-OUT: FLOATING, dead |
| 0 | 11 | 99.37 | 6 | no | buck + 2 | Sa1,Sb1 loop n0-OUT: FLOATING, dead |
| 1 | 6  | 99.37 | 5 | no | buck + 2 | two series input caps (alive, trivial) |
| 1 | 20 | 99.37 | 6 | no | buck + 2 | two parallel input caps + C OUT-IN (alive, trivial) |
| 1 | 11 | 99.37 | 7 | no | buck + 3 | Sb0,Sa1,L0 loop n6-IN: FLOATING, dead |
| 1 | 13 | 99.37 | 5 | no | buck + 2 | C0,C1 loop n0-0: FLOATING, dead |
| 1 | 19 | 99.37 | 5 | no | buck + 2 | C0,C1 loop n0-0: FLOATING, dead |

Summary: 2/15 exact corpus circuits; 13/15 not in corpus by isomorphism, but ALL 13 are a corpus buck
plus 1-3 added devices. 6/13 additions are floating loops (a net whose every element goes to the same
other net) that carry no current -> identical electrically to the buck; the novelty score (0.10-0.13)
rewards them. Electrically distinct alive non-corpus topologies: seed 0 = 4 (paralleled L, switched
output cap, doubled high-side switch, series-C freewheel); seed 1 = 2 (series/parallel input caps).
Action item: prune floating subgraphs before novelty scoring + dedup (validity check lets them through).
