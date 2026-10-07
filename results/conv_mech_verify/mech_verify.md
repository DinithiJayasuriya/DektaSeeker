# Mechanism verification, conv_g20_v6_s0 children vs nearest training parents (2026-09-13)

All waveform numbers are from the bench's own ngspice deck (VIN 100 V, 100 kHz, L 500 µH / DCR 0.25 Ω, C 10 µF / ESR 30 mΩ, Cout 10 µF, ideal SW switches Ron 50 mΩ / Roff 1 MΩ), last 20 of 2,000 periods, at the child's refined nominal duty, with a 0 V probe source in series with every switch and capacitor. **Switching loss is not modelled** (ideal switch model, 1 ns edges): the loss table is conduction + ESR only, and it closes against Pin − Pout to <1 mW. I_load = 1 A at nominal (50 V / 50 Ω). U = fraction of the period with |i| > 1 % I_load. Δ columns are child − parent; Δη/Δripple/Δfeasible use the 4-corner re-simulation of parent_compare.md (duty re-refined per circuit and corner).

## 1. Mechanism-verification table

| design | added element | active? (U, I_rms/I_load) | Δη median (pp) | Δη worst-corner (pp) | Δripple nominal | Δfeasible corners | peak stress on added element | verdict |
|---|---|---|---|---|---|---|---|---|
| a | L1 (L) | yes (U 1.00, 0.52) | +0.23 | +0.48 | +32 mV | +0 | 50.1 V, 0.75 A pk | trade-off: +η from halved winding loss, ripple ×2 (still 0.13 % Vout) |
| b | C0 (C) | no (U 0.00, 0.00) | +0.00 | +0.00 | +0 mV | +0 | 100.0 V, 0.00 A pk | NO: zero current (sits across the ideal source); redundant |
| c | C0 (C) | yes (U 0.92, 0.07) | +0.00 | +0.00 | -32 mV | +0 | 50.0 V, 0.12 A pk | ripple suppression only; merges into the bench output cap |
| d | C1 (C) | yes (U 0.97, 1.47) | +67.78 | +81.17 | -132 mV | +4 | 0.6 V, 6.46 A pk | YES: new energy-transfer path (parent is not a converter without it), but 6.5 A / 7.2 A peaks on C1 / Sa1 at 1 A load |

## 2. Per-element currents, stress, loss (nominal, child duty)

Added element in **bold**. i_mean of a capacitor is the charge-balance check (should be ≈ 0).

### (a) paralleled inductors, cap IN->OUT — child D = 0.5016

**child**: Vout 50.00 V, η 99.60 %, ripple 63 mV, Pin 50.190 W, total loss 200 mW

| element | kind | I_rms A | I_peak A | I_mean A | I_rms/I_load | U | V_peak V | P_loss mW |
|---|---|---|---|---|---|---|---|---|
| Sb0 | S | 0.734 | 1.500 | -0.4980 | 0.73 | 0.50 | 100.0 | 32.0 |
| L0 | L | 0.520 | 0.750 | +0.5000 | 0.52 | 1.00 | 50.1 | 67.5 |
| Sa0 | S | 0.737 | 1.500 | +0.5019 | 0.74 | 0.50 | 100.1 | 32.2 |
| C0 | C | 0.144 | 0.250 | +0.0000 | 0.14 | 0.96 | 50.0 | 0.6 |
| **L1** | L | 0.520 | 0.750 | +0.5000 | 0.52 | 1.00 | 50.1 | 67.5 |

