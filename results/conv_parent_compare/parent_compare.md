# Child vs nearest-training-parent, conv_g20_v6_s0 (re-simulated 2026-09-13)

Same evaluator as the search: spec eff_floor 0.90, |Vout−50|≤5 %, ripple ≤5 % of Vout, duty sweep {0.1..0.9} + 2 secant refinements, 
bench VIN 100 V, 100 kHz, L 500 µH, C 10 µF, Cout 10 µF, Ron 50 mΩ, DCR 0.25 Ω, ESR 30 mΩ. Parent = nearest LaMAGIC sample by exact isomorphism; 
child = parent + ONE device. Δ = child − parent.

## Summary over the 4 corners

| panel | circuit | added device | parent sample | | feasible corners | median η % | worst η % | η spread % | max ripple mV |
|---|---|---|---|---|---|---|---|---|---|
| a | paralleled inductors, cap IN->OUT | L1 (2nd inductor, parallel) | train #9562 | parent | 4/4 | 99.37 | 98.80 | 0.84 | 44 |
| | | | | **child** | **4/4** | **99.60** | **99.28** | **0.44** | **88** |
| | | | | Δ | +0 | +0.23 | +0.48 | -0.39 | +44 |
| b | switched output capacitor | C0 (input cap) | train #19363 | parent | 4/4 | 99.37 | 98.80 | 0.84 | 72 |
| | | | | **child** | **4/4** | **99.37** | **98.80** | **0.84** | **72** |
| | | | | Δ | +0 | +0.00 | +0.00 | +0.00 | +0 |
| c | doubled series high-side switch | C0 (output cap) | train #415 | parent | 4/4 | 99.32 | 98.70 | 0.91 | 87 |
| | | | | **child** | **4/4** | **99.32** | **98.70** | **0.92** | **44** |
| | | | | Δ | +0 | +0.00 | +0.00 | +0.01 | -44 |
| d | inductor to OUT through Sa1 || C1 | C1 (cap across Sa1) | train #10271 | parent | 0/4 | 31.18 | 16.82 | 27.89 | 251 |
| | | | | **child** | **4/4** | **98.96** | **97.99** | **1.43** | **88** |
| | | | | Δ | +4 | +67.78 | +81.17 | -26.46 | -163 |
| ref | textbook buck | – | train #6935 | – | 4/4 | 99.37 | 98.80 | 0.84 | 87 |

## Per corner

