# Corpus membership of the 15, before and after pruning zero-current devices

Corpus: 37496 distinct LaMAGIC topologies (train + val + test), WL-canonical with rails fixed.
A device is pruned only if its measured I_rms is 0 (< 10 mA = 1 % of the 1 A load current).

| # | devices | in corpus as discovered | zero-current devices pruned | in corpus after pruning | copies in corpus |
|---|---|---|---|---|---|
| s0#00 | 5 | no | -- | no | -- |
| s0#01 | 5 | no | -- | no | -- |
| s0#02 | 4 | **YES** | C0 | **YES** | 5 |
| s0#03 | 6 | no | L1, Sa1 | **YES** | 5 |
| s0#04 | 6 | no | C0, Sa1, C1 | **YES** | 5 |
| s0#05 | 6 | no | C0 | **YES** | 5 |
| s0#06 | 6 | no | C0, Sa1, Sb1 | **YES** | 5 |
| s0#07 | 4 | **YES** | -- | **YES** | 5 |
| s0#08 | 6 | no | Sb1 | no | -- |
| s0#09 | 6 | no | C0 | **YES** | 5 |
| s1#00 | 5 | no | C0, C1 | **YES** | 6 |
| s1#01 | 7 | no | Sb0, L0, Sa1 | **YES** | 5 |
| s1#02 | 5 | no | C0, C1 | **YES** | 6 |
| s1#03 | 5 | no | C0, C1 | **YES** | 5 |
| s1#04 | 6 | no | C0, C1 | **YES** | 5 |

**2/15 in the corpus as discovered; 12/15 in the corpus once zero-current devices are removed.**

## Pruned netlists

| # | pruned netlist | in corpus |
|---|---|---|
| s0#00 | `Sb0 n1 0; L0 n1 OUT; Sa0 IN n1; C0 IN OUT; L1 n1 OUT` | no |
| s0#01 | `Sb0 n1 0; L0 n1 OUT; Sa0 IN n1; C0 OUT 0; L1 n1 OUT` | no |
| s0#02 | `Sa0 n3 IN; Sb0 n3 0; L0 OUT n3` | YES |
| s0#03 | `L0 OUT n5; Sb0 n5 IN; C0 OUT IN; Sa0 n5 0` | YES |
| s0#04 | `Sb0 0 n7; Sa0 IN n7; L0 n7 OUT` | YES |
| s0#05 | `Sb0 0 n7; Sa0 IN n7; L0 n7 OUT; Sb1 n0 OUT; C1 n0 0` | YES |
| s0#06 | `Sb0 0 n7; Sa0 IN n7; L0 n7 OUT` | YES |
| s0#07 | `Sb0 n3 IN; Sa0 n3 0; L0 OUT n3; C0 OUT IN` | YES |
| s0#08 | `Sb0 0 n7; Sa0 n0 n7; L0 n7 OUT; C0 0 OUT; Sa1 n0 IN` | no |
| s0#09 | `Sb0 0 n7; Sa0 IN n7; L0 n7 n8; Sa1 OUT n8; C1 OUT n8` | YES |
| s1#00 | `L0 OUT n9; Sb0 IN n9; Sa0 0 n9` | YES |
| s1#01 | `C0 0 OUT; Sb1 n5 IN; Sa0 0 n5; L1 OUT n5` | YES |
| s1#02 | `L0 OUT n9; Sb0 IN n9; Sa0 0 n9` | YES |
| s1#03 | `L0 OUT n9; Sb0 0 n9; Sa0 IN n9` | YES |
| s1#04 | `L0 OUT n9; Sb0 IN n9; C2 OUT IN; Sa0 0 n9` | YES |
