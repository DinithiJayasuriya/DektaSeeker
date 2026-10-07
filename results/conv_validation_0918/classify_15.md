# All 15 corner-robust converters of conv_g20_v6 (seeds 0 and 1)

Reference textbook buck `Sa0 n3 IN; Sb0 n3 0; L0 OUT n3; C0 0 IN`: 4/4 corners, eff median 99.37 %, worst 98.80 %, ripple max 87 mV.

A device is INERT if its I_rms is below 10 mA = 1 % of the 1 A nominal load current,
measured at the circuit's own refined nominal duty with a 0 V ammeter in series with it.
`reduced` = inert devices deleted; `merged` = parallel same-kind devices then collapsed.
The reduced circuit is re-scored on all 4 corners: identical numbers confirm the deletion is free.

| # | gen | nov | dev | inert devices | reduced to | eff med % (run -> reduced) | corners | vs buck (pp) |
|---|---|---|---|---|---|---|---|---|
| s0#00 | 8 | 0.080 | 5 | -- | 5 dev, NOT buck | 99.60 -> 99.60 | 4/4 | +0.23 |
| s0#01 | 15 | 0.147 | 5 | -- | 5 dev, NOT buck | 99.60 -> 99.60 | 4/4 | +0.23 |
| s0#02 | 0 | 0.000 | 4 | C0 | 3 dev, NOT buck | 99.37 -> 99.37 | 4/4 | +0.00 |
| s0#03 | 2 | 0.107 | 6 | L1, Sa1 | 4 dev, NOT buck | 99.37 -> 99.37 | 4/4 | +0.00 |
| s0#04 | 4 | 0.103 | 6 | C0, Sa1, C1 | 3 dev, NOT buck | 99.37 -> 99.37 | 4/4 | +0.00 |
| s0#05 | 7 | 0.107 | 6 | C0 | 5 dev, NOT buck | 99.37 -> 99.37 | 4/4 | +0.00 |
| s0#06 | 11 | 0.107 | 6 | C0, Sa1, Sb1 | 3 dev, NOT buck | 99.37 -> 99.37 | 4/4 | +0.00 |
| s0#07 | 17 | 0.000 | 4 | -- | 4 dev, NOT buck | 99.37 -> 99.37 | 4/4 | +0.00 |
| s0#08 | 17 | 0.107 | 6 | Sb1 | 5 dev, NOT buck | 99.32 -> 99.32 | 4/4 | -0.05 |
| s0#09 | 13 | 0.111 | 6 | C0 | 5 dev, NOT buck | 98.96 -> 98.96 | 4/4 | -0.41 |
| s1#00 | 6 | 0.083 | 5 | C0, C1 | 3 dev, NOT buck | 99.37 -> 99.37 | 4/4 | -0.00 |
| s1#01 | 11 | 0.125 | 7 | Sb0, L0, Sa1 | 4 dev, NOT buck | 99.37 -> 99.37 | 4/4 | +0.00 |
| s1#02 | 13 | 0.069 | 5 | C0, C1 | 3 dev, NOT buck | 99.37 -> 99.37 | 4/4 | -0.00 |
| s1#03 | 19 | 0.105 | 5 | C0, C1 | 3 dev, NOT buck | 99.37 -> 99.37 | 4/4 | +0.00 |
| s1#04 | 20 | 0.131 | 6 | C0, C1 | 4 dev, NOT buck | 99.37 -> 99.37 | 4/4 | +0.00 |

## Per-circuit detail

### s0#00  (seed 0, first seen gen 8, novelty 0.0801)

