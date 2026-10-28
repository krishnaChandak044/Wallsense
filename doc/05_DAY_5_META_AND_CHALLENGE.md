# Day 5 — Saturday, October 31: Meta agent and blind challenge

## Goal

Meta AI becomes a useful part of the product: it investigates a particular sensing decision by calling evidence tools. The blind challenge lets a judge test the system instead of trusting a curated clip.

## Meta Model API integration

- Check current official API docs/model/tool-calling interface before implementation. Keep key and any billing token only in server environment variables. Make one tiny smoke call, then record model ID, response mode, latency, and estimated cost. Check that credits are applied and that a payment method is configured if the account requires one.
- Define typed, read-only tool schemas for event, signal summary, quality, model decision, evaluation scope, and a comparison/counterexample. Tool output contains IDs, units, source, window range, and uncertainty. It never contains hidden challenge truth or raw CSI by default.
- Implement a bounded multi-turn tool loop with call limit, timeout, payload limit, strict JSON validation, and clear error states. Prevent a model response from inventing event IDs or metric values by server-side citation checking.
- Stream tool progress and the final answer to the UI. The judge should see “Meta is checking event E17, quality window W204, and NLOS evaluation” rather than just receive a paragraph.
- Agent instructions require: distinguish measured signal from classifier inference; state dataset and capture scope; say when the question is unsupported; avoid identity, intent, exact coordinates, medical advice, and numerical vital claims without evidence.
- Build conversations that materially use tools: “Why did this alert?”, “What evidence makes this uncertain?”, “Could it be a fall behind a wall?”, and “Compare this with another event.” The last question should explain that fall evidence on CSI-Bench cannot be projected onto a Wallhack recording.
- On API outage, the agent panel explicitly says unavailable while replay, model, and report keep working. Do not quietly switch to a local canned answer while labeling it Meta.

## Blind Challenge Mode

- Reserve held-out recording IDs from Day 1 manifests. Display opaque choices without class labels or result-bearing filenames.
- Challenge API creates a session with no access to ground truth in the normal recording/event/agent tool layer. The server writes predictions, quality decisions, event list, model hash, and split hash to a ledger; hash and freeze it before reveal is enabled.
- Reveal endpoint returns actual label/event truth and computes result from the frozen ledger. It must show mistakes, abstentions, and capture conditions, not only a success badge.
- At least one NLOS Wallhack challenge and, if valid, one separate CSI-Bench fall challenge. The two are separate recordings and separate tasks. Do not pre-select only favorable examples; include a difficult case.
- Demo screen makes it obvious that prediction occurred before truth was shown. A judge should be able to choose and rerun a challenge without changing model weights.

## Agent and challenge verification today

Manually inspect three real Meta conversations and the tool trajectory. Test a request for heart rate, a prompt-injection string inside user text, a hidden-label request, and a nonexistent event ID. Direct API calls must not expose truth before reveal. Verify that the ledger hash stays fixed after reveal.

## Exit gate

At least three useful Meta-powered investigations with valid evidence IDs; no invented numbers in reviewed answers; judge-selectable challenge freezes before reveal; and billing spend is logged. If tool-calling cannot be verified today, prioritize repairing it over optional features.
