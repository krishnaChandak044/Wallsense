# WallSense

Event-period implementation for the Meta Global AI Developer Hackathon. This stage covers the Day 1–2 foundation: a verified Wallhack1.8k CSV adapter, recording-safe split, reproducible feature baseline, and CSI-Bench metadata adapter. The older `meta_hack` app and planning dossier are references only; their code and model artifacts are not submitted here.

WallSense currently analyzes **recorded** Wi-Fi CSI. It does not capture live signals or report medical vitals. Wallhack labels are no presence, walking, and walking plus arm waving. A no-presence dataset label does not prove a motionless person is absent. CSI-Bench is a separate source/task with separate models.

## Day 1–2 setup

```bash
uv sync --extra test
mkdir -p data
ln -s /path/to/wallhack1.8k data/wallhack1.8k
uv run wallsense wallhack-inventory
uv run wallsense wallhack-prepare
uv run wallsense wallhack-train
uv run wallsense wallhack-evaluate
```

The symlink points to a local copy and is ignored by Git. Download [Wallhack1.8k 1.0.1](https://zenodo.org/records/13950918), verify the published MD5 `57a0b9baa3532e1172b25d756536071a`, and extract under `data/wallhack1.8k/`; or point the symlink at that directory. Raw recordings are not redistributed. A newer Zenodo version needs a separate manifest before use.

For CSI-Bench, the metadata and official split files can be fetched individually from [Kaggle version 12](https://www.kaggle.com/datasets/guozhenjennzhu/csi-bench). The full release is about 81 GB. A bounded, deterministic FallDetection pilot is fetched without the full release:

```bash
uvx kaggle datasets download guozhenjennzhu/csi-bench/12 -f FallDetection/metadata/label_mapping.json -p data/csi-bench --unzip
uvx kaggle datasets download guozhenjennzhu/csi-bench/12 -f FallDetection/metadata/sample_metadata.csv -p data/csi-bench --unzip
uvx kaggle datasets download guozhenjennzhu/csi-bench/12 -f FallDetection/splits/train_id.json -p data/csi-bench --unzip
uvx kaggle datasets download guozhenjennzhu/csi-bench/12 -f FallDetection/splits/val_id.json -p data/csi-bench --unzip
uvx kaggle datasets download guozhenjennzhu/csi-bench/12 -f FallDetection/splits/test_id.json -p data/csi-bench --unzip
uv run wallsense csi-inventory
uv run python scripts/fetch_csibench_pilot.py --per-user-class 35 --workers 4
uv run wallsense csi-prepare
uv run wallsense csi-train
uv run wallsense csi-evaluate
```

The CSI-Bench result is explicitly a bounded, incomplete user-disjoint pilot, not the official full benchmark. The current pilot retained 725 of 1,040 selected files after retrieval, so its metrics are preliminary and must not be presented as generalization or through-wall proof. Day 1–2 metrics and caveats are recorded in `doc/02_DAY_2_BASELINES.md`.

Generated manifests, feature caches, model files, and metrics live under ignored `artifacts/`. The exact split IDs and aggregate metrics can be copied to reviewed reports before public submission. The API credit policy is in [the spend plan](doc/09_CREDITS_AND_SPEND_PLAN.md). See [Day 1](doc/01_DAY_1_FOUNDATION_AND_DATA.md), [Day 2](doc/02_DAY_2_BASELINES.md), and [claims and rights](doc/08_DATA_RIGHTS_AND_CLAIMS.md).

## Commands

`wallhack-inventory` scans recordings. `wallhack-prepare` parses real I/Q packets, extracts non-overlapping windows, and freezes a recording-level split. `wallhack-train` fits train-only preprocessing and baselines. `wallhack-evaluate` reports held-out metrics and domain breakdown. `csi-inventory` validates CSI-Bench metadata and split files if downloaded; it never pretends to train without data. Run quick checks with `uv run pytest -q`.