**parent**: Vout 49.87 V, η 99.37 %, ripple 32 mV, Pin 50.057 W, total loss 315 mW  (parent at the CHILD's duty: not re-refined)

| element | kind | I_rms A | I_peak A | I_mean A | I_rms/I_load | U | V_peak V | P_loss mW |
|---|---|---|---|---|---|---|---|---|
| Sb0 | S | 0.711 | 1.247 | -0.4968 | 0.71 | 0.50 | 100.0 | 30.3 |
| L0 | L | 1.008 | 1.247 | +0.9974 | 1.01 | 1.00 | 50.1 | 253.7 |
| Sa0 | S | 0.714 | 1.248 | +0.5006 | 0.72 | 0.50 | 100.1 | 30.5 |
| C0 | C | 0.072 | 0.125 | +0.0000 | 0.07 | 0.92 | 50.1 | 0.2 |

### (b) switched output capacitor — child D = 0.5029

**child**: Vout 50.00 V, η 99.37 %, ripple 51 mV, Pin 50.316 W, total loss 317 mW

| element | kind | I_rms A | I_peak A | I_mean A | I_rms/I_load | U | V_peak V | P_loss mW |
|---|---|---|---|---|---|---|---|---|
| Sb0 | S | 0.712 | 1.250 | +0.4968 | 0.71 | 0.50 | 100.0 | 30.4 |
| Sa0 | S | 0.717 | 1.250 | +0.5032 | 0.72 | 0.50 | 100.1 | 30.7 |
| **C0** | C | 0.000 | 0.000 | +0.0000 | 0.00 | 0.00 | 100.0 | 0.0 |
| L0 | L | 1.010 | 1.250 | +1.0000 | 1.01 | 1.00 | 50.1 | 255.0 |
| Sb1 | S | 0.041 | 0.113 | -0.0000 | 0.04 | 0.46 | 0.0 | 0.1 |
| C1 | C | 0.041 | 0.113 | +0.0000 | 0.04 | 0.46 | 50.0 | 0.1 |

**parent**: Vout 50.00 V, η 99.37 %, ripple 51 mV, Pin 50.317 W, total loss 317 mW  (parent at the CHILD's duty: not re-refined)

| element | kind | I_rms A | I_peak A | I_mean A | I_rms/I_load | U | V_peak V | P_loss mW |
|---|---|---|---|---|---|---|---|---|
| Sb0 | S | 0.712 | 1.250 | +0.4968 | 0.71 | 0.50 | 100.0 | 30.4 |
| Sa0 | S | 0.717 | 1.250 | +0.5032 | 0.72 | 0.50 | 100.1 | 30.7 |
| L0 | L | 1.010 | 1.250 | +1.0000 | 1.01 | 1.00 | 50.1 | 254.9 |
| Sb1 | S | 0.041 | 0.113 | -0.0000 | 0.04 | 0.46 | 0.0 | 0.1 |
| C1 | C | 0.041 | 0.113 | +0.0000 | 0.04 | 0.46 | 50.0 | 0.1 |

### (c) doubled series high-side switch — child D = 0.5032

**child**: Vout 50.00 V, η 99.32 %, ripple 32 mV, Pin 50.350 W, total loss 341 mW

| element | kind | I_rms A | I_peak A | I_mean A | I_rms/I_load | U | V_peak V | P_loss mW |
|---|---|---|---|---|---|---|---|---|
| Sb0 | S | 0.712 | 1.250 | +0.4966 | 0.71 | 0.50 | 99.9 | 30.4 |
| Sa0 | S | 0.717 | 1.250 | +0.5035 | 0.72 | 0.50 | 50.1 | 26.9 |
| L0 | L | 1.010 | 1.250 | +1.0001 | 1.01 | 1.00 | 50.1 | 254.9 |
| **C0** | C | 0.072 | 0.125 | +0.0000 | 0.07 | 0.92 | 50.0 | 0.1 |
| Sa1 | S | 0.717 | 1.250 | -0.5035 | 0.72 | 0.50 | 50.0 | 26.9 |
| Sb1 | S | 0.000 | 0.000 | +0.0000 | 0.00 | 0.00 | 50.0 | 1.3 |

**parent**: Vout 50.00 V, η 99.32 %, ripple 63 mV, Pin 50.351 W, total loss 341 mW  (parent at the CHILD's duty: not re-refined)

| element | kind | I_rms A | I_peak A | I_mean A | I_rms/I_load | U | V_peak V | P_loss mW |
|---|---|---|---|---|---|---|---|---|
| Sb0 | S | 0.712 | 1.250 | +0.4966 | 0.71 | 0.50 | 99.9 | 30.4 |
| Sa0 | S | 0.717 | 1.250 | +0.5035 | 0.72 | 0.50 | 50.1 | 27.0 |
| L0 | L | 1.010 | 1.250 | +1.0001 | 1.01 | 1.00 | 50.1 | 255.0 |
| Sa1 | S | 0.717 | 1.250 | -0.5035 | 0.72 | 0.50 | 50.0 | 26.9 |
| Sb1 | S | 0.000 | 0.000 | +0.0000 | 0.00 | 0.00 | 50.0 | 1.3 |

### (d) inductor to OUT through Sa1 || C1 — child D = 0.5052

**child**: Vout 50.00 V, η 98.95 %, ripple 64 mV, Pin 50.536 W, total loss 530 mW

| element | kind | I_rms A | I_peak A | I_mean A | I_rms/I_load | U | V_peak V | P_loss mW |
|---|---|---|---|---|---|---|---|---|
| Sb0 | S | 0.711 | 1.251 | +0.4947 | 0.71 | 0.49 | 100.0 | 30.3 |
| Sa0 | S | 0.718 | 1.251 | +0.5054 | 0.72 | 0.51 | 100.1 | 30.7 |
| C0 | C | 0.000 | 0.000 | -0.0000 | 0.00 | 0.00 | 100.0 | -0.0 |
| L0 | L | 1.010 | 1.251 | +1.0001 | 1.01 | 1.00 | 50.6 | 255.0 |
| Sa1 | S | 1.724 | 7.209 | -1.0001 | 1.72 | 0.51 | 0.6 | 148.6 |
| **C1** | C | 1.467 | 6.460 | +0.0000 | 1.47 | 0.97 | 0.6 | 64.4 |

**parent**: Vout 11.31 V, η 11.31 %, ripple 147 mV, Pin 22.635 W, total loss 20075 mW  (parent at the CHILD's duty: not re-refined)

| element | kind | I_rms A | I_peak A | I_mean A | I_rms/I_load | U | V_peak V | P_loss mW |
|---|---|---|---|---|---|---|---|---|
| Sb0 | S | 0.005 | 0.813 | -0.0001 | 0.02 | 0.00 | 100.0 | 5.1 |
| Sa0 | S | 0.368 | 0.895 | +0.2264 | 1.62 | 0.50 | 100.0 | 11.7 |
| C0 | C | 0.000 | 0.000 | +0.0000 | 0.00 | 0.00 | 100.0 | 0.0 |
| L0 | L | 0.367 | 0.895 | +0.2263 | 1.62 | 0.50 | 813073.8 | -948.2 |
| Sa1 | S | 0.367 | 0.895 | -0.2263 | 1.62 | 0.50 | 813062.3 | 21003.7 |

Notes. (d) parent at the child's duty: when Sa1 opens there is no path for the inductor current, so the ideal model produces an unbounded voltage spike (8×10⁵ V through Roff = 1 MΩ) and the per-element losses are numerically meaningless; that spike IS the reason the parent is not a converter. (d) child: C1 is charged to ≈ Vout and is discharged through Sa1 every time Sa1 closes; the only limit is Ron + ESR = 80 mΩ, hence the 6.5 A / 7.2 A peaks and the 149 mW + 64 mW extra loss that put (d) 0.4 pp below the textbook buck. A real design would need a snubber or a resonant inductor here.

## 3. Loss breakdown by element kind (mW, nominal, child duty)

| design | | switches | inductors | capacitors ESR | Cout ESR | total | Pin − Pout |
|---|---|---|---|---|---|---|---|
| a | child | 64.2 | 134.9 | 0.6 | 0.6 | 200.3 | 200.3 |
|  | parent | 60.8 | 253.7 | 0.2 | 0.2 | 314.8 | 314.8 |
| b | child | 61.1 | 255.0 | 0.1 | 0.4 | 316.7 | 316.6 |
|  | parent | 61.1 | 254.9 | 0.1 | 0.4 | 316.6 | 316.6 |
| c | child | 85.5 | 254.9 | 0.1 | 0.2 | 340.7 | 340.6 |
|  | parent | 85.5 | 255.0 | 0.0 | 0.6 | 341.2 | 341.2 |
| d | child | 209.7 | 255.0 | 64.4 | 0.6 | 529.8 | 529.8 |
|  | parent | 21020.5 | -948.2 | 0.0 | 2.5 | 20074.8 | 20074.7 |
| ref | textbook buck | 61.0 | 255.0 | 0.0 | 0.6 | 316.7 | 316.6 |

## 4. Load-step transient (R_out 50 → 25 Ω at 20 ms, back to 50 Ω at 28 ms; fixed duty, open loop)

| design | | step UP: undershoot V | overshoot V | settle to 1 % ms | step DOWN: overshoot V | undershoot V | settle ms | ΔVout steady (open-loop droop) V |
|---|---|---|---|---|---|---|---|---|
| a | child | 3.05 | 2.25 | 1.27 | 3.21 | 2.65 | 2.14 | -0.17 |
|  | parent | 4.05 | 2.68 | 1.75 | 4.36 | 3.37 | 2.72 | -0.30 |
| b | child | 4.02 | 2.58 | 1.49 | 4.31 | 3.25 | 2.41 | -0.30 |
|  | parent | 4.02 | 2.58 | 1.49 | 4.31 | 3.25 | 2.41 | -0.30 |
| c | child | 4.04 | 2.66 | 1.50 | 4.35 | 3.33 | 2.70 | -0.32 |
|  | parent | 5.50 | 3.26 | 1.05 | 6.06 | 4.49 | 1.92 | -0.32 |
| d | child | 5.34 | 3.04 | 1.03 | 5.88 | 4.18 | 1.69 | -0.50 |
|  | parent | 0.07 | 5.27 | 1.06 | 0.08 | 5.38 | 1.70 | -5.31 |
| ref | child | 5.52 | 3.29 | 1.06 | 6.08 | 4.53 | 1.92 | -0.30 |

## 5. Load and line sweep (duty re-refined to 50 V at each point; η % / ripple mV)

| design | | 0.25× load (200 Ω) | 0.5× (100 Ω) | 1× (50 Ω) | 1.5× (33 Ω) | VIN 90 V | VIN 110 V |
|---|---|---|---|---|---|---|---|
| a | child | 99.71 / 68 | 99.72 / 64 | 99.60 / 63 | 99.44 / 63 | 99.61 / 56 | 99.59 / 69 |
|  | parent | 99.72 / 43 | 99.64 / 33 | 99.37 / 32 | 99.09 / 32 | 99.38 / 28 | 99.36 / 35 |
| b | child | 99.79 / 53 | 99.64 / 51 | 99.37 / 51 | 99.09 / 51 | 99.38 / 47 | 99.36 / 54 |
|  | parent | 99.79 / 53 | 99.64 / 51 | 99.37 / 51 | 99.09 / 51 | 99.38 / 47 | 99.36 / 54 |
| c | child | 99.99 / 38 | 99.62 / 32 | 99.32 / 32 | 99.01 / 32 | 99.32 / 28 | 99.32 / 35 |
|  | parent | 99.72 / 64 | 99.61 / 63 | 99.32 / 63 | 99.01 / 63 | 99.32 / 56 | 99.32 / 69 |
| d | child | 99.60 / 63 | 99.42 / 64 | 98.95 / 64 | 98.47 / 64 | 99.02 / 56 | 98.89 / 69 |
|  | parent | FAIL (efficiency 0.501 below) | FAIL (Vout 44.7 misses 50.0) | FAIL (Vout 28.8 misses 50.0) | FAIL (Vout 21.2 misses 50.0) | FAIL (Vout 25.9 misses 50.0) | FAIL (Vout 31.7 misses 50.0) |
| ref | child | 99.74 / 65 | 99.63 / 63 | 99.37 / 63 | 99.09 / 63 | 99.38 / 56 | 99.36 / 69 |
Note: (c) child at 0.25× load reads 99.99 %, which is unphysical (≈1 mW loss at 12.5 W); the same bench family produced a 122 % child during the run. Treat light-load efficiencies from the duty-refined sweep as ±0.3 pp; the fixed-duty probe numbers in §2 are the reliable ones.


## 6. Component-tolerance grid: L ±10 %, C (and Cout) ±20 %, Ron ×0.5 / ×2 → 8 combinations, duty re-refined

| design | | feasible / 8 | η min–max % | ripple max mV | worst combination |
|---|---|---|---|---|---|
| a | child | 8/8 | 99.48–99.66 | 88 | L0.9_C0.8_R2.0 |
|  | parent | 8/8 | 99.27–99.42 | 44 | L0.9_C0.8_R2.0 |
| b | child | 8/8 | 99.27–99.42 | 73 | L0.9_C0.8_R2.0 |
|  | parent | 8/8 | 99.27–99.42 | 73 | L0.9_C0.8_R2.0 |
| c | child | 8/8 | 99.17–99.40 | 44 | L0.9_C0.8_R2.0 |
|  | parent | 8/8 | 99.17–99.40 | 88 | L0.9_C0.8_R2.0 |
| d | child | 8/8 | 98.64–99.12 | 88 | L0.9_C0.8_R2.0 |
|  | parent | 0/8 | – | – | all fail |
| ref | child | 8/8 | 99.27–99.42 | 88 | L0.9_C1.2_R2.0 |

## 7. Does the gain depend on a tuned value? (fixed child duty, nominal corner)

(d) C1 value sweep, child:

| C1 | Vout V | η % | ripple mV | i_C1 rms A | i_Sa1 rms A | U(C1) | U(Sa1) |
|---|---|---|---|---|---|---|---|
| 10 µF (as run) | 50.00 | 98.95 | 64 | 1.467 | 1.724 | 0.97 | 0.51 |
| 1 µF | 48.84 | 96.83 | 65 | 3.971 | 4.060 | 0.56 | 0.51 |
| 2.5 µF | 49.61 | 98.24 | 64 | 2.595 | 2.736 | 0.96 | 0.51 |
| 5 µF | 49.87 | 98.71 | 64 | 1.921 | 2.115 | 0.96 | 0.51 |
| 20 µF | 50.07 | 99.06 | 63 | 1.190 | 1.515 | 1.00 | 0.51 |
| 40 µF | 50.09 | 99.10 | 63 | 1.064 | 1.436 | 1.00 | 0.51 |
| 100 µF | 50.10 | 99.11 | 63 | 1.015 | 1.412 | 1.00 | 0.51 |

(a) L1 value sweep, child:

| L1 | Vout V | η % | ripple mV | i_L0 rms A | i_L1 rms A |
|---|---|---|---|---|---|
| 250 µH | 50.00 | 99.56 | 95 | 0.520 | 0.577 |
| 500 µH (as run) | 50.00 | 99.60 | 63 | 0.520 | 0.520 |
| 1000 µH | 50.00 | 99.61 | 48 | 0.521 | 0.505 |

## 8. Equivalent-circuit reductions (fixed child duty, nominal corner)

| design | variant | Vout V | η % | ripple mV | reading |
|---|---|---|---|---|---|
| a | child: L0 ∥ L1 (2 × 500 µH, 2 × 0.25 Ω) | 50.00 | 99.60 | 63 |  |
| a | parent: single 500 µH | 49.87 | 99.37 | 32 |  |
| a | parent with L0 = 250 µH, DCR 0.125 Ω (exact parallel equivalent) | 50.00 | 99.60 | 63 | ≡ child ⇒ the child IS a buck with half L and half DCR |
| a | parent with L0 = 250 µH, DCR 0.25 Ω | 49.87 | 99.33 | 63 | same ripple as child, parent's η ⇒ the η gain is the DCR halving, not the inductance |
| b | child | 50.00 | 99.37 | 51 |  |
| b | child with C0 removed (= parent) | 50.00 | 99.37 | 51 | identical ⇒ C0 redundant |
| c | child: C0 across OUT (+ bench Cout) | 50.00 | 99.32 | 32 |  |
| c | parent (bench Cout only) | 50.00 | 99.32 | 63 |  |
| c | parent with bench Cout = 20 µF | 50.00 | 99.32 | 33 | ≡ child ⇒ C0 merges into the output cap |
| c | child with idle Sb1 removed | 50.00 | 99.33 | 32 | identical ⇒ Sb1 is dead (inherited from the parent) |
| d | child: L → OUT via Sa1 ∥ C1 | 50.00 | 98.95 | 64 |  |
| d | parent: C1 removed | 11.31 | 11.31 | 147 | no freewheel path |
| d | child with C1 shorted | 50.23 | 99.37 | 63 | = plain buck |
| d | child with Sa1 removed (L → C1 → OUT only) | -0.00 | 0.06 | 63 | Vout = 0: a series capacitor blocks DC, so Sa1 is the DC path and C1 the freewheel path; both needed |
