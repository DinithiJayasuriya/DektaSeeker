# All 15 corner-robust converters, classified

conv_g20_v6_s0 (10 archived) + conv_g20_v6_s1 (5 archived). Everything below is measured:
per-device currents from a 0 V ammeter in series with each device at the circuit's own refined
nominal duty; corpus membership by exact WL-canonical isomorphism against all 37,496 distinct
LaMAGIC train/val/test topologies; 4-corner re-scores through the run's own spec.evaluate_topology.

| class | meaning | count |
|---|---|---|
| 1 | already in the LaMAGIC corpus | 2 |
| 2a | a corpus circuit + a floating loop (0.00000 A, dead in any bench) | 6 |
| 2b | a corpus circuit + capacitor(s) across the ideal input source (0.00000 A here) | 4 |
| 3 | a corpus circuit + an active device that rescales a passive or filters | 3 |
| 4 | a mechanism the corpus does not contain | 0 |

**12/15 are a LaMAGIC training circuit once devices measured at 0.00000 A are deleted. The remaining 3 add an active device that rescales an inductor or adds filtering. None of the 15 is a mechanism the corpus does not already contain.**

| # | gen | dev | class | in corpus | after pruning 0 A devices | Δη med pp | Δη worst pp | Δripple nom mV | reading |
|---|---|---|---|---|---|---|---|---|---|
| s0#00 | 8 | 5 | **3** | no | no | +0.23 | +0.48 | +0.02 | corpus circuit + an active device; see note |
| s0#01 | 15 | 5 | **3** | no | no | +0.23 | +0.48 | +0.02 | corpus circuit + an active device; see note |
| s0#02 | 0 | 4 | **1** | YES | YES | +0.00 | +0.00 | +0.00 | already in the LaMAGIC training set (5 copies) |
| s0#03 | 2 | 6 | **2a** | no | YES | +0.00 | +0.00 | -31.69 | corpus circuit + floating loop (L1, Sa1); all measure 0.00000 A |
| s0#04 | 4 | 6 | **2a** | no | YES | +0.00 | +0.00 | +0.00 | corpus circuit + capacitor across the ideal input source (C0) + floating loop (C1, Sa1); all measure 0.00000 A |
| s0#05 | 7 | 6 | **2b** | no | YES | +0.00 | +0.00 | -12.61 | corpus circuit + capacitor across the ideal input source (C0); all measure 0.00000 A |
| s0#06 | 11 | 6 | **2a** | no | YES | +0.00 | +0.00 | +0.00 | corpus circuit + capacitor across the ideal input source (C0) + floating loop (Sa1, Sb1); all measure 0.00000 A |
| s0#07 | 17 | 4 | **1** | YES | YES | +0.00 | +0.00 | -31.69 | already in the LaMAGIC training set (5 copies) |
| s0#08 | 17 | 6 | **3** | no | no | -0.05 | -0.10 | -31.71 | corpus circuit + an active device; see note |
| s0#09 | 13 | 6 | **2b** | no | YES | -0.41 | -0.81 | +0.17 | corpus circuit + capacitor across the ideal input source (C0); all measure 0.00000 A |
| s1#00 | 6 | 5 | **2b** | no | YES | -0.00 | +0.00 | +0.00 | corpus circuit + capacitor across the ideal input source (C0, C1); all measure 0.00000 A |
| s1#01 | 11 | 7 | **2a** | no | YES | +0.00 | +0.00 | -31.69 | corpus circuit + floating loop (L0, Sa1, Sb0); all measure 0.00000 A |
| s1#02 | 13 | 5 | **2a** | no | YES | -0.00 | +0.00 | +0.00 | corpus circuit + floating loop (C0, C1); all measure 0.00000 A |
| s1#03 | 19 | 5 | **2a** | no | YES | +0.00 | +0.00 | +0.00 | corpus circuit + floating loop (C0, C1); all measure 0.00000 A |
| s1#04 | 20 | 6 | **2b** | no | YES | +0.00 | +0.00 | -31.69 | corpus circuit + capacitor across the ideal input source (C0) + capacitor across the ideal input source (C1); all measure 0.00000 A |

