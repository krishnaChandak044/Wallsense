# Day 6 — Sunday, November 1: integrated release candidate

## Goal

Finish the product, make it runnable, and freeze features. November 2–4 are for hard testing and submission, not a new architecture.

## Complete the integrated path

- Start from a clean install. Verify data import, model loading, replay, event inspection, report, Meta tool flow, challenge freeze/reveal, and evaluation page in that order.
- Freeze model artifacts, feature schema, split manifests, threshold config, source/version metadata, and API response schemas. A later test bug fix may change them only with a new version and rerun of dependent metrics.
- Make a “quick demo” script that validates required local dataset files and starts backend/frontend. If a licensed dataset cannot be redistributed, document its exact official retrieval and expected checksum; never auto-substitute synthetic data.
- Polish loading, empty, offline, malformed-file, low-confidence, and Meta-unavailable states. Remove any placeholder alert, canned response, fake animation, or unsupported statistic from the build.
- Finish README: what the app does, no-hardware recorded-replay limitation, supported datasets/tasks, setup, commands, screenshots, Meta setup, API cost behavior, evaluation reproduction, rights/attribution, and safety/limitations.
- Generate model cards for both promoted lanes and a data card for each source. Preserve source authors and licenses/permission notes. Keep private permission correspondence outside the public repository unless sharing is clearly authorized.

## Demo narrative and assets

Draft a 180-second story: problem (15s), real NLOS replay (35s), event evidence/Meta investigation (45s), challenge selection/freezing/reveal (55s), report plus CSI-Bench fall lane or limitation (20s), measured result and close (10s). Time this rather than assuming it fits.

Choose one NLOS example and one honest difficult case for a guided walkthrough; Challenge Mode remains judge-selectable. If the CSI-Bench fall lane is promoted, show it as a second source-specific mode with its own held-out metric. Do not splice the two sources into a fake continuous scenario.

## Release-candidate review

Use the orientation rubric as a checklist:

- **Impact:** is the use case concrete and the output actionable within research scope?
- **Meta AI:** would removing the agent materially weaken the investigation? Can judges see actual tool calls?
- **Technical depth:** can we show splits, error analysis, uncertainty, and source-compatible inference?
- **Demo:** can the entire workflow be captured in three minutes without manual repair?

Perform a short threat/claim review: hidden labels, raw data exposure, path traversal, API key leakage, dataset redistribution, false medical claims, and replay described as live. Fix critical failures before declaring the release candidate.

## Minimal verification today

One full happy-path smoke run, one unhappy-path run, and a clean-checkout reproducibility attempt. Record blockers precisely. Do not launch the full stress matrix yet.

## Exit gate and freeze decision

Tag or commit a feature-complete release candidate. Maintain a ranked blocker list for November 2. After tonight, new features require a clear reason that they improve the judge-facing demo more than they risk destabilizing it. The default is repairs, measurement, video, and submission.
