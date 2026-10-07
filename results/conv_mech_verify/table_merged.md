# Child vs nearest training parent: performance and mechanism (conv_g20_v6_s0)

Parent = nearest LaMAGIC sample by exact isomorphism; child = parent + one device. Corner numbers: 4-corner re-simulation under the run's spec (duty re-refined per corner). Activity and stress: fixed-duty waveform probe at the nominal corner, I_load = 1 A. Δ = child − parent; ripple = max over the 4 corners.

| Design | Added device (parent sample) | Added element active? (U, I_rms/I_load) | Feasible corners parent → child | Median η % parent → child (Δ) | Worst-corner η % parent → child (Δ) | Max ripple mV parent → child (Δ) | Peak stress on added element | Mechanism verified? |
|---|---|---|---|---|---|---|---|---|
| a | second inductor in parallel (#9562) | yes (U 1.00, 0.52) | 4/4 → 4/4 (0) | 99.37 → **99.60** (+0.23) | 98.80 → **99.28** (+0.48) | 44 → 88 (+44) | 50 V, 0.75 A | trade-off: η gain from halved winding resistance, ripple ×2 (still 0.18 % of Vout) |
| b | input capacitor (#19363) | no (U 0.00, zero current) | 4/4 → 4/4 (0) | 99.37 → 99.37 (0) | 98.80 → 98.80 (0) | 72 → 72 (0) | 100 V, 0 A | no: sits across the ideal source, redundant |
| c | output capacitor (#415) | yes (U 0.92, 0.07) | 4/4 → 4/4 (0) | 99.32 → 99.32 (0) | 98.70 → 98.70 (0) | 87 → **44** (−43) | 50 V, 0.12 A | ripple suppression only; equivalent to a 20 µF output cap |
| d | capacitor across Sa1 (#10271) | yes (U 0.97, 1.47) | **0/4 → 4/4** (+4) | 31.2 → **98.96** (+67.8) | 16.8 → **97.99** (+81.2) | 251 → 88 (−163) | 0.6 V, **6.5 A** | yes: new freewheel path makes it a converter; cost = 6.5 A / 7.2 A peaks through C1 / Sa1 and 0.4 pp below the textbook buck |
| ref | textbook buck (#6935) | – | 4/4 | 99.37 | 98.80 | 87 | – | – |
