# Converter (a): is C1's 97 % conduction real, or an ideal-switch artifact?

Child `Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 n8; Sa1 OUT n8; C1 OUT n8`

Parent (#10271) `Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 n8; Sa1 OUT n8`

Waveforms at the child's refined nominal duty D = 0.5052, last 20 of 2,000 periods,
0 V ammeters in series with every switch, diode and capacitor. I_load = 1 A.
U = fraction of the period with |i| > 1 % I_load -- the same definition mech_verify.md uses.

## A. Waveform re-measurement, child

| switch model | U(C1) | I_rms(C1) A | I_peak(C1) A | U(Sa1) | I_rms(Sa1) A | I_rms(body diode of Sa1) A | Vout V | eff % | integration |
|---|---|---|---|---|---|---|---|---|---|
| `ideal_roff1e6` -- as run: ideal SW, no body diode | 0.97 | 1.467 | 6.460 | 0.51 | 1.724 | -- | 50.00 | 98.95 | trap |
| `ideal_roff1e4` -- ideal SW, 100x leakier off-state | 0.97 | 1.467 | 6.460 | 0.51 | 1.724 | -- | 50.00 | 97.05 | trap |
| `ideal_roff1e9` -- ideal SW, 1000x tighter off-state | 0.97 | 1.467 | 6.460 | 0.51 | 1.724 | -- | 50.00 | 98.97 | trap |
| `diode_Sa1_ab` -- Sa1 is a real switch, body diode OUT->n8 (blocks the freewheel direction) | 0.97 | 1.467 | 6.767 | 0.51 | 1.724 | 0.004 | 50.00 | 98.95 | trap |
| `diode_Sa1_ba` -- Sa1 is a real switch, body diode n8->OUT (conducts the freewheel direction) | 0.97 | 1.466 | 6.506 | 0.51 | 1.723 | 0.003 | 50.00 | 98.95 | gear |

## B. 4-corner feasibility under each switch model

| switch model | child feasible corners | child eff median % | parent feasible corners | parent eff median % |
|---|---|---|---|---|
| `ideal_roff1e6` | **4/4** | 98.96 | **0/4** | -- |
| `ideal_roff1e4` | **4/4** | 97.05 | **0/4** | -- |
| `ideal_roff1e9` | **4/4** | 98.98 | **0/4** | -- |
| `diode_Sa1_ab` | **4/4** | 98.96 | **0/4** | -- |
| `diode_Sa1_ba` | **4/4** | 98.96 | **4/4** | 98.32 |

## C. Per-element detail, child, each switch model

### `ideal_roff1e6` -- as run: ideal SW, no body diode
Vout 50.00 V, eff 98.95 %, ripple 64 mV, Pin 50.536 W, element loss 529.1 mW

| element | kind | I_rms A | I_peak A | I_mean A | U | V_peak V | P_loss mW |
|---|---|---|---|---|---|---|---|
| Sb0 | S | 0.711 | 1.251 | +0.4947 | 0.49 | 100.0 | 30.3 |
| Sa0 | S | 0.718 | 1.251 | +0.5054 | 0.51 | 100.1 | 30.7 |
| C0 | C | 0.000 | 0.000 | -0.0000 | 0.00 | 100.0 | -0.0 |
| L0 | L | 1.010 | 1.251 | +1.0001 | 1.00 | 50.6 | 255.0 |
| Sa1 | S | 1.724 | 7.209 | -1.0001 | 0.51 | 0.6 | 148.6 |
| C1 | C | 1.467 | 6.460 | +0.0000 | 0.97 | 0.6 | 64.4 |

### `ideal_roff1e4` -- ideal SW, 100x leakier off-state
Vout 50.00 V, eff 97.05 %, ripple 64 mV, Pin 51.526 W, element loss 1519.1 mW

| element | kind | I_rms A | I_peak A | I_mean A | U | V_peak V | P_loss mW |
|---|---|---|---|---|---|---|---|
| Sb0 | S | 0.704 | 1.241 | +0.4848 | 0.49 | 100.0 | 529.6 |
| Sa0 | S | 0.725 | 1.261 | +0.5153 | 1.00 | 100.1 | 521.5 |
| C0 | C | 0.000 | 0.000 | -0.0000 | 0.00 | 100.0 | -0.0 |
| L0 | L | 1.010 | 1.251 | +1.0001 | 1.00 | 50.6 | 255.0 |
| Sa1 | S | 1.724 | 7.209 | -1.0001 | 0.51 | 0.6 | 148.6 |
| C1 | C | 1.467 | 6.460 | +0.0000 | 0.97 | 0.6 | 64.4 |

### `ideal_roff1e9` -- ideal SW, 1000x tighter off-state
Vout 50.00 V, eff 98.97 %, ripple 64 mV, Pin 50.526 W, element loss 519.1 mW

| element | kind | I_rms A | I_peak A | I_mean A | U | V_peak V | P_loss mW |
|---|---|---|---|---|---|---|---|
| Sb0 | S | 0.711 | 1.251 | +0.4948 | 0.49 | 100.0 | 25.3 |
| Sa0 | S | 0.718 | 1.251 | +0.5053 | 0.51 | 100.1 | 25.8 |
| C0 | C | 0.000 | 0.000 | -0.0000 | 0.00 | 100.0 | -0.0 |
| L0 | L | 1.010 | 1.251 | +1.0001 | 1.00 | 50.6 | 255.0 |
| Sa1 | S | 1.724 | 7.209 | -1.0001 | 0.51 | 0.6 | 148.6 |
| C1 | C | 1.467 | 6.460 | +0.0000 | 0.97 | 0.6 | 64.4 |

### `diode_Sa1_ab` -- Sa1 is a real switch, body diode OUT->n8 (blocks the freewheel direction)
Vout 50.00 V, eff 98.95 %, ripple 64 mV, Pin 50.536 W, element loss 529.1 mW

| element | kind | I_rms A | I_peak A | I_mean A | U | V_peak V | P_loss mW |
|---|---|---|---|---|---|---|---|
| Sb0 | S | 0.711 | 1.251 | +0.4947 | 0.49 | 100.0 | 30.3 |
| Sa0 | S | 0.718 | 1.251 | +0.5054 | 0.51 | 100.1 | 30.7 |
| C0 | C | 0.000 | 0.000 | +0.0000 | 0.00 | 100.0 | 0.0 |
| L0 | L | 1.010 | 1.251 | +1.0001 | 1.00 | 50.6 | 255.0 |
| Sa1 | S | 1.724 | 7.506 | -1.0001 | 0.51 | 0.6 | 148.6 |
| D_Sa1 | D | 0.004 | 0.790 | +0.0000 | 0.00 | 0.6 | -0.0 |
| C1 | C | 1.467 | 6.767 | +0.0000 | 0.97 | 0.6 | 64.4 |

### `diode_Sa1_ba` -- Sa1 is a real switch, body diode n8->OUT (conducts the freewheel direction)
Vout 50.00 V, eff 98.95 %, ripple 64 mV, Pin 50.536 W, element loss 529.4 mW

| element | kind | I_rms A | I_peak A | I_mean A | U | V_peak V | P_loss mW |
|---|---|---|---|---|---|---|---|
| Sb0 | S | 0.711 | 1.251 | +0.4947 | 0.49 | 100.0 | 30.3 |
| Sa0 | S | 0.718 | 1.251 | +0.5054 | 0.51 | 100.1 | 30.7 |
| C0 | C | 0.000 | 0.000 | -0.0000 | 0.00 | 100.0 | -0.0 |
| L0 | L | 1.010 | 1.251 | +1.0001 | 1.00 | 50.6 | 255.3 |
| Sa1 | S | 1.723 | 7.747 | -0.9996 | 0.51 | 0.6 | 148.5 |
| D_Sa1 | D | 0.003 | 1.434 | -0.0000 | 0.00 | 0.6 | -0.0 |
| C1 | C | 1.466 | 6.506 | -0.0005 | 0.97 | 0.6 | 64.5 |

