# LaMAGIC corpus helpers

The nearest-parent netlists for D1..D4 are already in `circuits/discovered_converters_table.json`,
so nothing here is needed for Goal 1.

To browse the training corpus yourself (e.g. to check whether a pruned circuit is a training
circuit, or to find other parents):

1. Download the public LaMAGIC dataset (Chang et al., 2024; the `345comp` raw JSON release).
2. Run `build_lamagic_graphs.py` on it to produce `lamagic_graphs/{train,val,test}.pt`
   (splits 176,738 / 9,818 / 9,820 graphs; `stats.json` is the expected summary).
   Needs torch.
3. Put the output in `corpus/lamagic_graphs/`. Then `corpus_after_prune.py` and
   `train_overlap.py` run as-is (paths are relative to this folder).

Parent indices quoted in the paper figure are 0-based positions in `train.pt`:
D1 #9562, D2 #10271, D3 #55863, D4 #4397. Textbook bucks: #6935, #40128.
