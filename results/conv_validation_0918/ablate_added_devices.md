# Per-device effect of the added (red) devices, 4 figure converters

spec.evaluate_topology, eff_floor 0.9, duty re-refined per circuit and corner, 4 corners.
del = device removed from the child; short = device replaced by a wire; add = parent + that device only.

## a

| variant | device | corners | eff median (feasible) % | eff median (all) % | Vout nom V | fail reasons |
|---|---|---|---|---|---|---|
| child |  | 4/4 | 99.60 | 99.60 | 50.00 |  |
| parent |  | 4/4 | 99.37 | 99.37 | 50.00 |  |
| del | L1 | 4/4 | 99.37 | 99.37 | 50.00 |  |
| short | L1 | 0/4 | -- | 0.49 | 50.00 | ripple |
| add | L1 | 4/4 | 99.60 | 99.60 | 50.00 |  |

## b

| variant | device | corners | eff median (feasible) % | eff median (all) % | Vout nom V | fail reasons |
|---|---|---|---|---|---|---|
| child |  | 4/4 | 98.96 | 98.96 | 50.00 |  |
| parent |  | 0/4 | -- | 31.18 | 28.80 | Vout 16.8 misses 50.0; Vout 28.8 misses 50.0; Vout 30.2 misses 50.0; Vout 44.7 misses 50.0 |
| del | C1 | 0/4 | -- | 31.18 | 28.80 | Vout 16.8 misses 50.0; Vout 28.8 misses 50.0; Vout 30.2 misses 50.0; Vout 44.7 misses 50.0 |
| short | C1 | 4/4 | 99.37 | 99.37 | 50.00 |  |
| add | C1 | 4/4 | 98.96 | 98.96 | 50.00 |  |

## c

| variant | device | corners | eff median (feasible) % | eff median (all) % | Vout nom V | fail reasons |
|---|---|---|---|---|---|---|
| child |  | 4/4 | 99.64 | 99.64 | 50.00 |  |
| parent |  | 1/4 | 92.97 | 88.43 | 50.00 | efficiency 0.798 below floor 0.9; efficiency 0.884 below floor 0.9; efficiency 0.885 below floor 0.9 |
| del | L1 | 4/4 | 99.56 | 99.56 | 50.00 |  |
| short | L1 | 0/4 | -- | 0.49 | 50.17 | ripple |
| add | L1 | 1/4 | 93.39 | 88.59 | 50.00 | efficiency 0.798 below floor 0.9; efficiency 0.885 below floor 0.9; efficiency 0.887 below floor 0.9 |
| del | C0 | 1/4 | 93.39 | 88.60 | 50.00 | efficiency 0.798 below floor 0.9; efficiency 0.885 below floor 0.9; efficiency 0.887 below floor 0.9 |
| short | C0 | 4/4 | 99.67 | 99.67 | 50.00 |  |
| add | C0 | 1/4 | 92.97 | 88.43 | 50.00 | efficiency 0.798 below floor 0.9; efficiency 0.884 below floor 0.9; efficiency 0.885 below floor 0.9 |
| del | Sa0 | 4/4 | 99.48 | 99.48 | 50.00 |  |
| short | Sa0 | 0/4 | -- | 0.27 | 50.16 | efficiency 0.001 below floor 0.9; efficiency 0.002 below floor 0.9; efficiency 0.003 below floor 0.9; efficiency 0.005 b |
| add | Sa0 | 1/4 | 92.97 | 88.43 | 50.00 | efficiency 0.798 below floor 0.9; efficiency 0.884 below floor 0.9; efficiency 0.885 below floor 0.9 |
| del | Sb1 | 1/4 | 93.39 | 88.60 | 50.00 | efficiency 0.798 below floor 0.9; efficiency 0.885 below floor 0.9; efficiency 0.887 below floor 0.9 |
| short | Sb1 | 4/4 | 99.64 | 99.64 | 50.00 |  |
| add | Sb1 | 1/4 | 92.97 | 88.43 | 50.00 | efficiency 0.798 below floor 0.9; efficiency 0.884 below floor 0.9; efficiency 0.885 below floor 0.9 |
| del | C1 | 4/4 | 99.63 | 99.63 | 50.00 |  |
| add | C1 | 1/4 | 92.97 | 88.44 | 50.00 | efficiency 0.798 below floor 0.9; efficiency 0.884 below floor 0.9; efficiency 0.885 below floor 0.9 |

## d

| variant | device | corners | eff median (feasible) % | eff median (all) % | Vout nom V | fail reasons |
|---|---|---|---|---|---|---|
| child |  | 4/4 | 99.45 | 99.45 | 50.00 |  |
| parent |  | 0/4 | -- | 0.00 | 0.00 | passthrough: output ignores duty |
| del | L1 | 4/4 | 99.46 | 99.46 | 50.00 |  |
| short | L1 | 0/4 | -- | 0.60 | 49.29 | ripple |
| add | L1 | 0/4 | -- | 0.00 | 0.00 | passthrough: output ignores duty |
| del | C0 | 0/4 | -- | 79.74 | 50.00 | efficiency 0.665 below floor 0.9; efficiency 0.796 below floor 0.9; efficiency 0.799 below floor 0.9; efficiency 0.880 b |
| short | C0 | 4/4 | 99.65 | 99.65 | 50.00 |  |
| add | C0 | 0/4 | -- | 0.00 | 0.00 | passthrough: output ignores duty |
| del | Sa0 | 4/4 | 99.33 | 99.33 | 49.69 |  |
| short | Sa0 | 0/4 | -- | 0.03 | 38.50 | Vout 34.7 misses 50.0; Vout 38.3 misses 50.0; Vout 38.5 misses 50.0; Vout 38.6 misses 50.0 |
| add | Sa0 | 0/4 | -- | 0.00 | 0.00 | passthrough: output ignores duty |
| del | Sb0 | 0/4 | -- | 79.75 | 50.00 | efficiency 0.665 below floor 0.9; efficiency 0.796 below floor 0.9; efficiency 0.799 below floor 0.9; efficiency 0.880 b |
| short | Sb0 | 4/4 | 99.53 | 99.53 | 50.00 |  |
| add | Sb0 | 0/4 | -- | 0.00 | 0.00 | passthrough: output ignores duty |
| del | L2 | 4/4 | 98.89 | 98.89 | 49.54 |  |
| short | L2 | 0/4 | -- | 0.50 | 50.00 | ripple |
| add | L2 | 1/4 | 93.06 | 88.48 | 50.00 | efficiency 0.798 below floor 0.9; efficiency 0.884 below floor 0.9; efficiency 0.886 below floor 0.9 |