- as discovered: `Sb0 n1 0; L0 n1 OUT; Sa0 IN n1; C0 IN OUT; L1 n1 OUT`  (5 devices)
- inert: none
- reduced: `Sb0 n1 0; L0 n1 OUT; Sa0 IN n1; C0 IN OUT; L1 n1 OUT`
- parallel merge: L0, L1 in parallel -> one L of L/2 and DCR/2 -> `Sb0 n1 0; L0 n1 OUT; Sa0 IN n1; C0 IN OUT`
- reduces to the textbook buck: **False**

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| Sb0 | S | 0.734 | 1.500 | 0.50 | 32.0 |
| L0 | L | 0.520 | 0.750 | 1.00 | 67.5 |
| Sa0 | S | 0.737 | 1.500 | 0.50 | 32.2 |
| C0 | C | 0.144 | 0.250 | 0.96 | 0.6 |
| L1 | L | 0.520 | 0.750 | 1.00 | 67.5 |

| corner | as discovered: feasible / eff % / ripple mV | reduced: feasible / eff % / ripple mV |
|---|---|---|
| nominal | yes / 99.60 / 63 | yes / 99.60 / 63 |
| heavy_load | yes / 99.28 / 63 | yes / 99.28 / 63 |
| light_load | yes / 99.72 / 64 | yes / 99.72 / 64 |
| low_line_tol | yes / 99.60 / 88 | yes / 99.60 / 88 |

### s0#01  (seed 0, first seen gen 15, novelty 0.1472)

- as discovered: `Sb0 n1 0; L0 n1 OUT; Sa0 IN n1; C0 OUT 0; L1 n1 OUT`  (5 devices)
- inert: none
- reduced: `Sb0 n1 0; L0 n1 OUT; Sa0 IN n1; C0 OUT 0; L1 n1 OUT`
- parallel merge: L0, L1 in parallel -> one L of L/2 and DCR/2 -> `Sb0 n1 0; L0 n1 OUT; Sa0 IN n1; C0 OUT 0`
- reduces to the textbook buck: **False**

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| Sb0 | S | 0.734 | 1.500 | 0.50 | 32.0 |
| L0 | L | 0.520 | 0.750 | 1.00 | 67.5 |
| Sa0 | S | 0.737 | 1.500 | 0.50 | 32.2 |
| C0 | C | 0.144 | 0.250 | 0.96 | 0.6 |
| L1 | L | 0.520 | 0.750 | 1.00 | 67.5 |

| corner | as discovered: feasible / eff % / ripple mV | reduced: feasible / eff % / ripple mV |
|---|---|---|
| nominal | yes / 99.60 / 63 | yes / 99.60 / 63 |
| heavy_load | yes / 99.28 / 63 | yes / 99.28 / 63 |
| light_load | yes / 99.73 / 64 | yes / 99.73 / 64 |
| low_line_tol | yes / 99.60 / 88 | yes / 99.60 / 88 |

### s0#02  (seed 0, first seen gen 0, novelty 0.0000)

- as discovered: `Sa0 n3 IN; Sb0 n3 0; L0 OUT n3; C0 0 IN`  (4 devices)
- inert: C0
- reduced: `Sa0 n3 IN; Sb0 n3 0; L0 OUT n3`
- reduces to the textbook buck: **False**

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| Sa0 | S | 0.717 | 1.250 | 0.50 | 30.7 |
| Sb0 | S | 0.712 | 1.250 | 0.50 | 30.4 |
| L0 | L | 1.010 | 1.250 | 1.00 | 255.0 |
| C0 *(inert)* | C | 0.000 | 0.000 | 0.00 | 0.0 |

| corner | as discovered: feasible / eff % / ripple mV | reduced: feasible / eff % / ripple mV |
|---|---|---|
| nominal | yes / 99.37 / 63 | yes / 99.37 / 63 |
| heavy_load | yes / 98.80 / 63 | yes / 98.80 / 63 |
| light_load | yes / 99.63 / 63 | yes / 99.63 / 63 |
| low_line_tol | yes / 99.37 / 87 | yes / 99.37 / 87 |

### s0#03  (seed 0, first seen gen 2, novelty 0.1071)

