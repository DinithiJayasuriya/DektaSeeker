# Converter (a): control for the Sa1 || C1 branch

Circuit (a) = conv_g20_v6_s0 discovered #09 = mech_verify case "d"; parent LaMAGIC train #10271.
All rows: spec.evaluate_topology, eff_floor 0.9, duty re-refined per circuit and per corner,
4 corners (nominal / heavy load / light load / low line + -20% passives).

| variant | devices | feasible corners | eff median % | eff worst % | ripple max mV |
|---|---|---|---|---|---|
| `child` -- (a) as discovered: L0 -> n8, branch Sa1 || C1 to OUT | 6 | **4/4** | 98.96 | 97.99 | 88 |
| `short_branch` -- CONTROL: Sa1 || C1 branch replaced by a wire (n8 == OUT) | 4 | **4/4** | 99.37 | 98.80 | 87 |
| `parent` -- parent #10271: C1 deleted, Sa1 alone in series | 5 | **0/4** | -- | -- | -- |
| `c1_only` -- Sa1 deleted, C1 alone in series | 5 | **0/4** | -- | -- | -- |
| `buck_ref` -- textbook buck (discovered.json s0 #02, corpus circuit) | 4 | **4/4** | 99.37 | 98.80 | 87 |

## Per-corner detail

### `child`  `Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 n8; Sa1 OUT n8; C1 OUT n8`

| corner | feasible | duty | Vout V | eff % | ripple mV | reason |
|---|---|---|---|---|---|---|
| nominal | yes | 0.5052 | 50.00 | 98.95 | 64 |  |
| heavy_load | yes | 0.5102 | 50.00 | 97.99 | 64 |  |
| light_load | yes | 0.5026 | 50.00 | 99.42 | 64 |  |
| low_line_tol | yes | 0.5612 | 50.00 | 98.97 | 88 |  |

### `short_branch`  `Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 OUT`

| corner | feasible | duty | Vout V | eff % | ripple mV | reason |
|---|---|---|---|---|---|---|
| nominal | yes | 0.5029 | 50.00 | 99.37 | 63 |  |
| heavy_load | yes | 0.5059 | 50.00 | 98.80 | 63 |  |
| light_load | yes | 0.5014 | 50.00 | 99.63 | 63 |  |
| low_line_tol | yes | 0.5588 | 50.00 | 99.37 | 87 |  |

### `parent`  `Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 n8; Sa1 OUT n8`

| corner | feasible | duty | Vout V | eff % | ripple mV | reason |
|---|---|---|---|---|---|---|
| nominal | NO | 0.9000 | 28.80 | 28.79 | 196 | Vout 28.8 misses 50.0 |
| heavy_load | NO | 0.9000 | 16.82 | 16.82 | 228 | Vout 16.8 misses 50.0 |
| light_load | NO | 0.9000 | 44.71 | 44.71 | 152 | Vout 44.7 misses 50.0 |
| low_line_tol | NO | 0.9000 | 30.21 | 33.57 | 251 | Vout 30.2 misses 50.0 |

### `c1_only`  `Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 n8; C1 OUT n8`

| corner | feasible | duty | Vout V | eff % | ripple mV | reason |
|---|---|---|---|---|---|---|
| nominal | NO | 0.5000 | 0.00 | 0.06 | 63 | passthrough: output ignores duty |
| heavy_load | NO | 0.5000 | 0.00 | 0.12 | 63 | passthrough: output ignores duty |
| light_load | NO | 0.5000 | 0.00 | 0.03 | 64 | passthrough: output ignores duty |
| low_line_tol | NO | 0.5000 | -0.00 | 0.12 | 89 | passthrough: output ignores duty |

### `buck_ref`  `Sa0 n3 IN; Sb0 n3 0; L0 OUT n3; C0 0 IN`

| corner | feasible | duty | Vout V | eff % | ripple mV | reason |
|---|---|---|---|---|---|---|
| nominal | yes | 0.5029 | 50.00 | 99.37 | 63 |  |
| heavy_load | yes | 0.5059 | 50.00 | 98.80 | 63 |  |
| light_load | yes | 0.5014 | 50.00 | 99.63 | 63 |  |
| low_line_tol | yes | 0.5588 | 50.00 | 99.37 | 87 |  |

