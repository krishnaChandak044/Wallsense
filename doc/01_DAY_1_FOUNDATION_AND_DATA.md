# Day 1 — Tuesday, October 27: foundation and data contract

## Goal

End the day with a new event-period repository that can inspect **both** real datasets, reject malformed input, identify recording/session groups, and write a frozen split proposal. Do not spend the day on UI polish.

## Work blocks

### 1. Create the clean project

- Initialize Git here after kickoff; add backend, frontend, scripts, tests, docs, `data/` and `artifacts/` policies.
- Add `.gitignore` for all raw archives/extractions, checkpoints if redistribution is uncertain, `.env`, API keys, local databases, caches, and exported private event traces.
- Add a concise root README with truthful mode: recorded CSI replay, no hardware connected, two source-specific tasks.
- Record Python/Node versions and use lockfiles. Make a one-command backend start and frontend start target, even if each initially returns a skeleton.
- Add `doc/DECISIONS.md` and `doc/WORK_LOG.md`; identify the older dossier/prototype as pre-event references and log newly written code.

### 2. Secure data and provenance

- **Wallhack1.8k:** pin the Zenodo record/version and archive hash; reuse the already downloaded local copy only after verifying structure/hash against source metadata. Keep 44 raw recording CSVs and source spectrograms ignored. Record authors and citation.
- **CSI-Bench:** pin official repository commit and Kaggle dataset version/metadata. Capture the mentor's permission statement in a private evidence note; write a public short statement that permission for hackathon use was reported, without publishing private contact details. Verify exact rights for public redistribution and model weights separately. Download into ignored `data/` only.
- Save a machine-readable manifest: source URL, download date, checksum, file count, intended task, license/permission note, dataset version, and local path. A manifest must never contain a credential.
- Inventory each source: number of recordings/sessions, capture conditions, antenna/device, labels, subject/session IDs, sample lengths, missing/corrupt rows, and whether NLOS is documented. Do not infer metadata from filenames without recording that assumption.

### 3. Write two independent parsers

- Wallhack CSV adapter: validate required columns, parse 256 interleaved I/Q values per packet, preserve timestamps/packet IDs, class labels, LOS/NLOS, antenna, and source recording ID. Count malformed rows rather than silently dropping them. Confirm class mapping from original dataset documentation.
- CSI-Bench adapter: inspect actual archive and official metadata **before** coding assumptions. Read task-specific HDF5/array shapes and label mappings for FallDetection; inspect BreathingDetection separately. Decode into a canonical window object with explicit source, capture schema, task, label, subject/session/environment ID if supplied, and sampling metadata. Fail clearly if mandatory fields are missing.
- Canonical object: `source_id`, `recording_id`, `session_or_subject_group`, `task`, `capture_condition`, `start/end`, `complex_csi`, `label_if_allowed`, `integrity_flags`, `provenance_hash`.
- Never use ground truth labels in the feature vector or replay inference path. Challenge label access will be a separate protected store.

### 4. Split feasibility before model fitting

- Print a table of group count × class × LOS/NLOS × antenna for Wallhack; group by raw recording for the headline split.
- For CSI-Bench, determine whether subject, session, or environment groups exist. Prefer held-out subject/session, and state exactly which one is feasible. If group metadata is absent, do not advertise a generalization claim.
- Freeze a candidate test manifest and hash it. Reserve validation groups separately. Make test group IDs invisible to fitting and tuning scripts.
- Check whether each split contains all target classes. If impossible, document the limitation and choose a protocol that exposes it; never quietly move windows from one recording across partitions.

## Minimal verification today

Parser fixtures for valid, malformed, truncated, non-finite, and wrong-shape input; an assertion that group IDs do not overlap; a real-data dry run showing file counts and exclusions. These are quick checks, not the heavy test campaign.

## Output artifacts

`dataset_manifest.json`, inventory tables, parser/schema docs, frozen split JSON + SHA-256, a tiny synthetic parser fixture, and first setup commands. Raw CSI stays local.

## Exit gate

Both sources are inspectable; Wallhack parser works on actual files; CSI-Bench task shapes and label meanings are known; no raw dataset appears in `git status`; and the frozen split design is explicit. If CSI-Bench access/metadata blocks progress, log it immediately and preserve the Wallhack critical path.