- as discovered: `L0 OUT n5; Sb0 n5 IN; C0 OUT IN; L1 n3 IN; Sa0 n5 0; Sa1 n3 IN`  (6 devices)
- inert: L1, Sa1
- reduced: `L0 OUT n5; Sb0 n5 IN; C0 OUT IN; Sa0 n5 0`
- reduces to the textbook buck: **False**

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| L0 | L | 1.010 | 1.250 | 1.00 | 255.0 |
| Sb0 | S | 0.717 | 1.250 | 0.50 | 30.7 |
| C0 | C | 0.072 | 0.125 | 0.92 | 0.1 |
| L1 *(inert)* | L | 0.000 | 0.000 | 0.00 | 0.0 |
| Sa0 | S | 0.712 | 1.250 | 0.50 | 30.4 |
| Sa1 *(inert)* | S | 0.000 | 0.000 | 0.00 | 0.0 |

| corner | as discovered: feasible / eff % / ripple mV | reduced: feasible / eff % / ripple mV |
|---|---|---|
| nominal | yes / 99.37 / 32 | yes / 99.37 / 32 |
| heavy_load | yes / 98.80 / 32 | yes / 98.80 / 32 |
| light_load | yes / 99.63 / 33 | yes / 99.63 / 33 |
| low_line_tol | yes / 99.37 / 44 | yes / 99.37 / 44 |

### s0#04  (seed 0, first seen gen 4, novelty 0.1029)

- as discovered: `Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 OUT; Sa1 n0 OUT; C1 n0 OUT`  (6 devices)
- inert: C0, Sa1, C1
- reduced: `Sb0 0 n7; Sa0 IN n7; L0 n7 OUT`
- reduces to the textbook buck: **False**

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| Sb0 | S | 0.712 | 1.250 | 0.50 | 30.4 |
| Sa0 | S | 0.717 | 1.250 | 0.50 | 30.7 |
| C0 *(inert)* | C | 0.000 | 0.000 | 0.00 | 0.0 |
| L0 | L | 1.010 | 1.250 | 1.00 | 255.0 |
| Sa1 *(inert)* | S | 0.000 | 0.000 | 0.00 | 0.0 |
| C1 *(inert)* | C | 0.000 | 0.000 | 0.00 | 0.0 |

| corner | as discovered: feasible / eff % / ripple mV | reduced: feasible / eff % / ripple mV |
|---|---|---|
| nominal | yes / 99.37 / 63 | yes / 99.37 / 63 |
| heavy_load | yes / 98.80 / 63 | yes / 98.80 / 63 |
| light_load | yes / 99.63 / 63 | yes / 99.63 / 63 |
| low_line_tol | yes / 99.37 / 87 | yes / 99.37 / 87 |

### s0#05  (seed 0, first seen gen 7, novelty 0.1071)

- as discovered: `Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 OUT; Sb1 n0 OUT; C1 n0 0`  (6 devices)
- inert: C0
- reduced: `Sb0 0 n7; Sa0 IN n7; L0 n7 OUT; Sb1 n0 OUT; C1 n0 0`
- reduces to the textbook buck: **False**

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| Sb0 | S | 0.712 | 1.250 | 0.50 | 30.4 |
| Sa0 | S | 0.717 | 1.250 | 0.50 | 30.7 |
| C0 *(inert)* | C | 0.000 | 0.000 | 0.00 | 0.0 |
| L0 | L | 1.010 | 1.250 | 1.00 | 255.0 |
| Sb1 | S | 0.041 | 0.113 | 0.46 | 0.1 |
| C1 | C | 0.041 | 0.113 | 0.46 | 0.1 |

| corner | as discovered: feasible / eff % / ripple mV | reduced: feasible / eff % / ripple mV |
|---|---|---|
| nominal | yes / 99.37 / 51 | yes / 99.37 / 51 |
| heavy_load | yes / 98.80 / 51 | yes / 98.80 / 51 |
| light_load | yes / 99.64 / 51 | yes / 99.64 / 51 |
| low_line_tol | yes / 99.37 / 72 | yes / 99.37 / 72 |

### s0#06  (seed 0, first seen gen 11, novelty 0.1071)

