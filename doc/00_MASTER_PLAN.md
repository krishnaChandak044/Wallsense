# Six-day master build plan

**Version:** 1.0 — October 27, 2026
**Build window:** October 27–November 1 (IST calendar days)
**Hardening and submission:** November 2–4 ET; final deadline November 4, 9:00 PM ET = November 5, 7:30 AM IST, subject to official updates. Submit before the final hour.

## 1. The product we will actually ship

A judge opens WallSense, selects an approved recorded CSI session, and runs a replay. The app shows the signal, a source-specific inference, confidence/quality, and a timeline of evidence-backed events. The judge opens an event and asks SensorGPT why it occurred or whether a competing explanation is plausible. SensorGPT uses Meta Model API to call read-only evidence tools, cites actual event/window IDs, and can say “unknown.” The judge can run a sealed recording in Challenge Mode, freeze predictions, then reveal labels and errors. A report and evaluation page use the same stored event ledger and metrics file as the UI.

**Two distinct replay lanes:**

1. **Wallhack1.8k / motion lane:** no-presence, walking, and walking-plus-arm-movement on the captured LOS/NLOS setups. This is the main through-wall research story. “No motion detected” is not proof that nobody is present.
2. **CSI-Bench / fall lane:** fall-related classification only after its file schema, label meaning, and group-safe holdout are established. Its result is explicitly tied to CSI-Bench capture conditions. If the dataset has no documented NLOS fall test, the product does not claim through-wall fall detection. Breathing detection is a separate task only if its labels are valid; numerical respiratory or heart rates require paired reference measurements and are not assumed.

The lanes share event, report, and agent interfaces, but have separate parsers, models, preprocessing, splits, metrics, and model cards. The UI never presents Wallhack motion and CSI-Bench fall as simultaneous measurements of one person.

## 2. Judge-facing differentiation

The orientation gives 30% to impact, 25% to Meta AI use, 20% to technical depth, and 25% to demo. Build for those four tests:

| Rubric | Visible proof |
| --- | --- |
| Impact | Camera-free investigation in settings where video is undesirable; clear limits prevent unsafe overconfidence. |
| Meta AI | SensorGPT executes real evidence tools over events, quality, model decision, evaluation scope, and counterfactual questions. Meta changes the investigation, not merely the prose. |
| Technical depth | Real CSI parsing, source-specific models, recording/subject-safe splits, uncertainty gate, event aggregation, provenance, and blind challenge. |
| Demo | A judge-selectable recording, synchronous replay, agent tool trace, frozen prediction, reveal, and report in about three minutes. |

The orientation explicitly discourages a dashboard as the main feature, basic RAG, Streamlit, and AI-generated medical advice. WallSense is an interactive investigation workflow. Its visual console serves the decision and challenge; it does not constitute the product alone. No medical advice, diagnosis, or emergency response copy appears.

## 3. Proposed implementation architecture

```text
Ignored local data/ (Wallhack, CSI-Bench)
    -> source-specific parser + provenance validator
    -> deterministic windows + quality measurements
    -> source-specific model + calibrated/explicit uncertainty
    -> event builder + append-only evidence ledger (SQLite/JSON)
    -> FastAPI: sessions, replay WebSocket, evidence tools, report, challenge
    -> React/Vite operator app: replay, event investigation, challenge, evaluation
    -> server-side Meta Model API agent: bounded tool calls over derived evidence
```

Suggested repository layout after build begins:

```text
wallsense/
  README.md  pyproject.toml  .gitignore  .env.example
  doc/        data/ (ignored)   artifacts/ (model and evaluation policy)
  backend/wallsense/{data,features,models,quality,events,agent,api,challenge}/
  frontend/src/{pages,components,lib}/
  scripts/{inspect_data,prepare,train,evaluate,run_demo}.py
  tests/       reports/ (generated aggregates only)
```

