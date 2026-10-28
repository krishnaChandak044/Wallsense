# November 2–4: heavy testing, repairs, demo, submission

This work starts **after** the six build days. Tests during the build are limited to fast checks needed to keep each day’s output usable. This phase deliberately tests failures and claims hard.

## Monday, November 2 — science and system audit

### Evaluation audit

- Rerun all published metrics from frozen model/split hashes. Confirm sample and group counts and that no recording/subject/session crosses train and test.
- Inspect Wallhack per-class errors and NLOS/BQ/PIFA breakdown; explicitly compare any LOS-to-NLOS transfer gap. Report uncertainty coverage and both false alerts and missed motion, not only accuracy.
- Audit CSI-Bench fall label meaning, split, false positives, false negatives, and whether NLOS is documented. Do not present clip-level classification as event-level detection.
- Corrupt held-out inputs in controlled ways: packet drop, missing subcarriers, amplitude scale, timing jitter. Label this stress test as artificial. Measure whether quality/abstention prevents false confidence.
- Test agent grounding against a fixed question set; record tool traces, claim errors, missing citations, and unsupported health/location answers. Fix prompt/tool boundaries at the server, not only wording.

### System audit

- Repeated replay determinism, WebSocket reconnect/seek, concurrent requests, large input/malformed archive, path traversal, unavailable Meta API, missing model, and report/UI ledger consistency.
- Measure startup time, per-window p50/p95 latency, replay jitter, and actual Meta API cost. Document machine specs.
- Make a severity-ranked blocker list. Freeze a stable build by evening.

## Tuesday, November 3 — demo and independent review

- Give the app to a fresh reviewer with only README instructions. Note every step requiring hidden knowledge. Fix install or interface blockers.
- Rehearse the three-minute flow twice without editing around failures. Choose camera framing/screen scale so scores, source labels, and tool traces are readable.
- Record the demo video with a clear label for recorded replay. Demonstrate actual Meta calls and a frozen challenge before reveal. Include one limitation in spoken narration.
- Draft public repo README, architecture diagram, model/data cards, metric table, exact event-period work statement, dataset attribution, and “how Meta is used.”
- Check Git for large data files, `.env`, keys, personal messages, local paths, and generated outputs that should not be public. Verify a logged-out browser can open the public repo and video.
- Prepare submission text and all links; do not wait for final day to write them.

## Wednesday, November 4 — final verification and early submit

- Run one clean start and one full challenge. Verify model/artifact hashes and that displayed metrics equal generated report files.
- Rewatch the final video for legibility, audio, timing, no hidden claims, and no misleading “live” wording.
- Check the current official submission instructions and deadline. Submit the CV form with every teammate if required, public GitHub repo, and three-minute video. Complete submission **well before** 9:00 PM ET.
- Open submitted links logged out. Save a local copy of the final form confirmation, repo commit hash, video link, and results JSON.
- After submission, stop risky edits. Keep an exact copy of what judges will see.

## Release blockers

Do not publish a build that exposes raw licensed data or secrets, fabricates live sensing, leaks challenge truth, combines the two datasets into one person’s report, labels an unverified fall as through-wall, gives numerical vitals without reference labels, or cites metrics that cannot be reproduced. Fix or remove the affected feature before submitting.

## Submission evidence package

1. Public GitHub repository accessible when logged out.
2. Three-minute demo video featuring only work built during the event.
3. Running app or clear local setup path accepted by the rules.
4. Evaluation JSON/figures with exact split and denominators.
5. Model/data cards, attribution, permission summary, limitations, and API integration description.
6. Screenshot or confirmation of submission before the deadline.