- as discovered: `Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 OUT; Sa1 n0 OUT; Sb1 n0 OUT`  (6 devices)
- inert: C0, Sa1, Sb1
- reduced: `Sb0 0 n7; Sa0 IN n7; L0 n7 OUT`
- reduces to the textbook buck: **False**

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| Sb0 | S | 0.712 | 1.250 | 0.50 | 30.4 |
| Sa0 | S | 0.717 | 1.250 | 0.50 | 30.7 |
| C0 *(inert)* | C | 0.000 | 0.000 | 0.00 | 0.0 |
| L0 | L | 1.010 | 1.250 | 1.00 | 255.0 |
| Sa1 *(inert)* | S | 0.000 | 0.000 | 0.00 | 0.0 |
| Sb1 *(inert)* | S | 0.000 | 0.000 | 0.00 | 0.0 |

| corner | as discovered: feasible / eff % / ripple mV | reduced: feasible / eff % / ripple mV |
|---|---|---|
| nominal | yes / 99.37 / 63 | yes / 99.37 / 63 |
| heavy_load | yes / 98.80 / 63 | yes / 98.80 / 63 |
| light_load | yes / 99.63 / 63 | yes / 99.63 / 63 |
| low_line_tol | yes / 99.37 / 87 | yes / 99.37 / 87 |

### s0#07  (seed 0, first seen gen 17, novelty 0.0000)

- as discovered: `Sb0 n3 IN; Sa0 n3 0; L0 OUT n3; C0 OUT IN`  (4 devices)
- inert: none
- reduced: `Sb0 n3 IN; Sa0 n3 0; L0 OUT n3; C0 OUT IN`
- reduces to the textbook buck: **False**

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| Sb0 | S | 0.717 | 1.250 | 0.50 | 30.7 |
| Sa0 | S | 0.712 | 1.250 | 0.50 | 30.4 |
| L0 | L | 1.010 | 1.250 | 1.00 | 255.0 |
| C0 | C | 0.072 | 0.125 | 0.92 | 0.1 |

| corner | as discovered: feasible / eff % / ripple mV | reduced: feasible / eff % / ripple mV |
|---|---|---|
| nominal | yes / 99.37 / 32 | yes / 99.37 / 32 |
| heavy_load | yes / 98.80 / 32 | yes / 98.80 / 32 |
| light_load | yes / 99.63 / 33 | yes / 99.63 / 33 |
| low_line_tol | yes / 99.37 / 44 | yes / 99.37 / 44 |

### s0#08  (seed 0, first seen gen 17, novelty 0.1071)

- as discovered: `Sb0 0 n7; Sa0 n0 n7; L0 n7 OUT; C0 0 OUT; Sa1 n0 IN; Sb1 n0 OUT`  (6 devices)
- inert: Sb1
- reduced: `Sb0 0 n7; Sa0 n0 n7; L0 n7 OUT; C0 0 OUT; Sa1 n0 IN`
- reduces to the textbook buck: **False**

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| Sb0 | S | 0.712 | 1.250 | 0.50 | 30.4 |
| Sa0 | S | 0.717 | 1.250 | 0.50 | 26.9 |
| L0 | L | 1.010 | 1.250 | 1.00 | 254.9 |
| C0 | C | 0.072 | 0.125 | 0.92 | 0.1 |
| Sa1 | S | 0.717 | 1.250 | 0.50 | 26.9 |
| Sb1 *(inert)* | S | 0.000 | 0.000 | 0.00 | 1.3 |

| corner | as discovered: feasible / eff % / ripple mV | reduced: feasible / eff % / ripple mV |
|---|---|---|
| nominal | yes / 99.32 / 32 | yes / 99.33 / 32 |
| heavy_load | yes / 98.70 / 32 | yes / 98.70 / 32 |
| light_load | yes / 99.62 / 32 | yes / 99.63 / 32 |
| low_line_tol | yes / 99.32 / 44 | yes / 99.32 / 44 |

### s0#09  (seed 0, first seen gen 13, novelty 0.1105)