Δ columns compare the circuit (with 0 A devices deleted) against the textbook buck `Sa0 n3 IN; Sb0 n3 0; L0 OUT n3; C0 0 IN` at 99.37 % median / 98.80 % worst / 63 mV nominal ripple.

## Notes on the three circuits that are not a corpus circuit plus dead devices

**s0#00** -- added L1 is in parallel with L0: the pair is one inductor of L/2 and DCR/2. The +0.23 pp comes from halving the winding resistance, not from a new path (mech_verify.md S8: a single 250 uH / 0.125 Ohm inductor reproduces the child exactly).

**s0#01** -- same as s0#00 with the filter capacitor moved to OUT-0.

**s0#08** -- the added C0 (OUT-0, 72 mA) is an output filter capacitor that merges into the bench's own Cout (mech_verify.md S8: the parent with Cout = 20 uF reproduces the child). Its parent already contains the doubled series high-side switch, which is what costs the 0.05 pp.

## Note on converter (a)

THIS IS CONVERTER (a) IN THE PAPER. Two separate results below: its Sa1 || C1 branch is already in the corpus (train #23311), and replacing that branch with a wire is strictly better.

## Netlists, pruned forms and the matching corpus circuit

| # | as discovered | after deleting 0 A devices | matching corpus circuit |
|---|---|---|---|
| s0#00 | `Sb0 n1 0; L0 n1 OUT; Sa0 IN n1; C0 IN OUT; L1 n1 OUT` | `Sb0 n1 0; L0 n1 OUT; Sa0 IN n1; C0 IN OUT; L1 n1 OUT` | -- |
| s0#01 | `Sb0 n1 0; L0 n1 OUT; Sa0 IN n1; C0 OUT 0; L1 n1 OUT` | `Sb0 n1 0; L0 n1 OUT; Sa0 IN n1; C0 OUT 0; L1 n1 OUT` | -- |
| s0#02 | `Sa0 n3 IN; Sb0 n3 0; L0 OUT n3; C0 0 IN` | `Sa0 n3 IN; Sb0 n3 0; L0 OUT n3` | `Sa0 IN n6; Sb0 0 n6; L0 OUT n6` (train #4130, 5 copies) |
| s0#03 | `L0 OUT n5; Sb0 n5 IN; C0 OUT IN; L1 n3 IN; Sa0 n5 0; Sa1 n3 IN` | `L0 OUT n5; Sb0 n5 IN; C0 OUT IN; Sa0 n5 0` | `Sa0 0 n5; C0 IN OUT; Sb0 n5 IN; L0 n5 OUT` (train #40128, 5 copies) |
| s0#04 | `Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 OUT; Sa1 n0 OUT; C1 n0 OUT` | `Sb0 0 n7; Sa0 IN n7; L0 n7 OUT` | `Sa0 IN n6; Sb0 0 n6; L0 OUT n6` (train #4130, 5 copies) |
| s0#05 | `Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 OUT; Sb1 n0 OUT; C1 n0 0` | `Sb0 0 n7; Sa0 IN n7; L0 n7 OUT; Sb1 n0 OUT; C1 n0 0` | `L0 OUT n7; Sa0 IN n7; C0 0 n9; Sb0 OUT n9; Sb1 n7 0` (train #19363, 5 copies) |
| s0#06 | `Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 OUT; Sa1 n0 OUT; Sb1 n0 OUT` | `Sb0 0 n7; Sa0 IN n7; L0 n7 OUT` | `Sa0 IN n6; Sb0 0 n6; L0 OUT n6` (train #4130, 5 copies) |
| s0#07 | `Sb0 n3 IN; Sa0 n3 0; L0 OUT n3; C0 OUT IN` | `Sb0 n3 IN; Sa0 n3 0; L0 OUT n3; C0 OUT IN` | `Sa0 0 n5; C0 IN OUT; Sb0 n5 IN; L0 n5 OUT` (train #40128, 5 copies) |
| s0#08 | `Sb0 0 n7; Sa0 n0 n7; L0 n7 OUT; C0 0 OUT; Sa1 n0 IN; Sb1 n0 OUT` | `Sb0 0 n7; Sa0 n0 n7; L0 n7 OUT; C0 0 OUT; Sa1 n0 IN` | -- |
| s0#09 | `Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 n8; Sa1 OUT n8; C1 OUT n8` | `Sb0 0 n7; Sa0 IN n7; L0 n7 n8; Sa1 OUT n8; C1 OUT n8` | `L0 n7 n9; C0 OUT n9; Sa0 OUT n9; Sb0 0 n7; Sa1 IN n7` (train #23311, 5 copies) |
| s1#00 | `L0 OUT n9; C0 n0 IN; Sb0 IN n9; C1 n0 0; Sa0 0 n9` | `L0 OUT n9; Sb0 IN n9; Sa0 0 n9` | `Sa0 0 n6; Sb0 IN n6; L0 OUT n6` (train #24637, 6 copies) |
| s1#01 | `Sb0 n6 IN; C0 0 OUT; Sb1 n5 IN; L0 n6 IN; Sa0 0 n5; L1 OUT n5; Sa1 n6 IN` | `C0 0 OUT; Sb1 n5 IN; Sa0 0 n5; L1 OUT n5` | `Sa0 n5 0; C0 0 OUT; Sb0 IN n5; L0 n5 OUT` (train #8319, 5 copies) |
| s1#02 | `L0 OUT n9; C0 n0 0; Sb0 IN n9; C1 n0 0; Sa0 0 n9` | `L0 OUT n9; Sb0 IN n9; Sa0 0 n9` | `Sa0 0 n6; Sb0 IN n6; L0 OUT n6` (train #24637, 6 copies) |
| s1#03 | `L0 OUT n9; C0 n0 0; Sb0 0 n9; C1 n0 0; Sa0 IN n9` | `L0 OUT n9; Sb0 0 n9; Sa0 IN n9` | `Sa0 IN n6; Sb0 0 n6; L0 OUT n6` (train #4130, 5 copies) |
| s1#04 | `L0 OUT n9; C0 IN 0; C1 IN 0; Sb0 IN n9; C2 OUT IN; Sa0 0 n9` | `L0 OUT n9; Sb0 IN n9; C2 OUT IN; Sa0 0 n9` | `Sa0 0 n5; C0 IN OUT; Sb0 n5 IN; L0 n5 OUT` (train #40128, 5 copies) |

## Per-device currents (nominal duty, I_load = 1 A)

### s0#00  `Sb0 n1 0; L0 n1 OUT; Sa0 IN n1; C0 IN OUT; L1 n1 OUT`

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| Sb0 | S | 0.73442 | 1.500 | 0.50 | 31.98 |
| L0 | L | 0.52039 | 0.750 | 1.00 | 67.47 |
| Sa0 | S | 0.73747 | 1.500 | 0.50 | 32.18 |
| C0 | C | 0.14438 | 0.250 | 0.96 | 0.63 |
| L1 | L | 0.52039 | 0.750 | 1.00 | 67.47 |

### s0#01  `Sb0 n1 0; L0 n1 OUT; Sa0 IN n1; C0 OUT 0; L1 n1 OUT`

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| Sb0 | S | 0.73442 | 1.500 | 0.50 | 31.98 |
| L0 | L | 0.52039 | 0.750 | 1.00 | 67.47 |
| Sa0 | S | 0.73747 | 1.500 | 0.50 | 32.18 |
| C0 | C | 0.14438 | 0.250 | 0.96 | 0.62 |
| L1 | L | 0.52039 | 0.750 | 1.00 | 67.47 |

### s0#02  `Sa0 n3 IN; Sb0 n3 0; L0 OUT n3; C0 0 IN`

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| Sa0 | S | 0.71675 | 1.250 | 0.50 | 30.66 |
| Sb0 | S | 0.71213 | 1.250 | 0.50 | 30.38 |
| L0 | L | 1.01037 | 1.250 | 1.00 | 255.00 |
| C0 **(0 A)** | C | 0.00000 | 0.000 | 0.00 | 0.00 |

### s0#03  `L0 OUT n5; Sb0 n5 IN; C0 OUT IN; L1 n3 IN; Sa0 n5 0; Sa1 n3 IN`

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| L0 | L | 1.01037 | 1.250 | 1.00 | 254.98 |
| Sb0 | S | 0.71674 | 1.250 | 0.50 | 30.66 |
| C0 | C | 0.07217 | 0.125 | 0.92 | 0.14 |
| L1 **(0 A)** | L | 0.00000 | 0.000 | 0.00 | 0.00 |
| Sa0 | S | 0.71213 | 1.250 | 0.50 | 30.38 |
| Sa1 **(0 A)** | S | 0.00000 | 0.000 | 0.00 | 0.00 |

### s0#04  `Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 OUT; Sa1 n0 OUT; C1 n0 OUT`

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| Sb0 | S | 0.71213 | 1.250 | 0.50 | 30.38 |
| Sa0 | S | 0.71674 | 1.250 | 0.50 | 30.66 |
| C0 **(0 A)** | C | 0.00000 | 0.000 | 0.00 | 0.00 |
| L0 | L | 1.01037 | 1.250 | 1.00 | 255.02 |
| Sa1 **(0 A)** | S | 0.00000 | 0.000 | 0.00 | 0.00 |
| C1 **(0 A)** | C | 0.00000 | 0.000 | 0.00 | 0.00 |

### s0#05  `Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 OUT; Sb1 n0 OUT; C1 n0 0`

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| Sb0 | S | 0.71213 | 1.250 | 0.50 | 30.38 |
| Sa0 | S | 0.71674 | 1.250 | 0.50 | 30.66 |
| C0 **(0 A)** | C | 0.00000 | 0.000 | 0.00 | 0.00 |
| L0 | L | 1.01037 | 1.250 | 1.00 | 255.03 |
| Sb1 | S | 0.04075 | 0.113 | 0.46 | 0.08 |
| C1 | C | 0.04075 | 0.113 | 0.46 | 0.07 |

### s0#06  `Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 OUT; Sa1 n0 OUT; Sb1 n0 OUT`

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| Sb0 | S | 0.71213 | 1.250 | 0.50 | 30.38 |
| Sa0 | S | 0.71675 | 1.250 | 0.50 | 30.66 |
| C0 **(0 A)** | C | 0.00000 | 0.000 | 0.00 | 0.00 |
| L0 | L | 1.01037 | 1.250 | 1.00 | 254.98 |
| Sa1 **(0 A)** | S | 0.00000 | 0.000 | 0.00 | 0.00 |
| Sb1 **(0 A)** | S | 0.00000 | 0.000 | 0.00 | 0.00 |

### s0#07  `Sb0 n3 IN; Sa0 n3 0; L0 OUT n3; C0 OUT IN`

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| Sb0 | S | 0.71674 | 1.250 | 0.50 | 30.66 |
| Sa0 | S | 0.71213 | 1.250 | 0.50 | 30.38 |
| L0 | L | 1.01037 | 1.250 | 1.00 | 254.98 |
| C0 | C | 0.07217 | 0.125 | 0.92 | 0.14 |

### s0#08  `Sb0 0 n7; Sa0 n0 n7; L0 n7 OUT; C0 0 OUT; Sa1 n0 IN; Sb1 n0 OUT`

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| Sb0 | S | 0.71199 | 1.250 | 0.50 | 30.37 |
| Sa0 | S | 0.71700 | 1.250 | 0.50 | 26.95 |
| L0 | L | 1.01043 | 1.250 | 1.00 | 254.94 |
| C0 | C | 0.07213 | 0.125 | 0.92 | 0.08 |
| Sa1 | S | 0.71703 | 1.250 | 0.50 | 26.95 |
| Sb1 **(0 A)** | S | 0.00004 | 0.000 | 0.00 | 1.26 |

### s0#09  `Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 n8; Sa1 OUT n8; C1 OUT n8`

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| Sb0 | S | 0.71076 | 1.251 | 0.49 | 30.31 |
| Sa0 | S | 0.71828 | 1.251 | 0.51 | 30.75 |
| C0 **(0 A)** | C | 0.00000 | 0.000 | 0.00 | -0.00 |
| L0 | L | 1.01049 | 1.251 | 1.00 | 255.02 |
| Sa1 | S | 1.72416 | 7.209 | 0.51 | 148.64 |
| C1 | C | 1.46692 | 6.460 | 0.97 | 64.42 |

### s1#00  `L0 OUT n9; C0 n0 IN; Sb0 IN n9; C1 n0 0; Sa0 0 n9`

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| L0 | L | 1.01038 | 1.250 | 1.00 | 254.97 |
| C0 **(0 A)** | C | 0.00000 | 0.000 | 0.00 | 0.00 |
| Sb0 | S | 0.71675 | 1.250 | 0.50 | 30.66 |
| C1 **(0 A)** | C | 0.00000 | 0.000 | 0.00 | -0.00 |
| Sa0 | S | 0.71214 | 1.250 | 0.50 | 30.38 |

### s1#01  `Sb0 n6 IN; C0 0 OUT; Sb1 n5 IN; L0 n6 IN; Sa0 0 n5; L1 OUT n5; Sa1 n6 IN`

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| Sb0 **(0 A)** | S | 0.00000 | 0.000 | 0.00 | 0.00 |
| C0 | C | 0.07217 | 0.125 | 0.92 | 0.17 |
| Sb1 | S | 0.71674 | 1.250 | 0.50 | 30.66 |
| L0 **(0 A)** | L | 0.00000 | 0.000 | 0.00 | 0.00 |
| Sa0 | S | 0.71213 | 1.250 | 0.50 | 30.38 |
| L1 | L | 1.01037 | 1.250 | 1.00 | 254.98 |
| Sa1 **(0 A)** | S | 0.00000 | 0.000 | 0.00 | 0.00 |

### s1#02  `L0 OUT n9; C0 n0 0; Sb0 IN n9; C1 n0 0; Sa0 0 n9`

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| L0 | L | 1.01037 | 1.250 | 1.00 | 254.98 |
| C0 **(0 A)** | C | 0.00000 | 0.000 | 0.00 | 0.00 |
| Sb0 | S | 0.71675 | 1.250 | 0.50 | 30.66 |
| C1 **(0 A)** | C | 0.00000 | 0.000 | 0.00 | 0.00 |
| Sa0 | S | 0.71213 | 1.250 | 0.50 | 30.38 |

### s1#03  `L0 OUT n9; C0 n0 0; Sb0 0 n9; C1 n0 0; Sa0 IN n9`

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| L0 | L | 1.01037 | 1.250 | 1.00 | 254.98 |
| C0 **(0 A)** | C | 0.00000 | 0.000 | 0.00 | 0.00 |
| Sb0 | S | 0.71213 | 1.250 | 0.50 | 30.38 |
| C1 **(0 A)** | C | 0.00000 | 0.000 | 0.00 | 0.00 |
| Sa0 | S | 0.71675 | 1.250 | 0.50 | 30.66 |

### s1#04  `L0 OUT n9; C0 IN 0; C1 IN 0; Sb0 IN n9; C2 OUT IN; Sa0 0 n9`

| device | kind | I_rms A | I_peak A | U | P_loss mW |
|---|---|---|---|---|---|
| L0 | L | 1.01037 | 1.250 | 1.00 | 255.01 |
| C0 **(0 A)** | C | 0.00000 | 0.000 | 0.00 | 0.00 |
| C1 **(0 A)** | C | 0.00000 | 0.000 | 0.00 | 0.00 |
| Sb0 | S | 0.71674 | 1.250 | 0.50 | 30.66 |
| C2 | C | 0.07217 | 0.125 | 0.92 | 0.14 |
| Sa0 | S | 0.71213 | 1.250 | 0.50 | 30.38 |