| panel | corner | | feasible | duty D | Vout V | η % | ripple mV | ripple % Vout |
|---|---|---|---|---|---|---|---|---|
| a | nominal (100 V, 50 Ω) | parent | yes | 0.503 | 50.00 | 99.37 | 32 | 0.06 |
|  |  | child | yes | 0.502 | 50.00 | 99.60 | 63 | 0.13 |
| | | Δ | | -0.001 | +0.00 | +0.23 | +32 | |
| a | heavy load (25 Ω) | parent | yes | 0.506 | 50.00 | 98.80 | 32 | 0.06 |
|  |  | child | yes | 0.503 | 50.00 | 99.28 | 63 | 0.13 |
| | | Δ | | -0.003 | +0.00 | +0.48 | +32 | |
| a | light load (100 Ω) | parent | yes | 0.501 | 50.00 | 99.64 | 33 | 0.07 |
|  |  | child | yes | 0.501 | 50.00 | 99.72 | 64 | 0.13 |
| | | Δ | | -0.001 | +0.00 | +0.09 | +31 | |
| a | low line (90 V, −20 % L/C) | parent | yes | 0.559 | 50.00 | 99.37 | 44 | 0.09 |
|  |  | child | yes | 0.557 | 50.00 | 99.60 | 88 | 0.18 |
| | | Δ | | -0.001 | +0.00 | +0.22 | +44 | |
| b | nominal (100 V, 50 Ω) | parent | yes | 0.503 | 50.00 | 99.37 | 51 | 0.10 |
|  |  | child | yes | 0.503 | 50.00 | 99.37 | 51 | 0.10 |
| | | Δ | | +0.000 | +0.00 | +0.00 | +0 | |
| b | heavy load (25 Ω) | parent | yes | 0.506 | 50.00 | 98.80 | 51 | 0.10 |
|  |  | child | yes | 0.506 | 50.00 | 98.80 | 51 | 0.10 |
| | | Δ | | +0.000 | +0.00 | +0.00 | +0 | |
| b | light load (100 Ω) | parent | yes | 0.501 | 50.00 | 99.64 | 51 | 0.10 |
|  |  | child | yes | 0.501 | 50.00 | 99.64 | 51 | 0.10 |
| | | Δ | | +0.000 | +0.00 | +0.00 | +0 | |
| b | low line (90 V, −20 % L/C) | parent | yes | 0.559 | 50.00 | 99.37 | 72 | 0.14 |
|  |  | child | yes | 0.559 | 50.00 | 99.37 | 72 | 0.14 |
| | | Δ | | +0.000 | +0.00 | +0.00 | +0 | |
| c | nominal (100 V, 50 Ω) | parent | yes | 0.503 | 50.00 | 99.32 | 63 | 0.13 |
|  |  | child | yes | 0.503 | 50.00 | 99.32 | 32 | 0.06 |
| | | Δ | | +0.000 | +0.00 | +0.00 | -32 | |
| c | heavy load (25 Ω) | parent | yes | 0.500 | 49.37 | 98.70 | 63 | 0.13 |
|  |  | child | yes | 0.500 | 49.37 | 98.70 | 32 | 0.06 |
| | | Δ | | +0.000 | +0.00 | +0.00 | -32 | |
| c | light load (100 Ω) | parent | yes | 0.501 | 50.00 | 99.61 | 63 | 0.13 |
|  |  | child | yes | 0.501 | 50.00 | 99.62 | 32 | 0.06 |
| | | Δ | | +0.000 | +0.00 | +0.01 | -31 | |
| c | low line (90 V, −20 % L/C) | parent | yes | 0.559 | 50.00 | 99.32 | 87 | 0.17 |
|  |  | child | yes | 0.559 | 50.00 | 99.32 | 44 | 0.09 |
| | | Δ | | +0.000 | +0.00 | +0.00 | -44 | |
| d | nominal (100 V, 50 Ω) | parent | NO (Vout 28.8 misses 50.0) | 0.900 | 28.80 | 28.79 | 196 | 0.68 |
|  |  | child | yes | 0.505 | 50.00 | 98.95 | 64 | 0.13 |
| | | Δ | | -0.395 | +21.20 | +70.16 | -132 | |
| d | heavy load (25 Ω) | parent | NO (Vout 16.8 misses 50.0) | 0.900 | 16.82 | 16.82 | 228 | 1.36 |
|  |  | child | yes | 0.510 | 50.00 | 97.99 | 64 | 0.13 |
| | | Δ | | -0.390 | +33.18 | +81.17 | -165 | |
| d | light load (100 Ω) | parent | NO (Vout 44.7 misses 50.0) | 0.900 | 44.71 | 44.71 | 152 | 0.34 |
|  |  | child | yes | 0.503 | 50.00 | 99.42 | 64 | 0.13 |
| | | Δ | | -0.397 | +5.29 | +54.71 | -88 | |
| d | low line (90 V, −20 % L/C) | parent | NO (Vout 30.2 misses 50.0) | 0.900 | 30.21 | 33.57 | 251 | 0.83 |
|  |  | child | yes | 0.561 | 50.00 | 98.97 | 88 | 0.18 |
| | | Δ | | -0.339 | +19.79 | +65.40 | -163 | |

## Reading

- **(a) + L1 in parallel:** efficiency up at every corner (+0.23 nominal, +0.48 at heavy load: conduction loss split over two windings) at the price of doubled ripple (32→63 mV, still 0.13 % of Vout vs the 5 % limit). This is the only child that beats the textbook buck.
- **(b) + input cap:** identical to the parent to 2 decimals at every corner. The bench source is ideal, so an input capacitor cannot change anything. Novel by isomorphism, not by performance.
- **(c) + output cap:** efficiency unchanged; ripple halved (63→32 mV) at every corner. Pure ripple improvement.
- **(d) + C1 across Sa1:** the parent is NOT a converter (best it can do is Vout 28.8 V at D=0.9, η 29 %, fails all 4 corners); the added capacitor is the freewheel path that makes it work (4/4 corners, η 98.95 %). Largest single-component effect, but the result is still 0.4 % below the textbook buck.