- as discovered: `Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 n8; Sa1 OUT n8; C1 OUT n8`  (6 devices)
- inert: C0
- reduced: `Sb0 0 n7; Sa0 IN n7; L0 n7 n8; Sa1 OUT n8; C1 OUT n8`
- reduces to the textbook buck: **False**

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| Sb0 | S | 0.711 | 1.251 | 0.49 | 30.3 |
| Sa0 | S | 0.718 | 1.251 | 0.51 | 30.7 |
| C0 *(inert)* | C | 0.000 | 0.000 | 0.00 | -0.0 |
| L0 | L | 1.010 | 1.251 | 1.00 | 255.0 |
| Sa1 | S | 1.724 | 7.209 | 0.51 | 148.6 |
| C1 | C | 1.467 | 6.460 | 0.97 | 64.4 |

| corner | as discovered: feasible / eff % / ripple mV | reduced: feasible / eff % / ripple mV |
|---|---|---|
| nominal | yes / 98.95 / 64 | yes / 98.95 / 64 |
| heavy_load | yes / 97.99 / 64 | yes / 97.99 / 64 |
| light_load | yes / 99.42 / 64 | yes / 99.42 / 64 |
| low_line_tol | yes / 98.97 / 88 | yes / 98.97 / 88 |

### s1#00  (seed 1, first seen gen 6, novelty 0.0833)

- as discovered: `L0 OUT n9; C0 n0 IN; Sb0 IN n9; C1 n0 0; Sa0 0 n9`  (5 devices)
- inert: C0, C1
- reduced: `L0 OUT n9; Sb0 IN n9; Sa0 0 n9`
- reduces to the textbook buck: **False**

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| L0 | L | 1.010 | 1.250 | 1.00 | 255.0 |
| C0 *(inert)* | C | 0.000 | 0.000 | 0.00 | 0.0 |
| Sb0 | S | 0.717 | 1.250 | 0.50 | 30.7 |
| C1 *(inert)* | C | 0.000 | 0.000 | 0.00 | -0.0 |
| Sa0 | S | 0.712 | 1.250 | 0.50 | 30.4 |

| corner | as discovered: feasible / eff % / ripple mV | reduced: feasible / eff % / ripple mV |
|---|---|---|
| nominal | yes / 99.37 / 63 | yes / 99.37 / 63 |
| heavy_load | yes / 98.80 / 63 | yes / 98.80 / 63 |
| light_load | yes / 99.63 / 63 | yes / 99.63 / 63 |
| low_line_tol | yes / 99.37 / 87 | yes / 99.37 / 87 |

### s1#01  (seed 1, first seen gen 11, novelty 0.1250)

- as discovered: `Sb0 n6 IN; C0 0 OUT; Sb1 n5 IN; L0 n6 IN; Sa0 0 n5; L1 OUT n5; Sa1 n6 IN`  (7 devices)
- inert: Sb0, L0, Sa1
- reduced: `C0 0 OUT; Sb1 n5 IN; Sa0 0 n5; L1 OUT n5`
- reduces to the textbook buck: **False**

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| Sb0 *(inert)* | S | 0.000 | 0.000 | 0.00 | 0.0 |
| C0 | C | 0.072 | 0.125 | 0.92 | 0.2 |
| Sb1 | S | 0.717 | 1.250 | 0.50 | 30.7 |
| L0 *(inert)* | L | 0.000 | 0.000 | 0.00 | 0.0 |
| Sa0 | S | 0.712 | 1.250 | 0.50 | 30.4 |
| L1 | L | 1.010 | 1.250 | 1.00 | 255.0 |
| Sa1 *(inert)* | S | 0.000 | 0.000 | 0.00 | 0.0 |

| corner | as discovered: feasible / eff % / ripple mV | reduced: feasible / eff % / ripple mV |
|---|---|---|
| nominal | yes / 99.37 / 32 | yes / 99.37 / 32 |
| heavy_load | yes / 98.80 / 32 | yes / 98.80 / 32 |
| light_load | yes / 99.62 / 33 | yes / 99.62 / 33 |
| low_line_tol | yes / 99.37 / 44 | yes / 99.37 / 44 |

