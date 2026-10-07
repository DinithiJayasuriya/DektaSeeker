# VERSION 6 on POWER CONVERTERS   (built 2026-09-13)

Same discovery loop as the op-amp VERSION 4/5/6 arms, with the domain plugs swapped. Nothing in
run_outer_nsga_cv3.py, repair_v5.py or controller_v6.py was edited.

## Launch
    agents/steering_dev/launch_conv_v6.sh <seed> [out] [extra args]
        V6=1 -> conv_g6_v6_s<seed>   V7=1 -> conv_g6_v7_s<seed>   V4=1 -> conv_g6_v4_s<seed>   default = V5 arm
        SMOKE=1 (pop 12, 2 gens)   GPU=<idx> (default 1)   WORKERS=<ngspice procs> (default 24)
Outputs land in CCT_Generation/setup_tracer/runs/<out>/ with the SAME files as the op-amp runs
(gen*_pop.pt, pareto_front.json, discovered.json, v5_monitor.json, v5_repairs/, v6_trajectory.json,
v6_actions.txt, v6_usage.json, gen0_cands.pt, run.log).

## Files
    CCT_Generation/setup_tracer/scripts/run_outer_nsga_conv.py   driver; imports run_outer_nsga_cv3 for NSGA-II,
                                                                 SMC gen-0, SDEdit/birth tournament, race_front,
                                                                 rescue_pass, discovered set, save_state; imports
                                                                 controller_v6.DiscoveryControllerV6 unchanged
    steergense_agent/converter/conv_evaluator.py    ConverterEvaluator (same rec schema as cv3.Evaluator),
                                                    graded_health (SMC + birth tournament), spawn-pool workers
    steergense_agent/converter/conv_repair.py       ConvChecker / ConvRewirer / ConvRepairProposer /
                                                    ConvRepairController (v5 twin) / ConvRuleRepairer +
                                                    ConvLLMRescue (rescue_pass twins)
    steergense_agent/converter/conv_novelty.py      WL novelty vs the 37,514 DISTINCT LaMAGIC training graphs
                                                    (cached sparse matrix conv_novelty_ref_lamagic.npz, 0.7 ms/score)
    steergense_agent/converter/spec.py              spec sheet, duty REFINEMENT, CORNERS, violation vector
    steergense_agent/converter/bench.py             transient bench (+ per-call operating-point override)
    CCT_Generation/setup_tracer/DiGress/src/datasets/lamagic_dataset.py, analysis/converter_validity.py
                                                    copied from CCT_Generation/DiGress (the training copy) so the
                                                    v6 stack's DiscreteDenoisingDiffusion can load lamagic_v1

## Generator
lamagic_v1 last-v1.ckpt (epoch 59), loaded through setup_tracer's model class: all 306 tensors matched.
Conditioning = duty-cycle label (5 classes); default --guidance_class 2 (D=0.5), --guidance_scale 0 (label fed,
no CFG amplification). Probe (48 samples each): 71-83% pass the strict validity gate, 0/100 met the 2:1 sheet
BEFORE duty refinement; 20-30% are pass-throughs. SMC gen-0 uses the converter gate as health; the conformal
pruner (prune3) is op-amp-calibrated and is NOT used here.

## Evaluator vocabulary (kept so every readout works unchanged)
    median_gain    efficiency in PERCENT at the chosen operating point (median over corners)
    feasible       |Vout-50| <= 5%, ripple <= 5% of Vout, output responds to duty (>= 1 V spread),
                   efficiency >= --conv_eff_floor (default 0.90)  -- at SOME duty (5-point sweep + <= 2 secant steps)
    k / seeds      OPERATING CORNERS: 0 nominal, 1 heavy load (ROUT/2), 2 light load (2*ROUT),
                   3 low line (0.9 VIN) with -20% L/C/COUT.  robust = nominal feasible AND > half the corners
    gain_spread    max-min efficiency % across corners;  feasible_frac = corners meeting the spec
    con_vec        [vout_error % over tol, ripple pp over limit, duty_response shortfall V, efficiency pp under floor]
    one 'sizing'   one corner evaluation (~20 s ngspice: 5 duties + refinement)
    stage          struct_reject (strict gate fails) | dead (no duty simulates) | scored
Textbook buck: feasible at all 4 corners (eff 98.8-99.6%, duty 0.50-0.56); boost / buck-boost: infeasible
(Vout 110 / -11 V), cv_raw 0.25 (inside the 0.3 rescue band).

## Tools (same names, converter mechanics)
    REPAIR   ConvChecker names faulty TERMINALS: UNBOUND_PIN, NET_FLOATING, DISCONNECTED, SHOOT_THROUGH (the closed
             switches that short IN-0 in a phase), VOUT_SHORT, NO_VIN_VOUT_PATH; EXTRA_PIN / RAIL_* / class faults
             are not repairable. LLM edit = 'connect FAULT k to NET j' (genome space, exactly invertible: the
             genome IS the device-net graph). Re-checked (no new strong faults) before SPICE.
    RESCUE   rule has NO op for a valid-but-off-spec converter; ConvLLMRescue proposes <= 2 of add_L / add_C /
             swap_phase / rewire, validity-gated as a set; kept if feasible or strictly closer (cv_raw).
    RACING / VERIFY   extend to more corners (ev.extend);  STEER  t_frac / birth_m as before.
    'op probe' = one nominal transient at D=0.5 on dead children.
Controller prompt: _CONV_SYSTEM in run_outer_nsga_conv.py (same schema, same validation, converter wording).

## Tested
bench lossless gate still 0.0% after the params change; spec corners on buck/boost/buck-boost; evaluator
(k=1 -> extend to 4); checker + mock-LLM repair (broken buck -> feasible buck, RECOVERED); rescue edit paths
(gate rejects a breaking single edit; two rewires turn a boost into a feasible step-down; add_C valid);
smoke V4 arm end to end (see runs/conv_smoke_v4).
