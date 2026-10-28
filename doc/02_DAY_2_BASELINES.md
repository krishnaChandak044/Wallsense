# Day 2 — Wednesday, October 28: real baselines

## Goal

Produce reproducible baseline results from held-out data. Today establishes what the product can actually detect; it is not a day for a sophisticated architecture with no comparison.

## Wallhack motion pipeline

1. Stream raw packets in recording order. Validate timing, packet loss, I/Q length, and finite values. Select documented usable subcarriers; keep a schema version.
2. Form non-overlapping four-second windows as a starting point, respecting recording boundaries. Skip/flag mixed-label windows with counts by class and domain. If a different window length is used, justify and freeze it before test evaluation.
3. Calculate simple signal features: per-subcarrier amplitude statistics, temporal variance, motion-band spectral power, phase-difference stability where physically meaningful, and missingness. Compute normalization on **training recordings only**; avoid full-recording normalization that uses future or holdout data.
4. Train a transparent majority/dummy baseline, a binary motion-versus-no-presence model, and a three-class ExtraTrees or logistic baseline. Use the exact same split and preprocessing for comparisons. Save feature schema, model version, seed, dependency versions, and artifact hash.
5. Select hyperparameters from training/validation only. Evaluate once on frozen test groups. Publish confusion matrices, macro F1, balanced accuracy, per-class recall, and LOS/NLOS counts. Evaluate NLOS separately because that supports the through-wall story.
6. Run one deliberate domain-shift test if group support permits: LOS-trained → NLOS-tested, or BQ → PIFA. If it performs poorly, retain the result and make uncertainty central.

## CSI-Bench fall feasibility and baseline

1. Confirm exact fall classes and positive event timing. Determine whether a “fall” label denotes a whole clip or a timestamped event. Do not create event-level latency claims from clip-level labels.
2. Inspect class and group counts before selecting the model. Use an author-provided split only if it is documented and leakage-safe; otherwise create a subject/session held-out split and publish the group IDs/hash.
3. Train a trivial baseline and a small source-specific fall classifier using only CSI-Bench inputs. Use preprocessing fitted on its train groups. Save its own scaler, schema, and artifact; no Wallhack classifier is applied to these frames.
4. Evaluate sensitivity/recall, precision, false-positive count/rate, confusion matrix, and macro F1 with denominators. For event-level claims, implement event aggregation and duration accounting first.
5. Inspect whether the held-out fall data includes NLOS. If absent, the UI wording is “fall-related classification on CSI-Bench replay,” not “person fell behind the wall.”

## Breathing and heart-rate decision

Inspect CSI-Bench BreathingDetection metadata for a real binary/multiclass label. If valid, record as an optional separate task. A breathing-detection label is **not** breaths/minute. Heart rate requires paired ground-truth BPM/ECG and adequate windows; neither dataset is assumed to supply this. Keep that report row `not_measured` until such data is actually verified.

## Minimal verification today

Run model fit and evaluation twice with the same seed to verify identical split/hash/metrics; assert training sees no test group; inspect one decoded signal visually and one held-out prediction manually. The broader stress campaign is reserved for Nov 2–4.

## Output artifacts and exit gate

Training commands, metrics JSON, confusion matrices, model cards, hashes, and a short error analysis. **Exit:** Wallhack has an end-to-end real-data benchmark; CSI-Bench has either an evaluated baseline or a documented exact blocker with a time-boxed plan to resolve it by Day 3.

## Recorded Day 1–2 result (Oct 27)

The initial pipelines now run end to end. Keep these results as baselines, not claims of product readiness:

- **Wallhack1.8k:** 1,822 four-second windows, recording-level split (1,024 train / 399 validation / 399 test). Three-class activity test macro-F1 is **0.314**; binary motion macro-F1 is **0.448** and balanced accuracy is **0.530**. The test has 149 no-presence windows and the motion classifier correctly labels only 9 as no-presence (recall **0.060**). This is not reliable occupancy detection, and the NLOS false-positive behavior is a clear failure mode.
- **CSI-Bench FallDetection v12:** bounded, user-disjoint pilot, 725 downloaded files retained after 315 selected files were unavailable (465 train / 127 validation / 133 test; test users U12 and U13). ExtraTrees validation macro-F1 is **0.912**; test macro-F1 is **0.932** with confusion matrix `[[59, 4], [5, 65]]`. Treat this result as encouraging but provisional: the incomplete selection, only two held-out test users, and untested environment/session/device shift prevent broad generalization claims. It is clip-level fall/nonfall classification, not event detection, and does not establish through-wall or medical performance.

Artifacts are in ignored `artifacts/` and raw CSI remains local. Freeze this CSI-Bench test result; use train/validation and additional group/domain analyses for iteration. The next gate is error analysis and robustness checks before any Baseten deployment or stronger user-facing claim. See `artifacts/wallhack_test_metrics.json`, `artifacts/csibench_fall_test_metrics.json`, and `artifacts/csibench_pilot_prepare.json`.
