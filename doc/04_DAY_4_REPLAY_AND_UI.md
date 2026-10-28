# Day 4 — Friday, October 30: end-to-end replay and operator experience

## Goal

A person unfamiliar with the project can choose a real recording, press Play, inspect an event, and export a truthful report. The interface serves investigation, not a wall of charts.

## Backend API

- FastAPI endpoints: `GET /health`, `GET /sources`, `GET /recordings`, `GET /recordings/{id}`, `POST /sessions`, `GET /sessions/{id}/events`, `GET /events/{id}`, `GET /sessions/{id}/report`, plus a versioned WebSocket `/sessions/{id}/replay`.
- Use server-generated opaque IDs from a whitelisted catalog. Never accept arbitrary local paths, SQL fragments, or raw archive URLs from the client.
- Replay messages carry monotonic sequence number, recording/window ID, capture-relative timestamp, replay speed, source/task, quality state, prediction, score/uncertainty, and feature plot payload. Replay must visibly say **RECORDED CSI**.
- Support play/pause, speed, scrub or seek, and restart without double-counting events. Define what seeking does to event state. Handle disconnect/reconnect and stale sessions.
- Generate JSON and printable HTML reports from the stored ledger. Report and UI must agree because they read the same event records.
- Preserve strict model compatibility: each source adapter selects only models registered for its schema and task.

## Frontend experience

1. **Source picker:** Wallhack NLOS/LOS motion or CSI-Bench fall research session, each with dataset/capture badge and supported capabilities. Ground-truth label is hidden in Challenge Mode.
2. **Investigation workspace:** one strong central signal view, synchronized timeline, current decision, quality reason, and event list. Provide a small legend for measured signal fact versus model inference.
3. **Event inspection:** click an event to see window/time range, evidence features, quality, model/version, evaluation scope, and a “why this may be wrong” note. SensorGPT opens from this context on Day 5.
4. **Report:** four capability rows, each with status and provenance. Fall on Wallhack and motion on incompatible CSI-Bench recordings are unavailable rather than fabricated.
5. **Evaluation:** real result files with counts, per-domain metrics, group split description, and selected mistakes. Never hard-code attractive percentages into the UI.

Use responsive React/Vite or equivalent polished app. Accessible labels, keyboard controls, adequate contrast, and legible demo typography matter more than animation. No Streamlit. Avoid a generic analytics dashboard as the primary screen.

## Demo-ready interaction by tonight

- Load one Wallhack NLOS recording and one CSI-Bench fall recording if fall was promoted.
- Show actual replay frames and event evidence, not synthetic sensor animation.
- Select an uncertain or mistaken case so limitations are visible.
- Export one report and verify its row states match the chosen recording.

## Minimal verification today

Two end-to-end manual replays, one API schema check, one reconnect/seek check, and one report consistency assertion. Save screenshots for critique. Heavy browser/system testing waits until Nov 2.

## Exit gate

A complete offline-capable sensing and replay demo works without Meta credentials. The UI shows the recording source and scope on every important screen. No report combines measurements from unrelated datasets into one person’s story.
