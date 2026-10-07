| circuit | variant | netlist | corners | eff median (all) % | Vout nom | fail |
|---|---|---|---|---|---|---|
| c | parent | `L0 OUT n13; Sb0 IN n13; L2 OUT n15; Sa1 0 n15; Sa2 n13 n15` | 1/4 | 88.43 | 50.00 | efficiency 0.798 below floor 0.9; efficiency 0.884 below floor 0.9; efficiency 0.885 below |
| c | +C0,Sb1 | `L0 OUT n13; Sb0 IN n13; C0 n13 n14; L2 OUT n15; Sa1 0 n15; Sb1 n14 n15; Sa2 n13 n15` | 4/4 | 99.31 | 49.67 |  |
| c | +C0,Sb1,Sa0 | `L0 OUT n13; Sb0 IN n13; C0 n13 n14; Sa0 0 n14; L2 OUT n15; Sa1 0 n15; Sb1 n14 n15; Sa2 n13 n15` | 4/4 | 99.56 | 50.00 |  |
| c | +C0,Sb1,Sa0,L1 | `L0 OUT n13; Sb0 IN n13; L1 OUT n13; C0 n13 n14; Sa0 0 n14; L2 OUT n15; Sa1 0 n15; Sb1 n14 n15; Sa2 n13 n15` | 4/4 | 99.63 | 50.00 |  |
| c | +C0,Sb1,Sa0,L1,C1 | `L0 OUT n13; Sb0 IN n13; L1 OUT n13; C0 n13 n14; Sa0 0 n14; L2 OUT n15; Sa1 0 n15; Sb1 n14 n15; Sa2 n13 n15; C1 OUT 0` | 4/4 | 99.64 | 50.00 |  |
| d | parent | `L0 OUT n13; Sa1 0 n15; Sa2 n13 n15; C1 OUT 0; Sb1 IN n15` | 0/4 | 0.00 | 0.00 | passthrough: output ignores duty |
| d | +L2 | `L0 OUT n13; L2 OUT n15; Sa1 0 n15; Sa2 n13 n15; C1 OUT 0; Sb1 IN n15` | 1/4 | 88.48 | 50.00 | efficiency 0.798 below floor 0.9; efficiency 0.884 below floor 0.9; efficiency 0.886 below |
| d | +L2,C0,Sb0 | `L0 OUT n13; C0 n13 n14; L2 OUT n15; Sa1 0 n15; Sb0 n14 n15; Sa2 n13 n15; C1 OUT 0; Sb1 IN n15` | 4/4 | 99.33 | 50.00 |  |
| d | +L2,C0,Sb0,Sa0 | `L0 OUT n13; C0 n13 n14; Sa0 0 n14; L2 OUT n15; Sa1 0 n15; Sb0 n14 n15; Sa2 n13 n15; C1 OUT 0; Sb1 IN n15` | 4/4 | 99.46 | 50.00 |  |
| d | +L2,C0,Sb0,Sa0,L1 | `L0 OUT n13; L1 OUT n13; C0 n13 n14; Sa0 0 n14; L2 OUT n15; Sa1 0 n15; Sb0 n14 n15; Sa2 n13 n15; C1 OUT 0; Sb1 IN n15` | 4/4 | 99.45 | 50.00 |  |
| c | parent + wire for C0-Sb1 | `L0 OUT n15; Sb0 IN n15; L2 OUT n15; Sa1 0 n15` | 4/4 | 99.60 | 50.00 |  |
| d | parent + wire for C0-Sb0 | `L0 OUT n15; Sa1 0 n15; C1 OUT 0; Sb1 IN n15` | 4/4 | 99.37 | 50.00 |  |
| d | parent + L2 + wire for C0-Sb0 | `L0 OUT n15; L2 OUT n15; Sa1 0 n15; C1 OUT 0; Sb1 IN n15` | 4/4 | 99.60 | 50.00 |  |
