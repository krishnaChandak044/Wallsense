# Day 3 — Thursday, October 29: uncertainty, events, and evidence

## Goal

Transform raw per-window scores into useful, inspectable events with explicit data quality and uncertainty. Finish the decision on whether the fall lane is ready for product integration.

## Quality gate

- Implement deterministic integrity checks: bad I/Q shape, missing timestamps, implausible packet rate, severe packet gaps, non-finite values, flatline/saturated amplitude, and missing critical subcarriers.
- Evaluate phase/coherence features only if validated; a complicated “coherence gate” is not inherently safer. Compare with and without it on the same validation set. Drop any rule that removes many valid positives without a measurable benefit.
- Define `ACCEPT`, `HOLD`, `REJECT`, and `RECALIBRATE`/`OUT_OF_SCOPE` states with reason codes and measured quantities. A rejected window cannot produce a confident person/fall event.
- Build a quality timeline that can be explained to a judge in one sentence for each state.

## Confidence and abstention

- Calibrate probabilities or label them honestly as uncalibrated model scores. Choose any acceptance/abstention threshold on validation groups only. Never tune it on the hidden challenge/test labels.
- Report risk versus coverage: accepted fraction, accuracy/false-alert performance of accepted windows, and excluded positive count. Include domain breakdown; a single global confidence number can conceal NLOS weakness.
- Support `UNCERTAIN` and `UNSUPPORTED_TASK` as first-class outputs. A model cannot silently fall back to “no person” when input is low quality.

## Event builder and evidence ledger

- Aggregate consecutive accepted windows into events with documented debounce and cooldown; preserve raw window outputs for audit. Event contains `event_id`, dataset/capture source, task, model hash, recording ID, start/end, score, quality status, feature summaries, window IDs, and provenance hash.
- Persist to SQLite or deterministic JSON with an append-only prediction ledger. The same recording and model version must produce the same event sequence in repeat runs.
- Create read-only evidence functions that will later become agent tools: `get_event`, `get_signal_summary`, `get_model_decision`, `get_quality`, `get_evaluation_scope`, and `compare_events`. Return bounded JSON and never raw file paths or test labels.
- Make report rows source-aware: motion, fall, breathing, and heart rate each show `supported`, `uncertain`, `not_measured`, or `error`, with a reason and provenance. A Wallhack session’s fall row remains `not_measured` even if the separate CSI-Bench fall model exists.

## Fall lane promotion gate

Promote CSI-Bench fall classification only if its labels, capture schema, group-safe split, held-out result, and task wording are defensible. The gate is documented in the model card. Otherwise preserve it as a research experiment and focus on shipping a complete motion investigation product. If breathing data passes its own gate, schedule it after feature completion; it must never delay the two-lane core.

## Minimal verification today

Test that corrupt input cannot create a confident event, repeated replay creates identical event IDs, and unsupported report rows are explicit. Review several false positives and missed events by hand. Record the threshold and why it was chosen.

## Exit gate

Both available classifiers feed a common evidence interface; quality and abstention are visible; the CSI-Bench fall release decision is made; and the ledger is stable enough to power API and UI work.
