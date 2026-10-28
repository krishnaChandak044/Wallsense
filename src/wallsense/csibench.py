"""Metadata contract for the separate CSI-Bench task; no cross-dataset mixing."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pandas as pd

from .common import DATA

TASKS = {"FallDetection", "BreathingDetection"}


def inspect_task(root: Path | None = None, task: str = "FallDetection") -> dict:
    if task not in TASKS:
        raise ValueError(f"unsupported CSI-Bench task: {task}")
    root = root or DATA / "csi-bench"
    task_root = root / task
    metadata_path = task_root / "metadata" / "sample_metadata.csv"
    mapping_path = task_root / "metadata" / "label_mapping.json"
    if not metadata_path.is_file() or not mapping_path.is_file():
        raise FileNotFoundError(
            f"CSI-Bench v12 {task} metadata is missing under {task_root}; "
            "download the task from Kaggle before training or claiming results"
        )
    frame = pd.read_csv(metadata_path)
    mandatory = {"file_path", "label"}
    if not mandatory.issubset(frame.columns):
        raise ValueError(f"{task}: metadata missing {mandatory - set(frame.columns)}")
    id_column = "id" if "id" in frame else "sample_id" if "sample_id" in frame else None
    if id_column is None or frame[id_column].isna().any() or frame[id_column].duplicated().any():
        raise ValueError(f"{task}: sample IDs missing or duplicated")
    mapping = json.loads(mapping_path.read_text())
    split_ids = {}
    for split in ("train_id", "val_id", "test_id"):
        path = task_root / "splits" / f"{split}.json"
        if not path.is_file():
            raise FileNotFoundError(f"{task}: missing official split {path}")
        values = json.loads(path.read_text())
        if not isinstance(values, list):
            raise ValueError(f"{task}: {split} is not a JSON list")
        split_ids[split] = {str(value) for value in values}
    pairs = (("train_id", "val_id"), ("train_id", "test_id"), ("val_id", "test_id"))
    for left, right in pairs:
        if split_ids[left] & split_ids[right]:
            raise ValueError(f"{task}: overlapping official sample IDs: {left}/{right}")
    known_ids = set(frame[id_column].astype(str))
    missing_ids = {key: len(ids - known_ids) for key, ids in split_ids.items()}
    if any(missing_ids.values()):
        raise ValueError(f"{task}: split IDs absent from metadata: {missing_ids}")
    # Split IDs are sample-safe; subject/session overlap must be audited separately.
    group_columns = [col for col in frame if any(word in col.lower() for word in ("user", "subject", "session", "env", "device"))]
    groups = {column: int(frame[column].nunique(dropna=False)) for column in group_columns}
    framed = {name: frame[frame[id_column].astype(str).isin(ids)] for name, ids in split_ids.items()}
    overlap = {}
    for column in ("user", "session", "environment", "device"):
        if column not in frame:
            continue
        overlap[column] = {}
        for left, right in pairs:
            overlap[column][f"{left}/{right}"] = len(set(framed[left][column].astype(str)) & set(framed[right][column].astype(str)))
    label_counts = {str(key): int(value) for key, value in Counter(frame["label"].astype(str)).items()}
    paths = frame["file_path"].astype(str)
    unsafe = sum(Path(path).is_absolute() or ".." in Path(path).parts for path in paths)
    if unsafe:
        raise ValueError(f"{task}: {unsafe} unsafe file paths in metadata")
    return {
        "source": "CSI-Bench", "version": 12, "task": task,
        "dataset_url": "https://www.kaggle.com/datasets/guozhenjennzhu/csi-bench",
        "source_code_url": "https://github.com/guozhen-jenn-zhu/CSI-Bench-Real-WiFi-Sensing-Benchmark",
        "source_code_commit_inspected": "b1beac7b0fa46e01748901195ecfbe309dfc0180",
        "dataset_license_notice": "Kaggle lists CC BY-NC-ND 4.0; user reports mentor approval for hackathon use. Raw files stay local.",
        "metadata_rows": int(len(frame)), "label_mapping": mapping,
        "label_counts": label_counts, "group_columns": groups,
        "official_split_group_overlap": overlap,
        "official_split_counts": {key: len(value) for key, value in split_ids.items()},
        "split_warning": "Official sample IDs are disjoint; verify subject/session overlap before claiming held-out generalization.",
        "h5_files_present": sum(1 for _ in task_root.rglob("*.h5")),
    }