### s1#02  (seed 1, first seen gen 13, novelty 0.0691)

- as discovered: `L0 OUT n9; C0 n0 0; Sb0 IN n9; C1 n0 0; Sa0 0 n9`  (5 devices)
- inert: C0, C1
- reduced: `L0 OUT n9; Sb0 IN n9; Sa0 0 n9`
- reduces to the textbook buck: **False**

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| L0 | L | 1.010 | 1.250 | 1.00 | 255.0 |
| C0 *(inert)* | C | 0.000 | 0.000 | 0.00 | 0.0 |
| Sb0 | S | 0.717 | 1.250 | 0.50 | 30.7 |
| C1 *(inert)* | C | 0.000 | 0.000 | 0.00 | 0.0 |
| Sa0 | S | 0.712 | 1.250 | 0.50 | 30.4 |

| corner | as discovered: feasible / eff % / ripple mV | reduced: feasible / eff % / ripple mV |
|---|---|---|
| nominal | yes / 99.37 / 63 | yes / 99.37 / 63 |
| heavy_load | yes / 98.80 / 63 | yes / 98.80 / 63 |
| light_load | yes / 99.63 / 63 | yes / 99.63 / 63 |
| low_line_tol | yes / 99.37 / 87 | yes / 99.37 / 87 |

### s1#03  (seed 1, first seen gen 19, novelty 0.1049)

- as discovered: `L0 OUT n9; C0 n0 0; Sb0 0 n9; C1 n0 0; Sa0 IN n9`  (5 devices)
- inert: C0, C1
- reduced: `L0 OUT n9; Sb0 0 n9; Sa0 IN n9`
- reduces to the textbook buck: **False**

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| L0 | L | 1.010 | 1.250 | 1.00 | 255.0 |
| C0 *(inert)* | C | 0.000 | 0.000 | 0.00 | 0.0 |
| Sb0 | S | 0.712 | 1.250 | 0.50 | 30.4 |
| C1 *(inert)* | C | 0.000 | 0.000 | 0.00 | 0.0 |
| Sa0 | S | 0.717 | 1.250 | 0.50 | 30.7 |

| corner | as discovered: feasible / eff % / ripple mV | reduced: feasible / eff % / ripple mV |
|---|---|---|
| nominal | yes / 99.37 / 63 | yes / 99.37 / 63 |
| heavy_load | yes / 98.80 / 63 | yes / 98.80 / 63 |
| light_load | yes / 99.63 / 63 | yes / 99.63 / 63 |
| low_line_tol | yes / 99.37 / 87 | yes / 99.37 / 87 |

### s1#04  (seed 1, first seen gen 20, novelty 0.1314)

- as discovered: `L0 OUT n9; C0 IN 0; C1 IN 0; Sb0 IN n9; C2 OUT IN; Sa0 0 n9`  (6 devices)
- inert: C0, C1
- reduced: `L0 OUT n9; Sb0 IN n9; C2 OUT IN; Sa0 0 n9`
- reduces to the textbook buck: **False**

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| L0 | L | 1.010 | 1.250 | 1.00 | 255.0 |
| C0 *(inert)* | C | 0.000 | 0.000 | 0.00 | 0.0 |
| C1 *(inert)* | C | 0.000 | 0.000 | 0.00 | 0.0 |
| Sb0 | S | 0.717 | 1.250 | 0.50 | 30.7 |
| C2 | C | 0.072 | 0.125 | 0.92 | 0.1 |
| Sa0 | S | 0.712 | 1.250 | 0.50 | 30.4 |

| corner | as discovered: feasible / eff % / ripple mV | reduced: feasible / eff % / ripple mV |
|---|---|---|
| nominal | yes / 99.37 / 32 | yes / 99.37 / 32 |
| heavy_load | yes / 98.80 / 32 | yes / 98.80 / 32 |
| light_load | yes / 99.63 / 33 | yes / 99.63 / 33 |
| low_line_tol | yes / 99.37 / 44 | yes / 99.37 / 44 |