The API key stays on the server. The agent receives compact, derived evidence, not raw CSI or hidden challenge labels. When billing, credentials, or Meta service is unavailable, sensing and replay still work and the agent clearly shows “unavailable.” No response may be labeled Meta-powered unless it was actually returned by Meta.

## 4. Build order and dependency graph

```text
Dataset rights and inventory
  -> parsers + window schema -> frozen group split
  -> model baselines + quality/abstention
  -> event ledger + replay API -> UI
  -> Meta tool agent + challenge -> integrated release candidate
  -> heavy testing -> video -> public submission
```

The Wallhack lane and CSI-Bench feasibility work start together on Day 1. The fall lane must not block the complete motion lane. By Day 3, either a valid fall data contract exists or the UI says fall is unavailable from the selected recording. This is a release gate, not a promise to invent a result.

## 5. Daily outputs and commits

| Day | Date | End-of-day outcome | Suggested commit |
| --- | --- | --- | --- |
| 1 | Oct 27 | New repo, rights/provenance, both dataset inventories, valid parsers, frozen group split design | `01-foundation-data-contract` |
| 2 | Oct 28 | Reproducible Wallhack baseline; CSI-Bench fall feasibility and first honest baseline | `02-reproducible-baselines` |
| 3 | Oct 29 | Quality and uncertainty, event ledger, error breakdown; fall lane promoted only on evidence | `03-quality-events` |
| 4 | Oct 30 | End-to-end replay API, report, and core operator UI from actual outputs | `04-replay-investigation` |
| 5 | Oct 31 | Real Meta tool-calling agent, challenge sealing/reveal, integrated stories for both lanes | `05-meta-agent-challenge` |
| 6 | Nov 1 | Feature-complete release candidate, polished demo path, docs and reproducibility | `06-release-candidate` |

Commits are made after a coherent slice works. Do not bundle licensed recordings, secrets, stale pre-event binaries, or unverified metrics. Record exact test command and result in each commit or PR note. The public repository must show new event-period work and attribution for reused ideas/packages.

## 6. Non-negotiable acceptance conditions

1. A clean checkout can install dependencies and reach a useful demo with documented dataset access and credentials.
2. Every reported metric is generated by code on a named frozen split with sample and group counts. A recording never appears on both sides of the headline train/test split.
3. Every on-screen alert identifies source dataset, recording/window, task/model version, quality decision, and evidence.
4. Challenge truth is inaccessible before the prediction ledger is frozen. The reveal explains mistakes as well as successes.
5. SensorGPT performs actual Meta API calls and read-only tool calls in at least three meaningful conversations. All factual claims link to tool evidence; unsupported claims are caught or softened.
6. A three-minute screen recording can show a complete real replay, agent investigation, challenge reveal, and report without staged labels or synthetic signals masquerading as real.
7. Fall/health wording is dataset-specific. No heart-rate number is produced without paired reference data and independent evaluation.

## 7. Scope discipline and decisions

**Required:** motion lane, honest fall lane if data gate passes, provenance, model evaluation, uncertainty, replay, events, Meta agent, challenge, report, strong demo.
**Only if time remains:** breathing classification, floor-plan metadata view, activity memory, corruption robustness chart, federated experiment.
**Outside this submission:** unsupported live sensing, precise location, people counting, numerical heart rate, clinical monitoring, emergency alerts, a 14-day baseline without 14 days of data.

If a channel fails its data or performance gate, its unavailable state is a valid product outcome. The strongest entry is one judges can interrogate and still trust. No plan can guarantee a prize, so effort goes to measured capability and a reliable demo.

## 8. Evidence and spending ledger

Create `doc/DECISIONS.md` when implementation starts. For each experiment log date, hypothesis, dataset version, split, command, result, cost, decision, and unresolved risk. Track Meta API spending from the billing page after smoke test and evaluation batches; the “spend limit” mentioned in the hackathon mail is a notification, so do not treat it as a hard cap. Use small prompts and derived evidence. Do not waste API credit training local CSI models.
