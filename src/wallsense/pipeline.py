"""Frozen recording split and train-only baseline selection for Wallhack."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

import joblib
import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, f1_score, precision_recall_fscore_support
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .common import ARTIFACTS, DATA, sha256_bytes, sha256_file, write_json
from .wallhack import FEATURE_NAMES, LABELS, WINDOW, load_recording, recordings, window_features

SEED = 20261027
SPLIT_VERSION = "recording-holdout-v2"


def split_for(rec_id: str) -> str:
    scenario, antenna, stem = rec_id.split("/")
    if stem == "b1":
        return {("LOS", "BQ"): "train", ("NLOS", "PIFA"): "train",
                ("LOS", "PIFA"): "validation", ("NLOS", "BQ"): "test"}[(scenario, antenna)]
    suffix = int(stem[-1])
    return "train" if suffix <= 3 else "validation" if suffix == 4 else "test"


def inventory() -> dict:
    files = recordings()
    if len(files) != 44:
        raise RuntimeError(f"expected 44 Wallhack raw CSV recordings, found {len(files)}")
    rows = []
    for item in files:
        with item.path.open("rb") as source:
            count = sum(1 for _ in source) - 1
        rows.append({"recording_id": item.recording_id, "scenario": item.scenario,
                     "antenna": item.antenna, "expected_label": item.expected_label,
                     "split": split_for(item.recording_id), "file_bytes": item.path.stat().st_size,
                     "csv_rows": count})
    by_split = defaultdict(Counter)
    for row in rows:
        by_split[row["split"]][row["expected_label"]] += 1
    value = {"source": "Wallhack1.8k", "version": "1.0.1",
             "url": "https://zenodo.org/records/13950918", "archive_md5": "57a0b9baa3532e1172b25d756536071a",
             "source_license_notice": "non-commercial research use; author permission for hackathon use",
             "split_version": SPLIT_VERSION, "recordings": rows,
             "group_counts": {split: {str(k): v for k, v in counts.items()} for split, counts in by_split.items()}}
    write_json(ARTIFACTS / "wallhack_inventory.json", value)
    return value


def prepare() -> dict:
    source_inventory = inventory()
    ids_by_split = {split: sorted(row["recording_id"] for row in source_inventory["recordings"] if row["split"] == split)
                    for split in ("train", "validation", "test")}
    if len(set(sum(ids_by_split.values(), []))) != 44:
        raise RuntimeError("split groups overlap or are missing")
    split_manifest = {"version": SPLIT_VERSION, "seed": SEED, "group_unit": "raw CSV recording",
                      "protocol_limit": "Recording-safe; may share rooms, users, or devices across groups.",
                      "groups": ids_by_split}
    encoded = json.dumps(split_manifest, sort_keys=True, separators=(",", ":")).encode()
    split_manifest["sha256"] = sha256_bytes(encoded)
    write_json(ARTIFACTS / "wallhack_split.json", split_manifest)
    arrays = {key: [] for key in ("X", "y", "group", "split", "scenario", "antenna", "offset")}
    audit = []
    for item in recordings():
        iq, labels, times, parse_audit = load_recording(item)
        X, y, offsets, mixed = window_features(iq, labels, times)
        for vector, target, offset in zip(X, y, offsets):
            arrays["X"].append(vector)
            arrays["y"].append(target)
            arrays["group"].append(item.recording_id)
            arrays["split"].append(split_for(item.recording_id))
            arrays["scenario"].append(item.scenario)
            arrays["antenna"].append(item.antenna)
            arrays["offset"].append(offset)
        audit.append({"recording_id": item.recording_id, "file_sha256": sha256_file(item.path),
                      "windows": int(len(y)), "mixed_label_windows": mixed, **parse_audit})
    output = {name: np.asarray(values) for name, values in arrays.items()}
    output["feature_names"] = np.asarray(FEATURE_NAMES)
    output["split_hash"] = np.asarray(split_manifest["sha256"])
    ARTIFACTS.mkdir(exist_ok=True)
    np.savez_compressed(ARTIFACTS / "wallhack_features.npz", **output)
    summary = {"split_hash": split_manifest["sha256"], "feature_names": list(FEATURE_NAMES),
               "window_packets": WINDOW, "window_count": len(arrays["y"]),
               "class_counts": {str(k): int(v) for k, v in Counter(arrays["y"]).items()},
               "split_window_counts": {split: int(sum(value == split for value in arrays["split"])) for split in ids_by_split},
               "parse_audit": audit}
    write_json(ARTIFACTS / "wallhack_prepare.json", summary)
    return {key: summary[key] for key in ("split_hash", "window_count", "class_counts", "split_window_counts")}


def _metrics(y: np.ndarray, pred: np.ndarray, labels: list[int]) -> dict:
    precision, recall, f1, support = precision_recall_fscore_support(y, pred, labels=labels, zero_division=0)
    balanced = float(balanced_accuracy_score(y, pred)) if len(set(y)) > 1 else None
    return {"n": int(len(y)), "accuracy": float(accuracy_score(y, pred)),
            "balanced_accuracy": balanced,
            "macro_f1": float(f1_score(y, pred, labels=labels, average="macro", zero_division=0)),
            "confusion_matrix": confusion_matrix(y, pred, labels=labels).tolist(),
            "per_class": {str(label): {"precision": float(p), "recall": float(r), "f1": float(f), "support": int(n)}
                          for label, p, r, f, n in zip(labels, precision, recall, f1, support)}}


def _load_features() -> dict:
    path = ARTIFACTS / "wallhack_features.npz"
    if not path.exists():
        raise FileNotFoundError("run `wallsense wallhack-prepare` first")
    with np.load(path, allow_pickle=False) as data:
        return {key: data[key] for key in data.files}


def train() -> dict:
    data = _load_features()
    X, y, split = data["X"], data["y"], data["split"]
    train_mask, val_mask = split == "train", split == "validation"
    result = {"split_hash": str(data["split_hash"]), "feature_names": list(FEATURE_NAMES), "tasks": {}}
    for task, target, labels in (("activity", y, [0, 1, 2]), ("motion", (y != 0).astype(np.int8), [0, 1])):
        candidates = {
            "dummy": DummyClassifier(strategy="most_frequent"),
            "logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, class_weight="balanced", random_state=SEED)),
            "extra_trees": ExtraTreesClassifier(n_estimators=200, min_samples_leaf=3, class_weight="balanced", random_state=SEED, n_jobs=-1),
        }
        scores = {}
        for name, model in candidates.items():
            model.fit(X[train_mask], target[train_mask])
            pred = model.predict(X[val_mask])
            scores[name] = _metrics(target[val_mask], pred, labels)
            joblib.dump(model, ARTIFACTS / f"wallhack_{task}_{name}.joblib")
        best = max(scores, key=lambda name: (scores[name]["macro_f1"], name))
        result["tasks"][task] = {"selected_model": best, "validation": scores,
                                 "train_groups": len(set(data["group"][train_mask])),
                                 "validation_groups": len(set(data["group"][val_mask]))}
    write_json(ARTIFACTS / "wallhack_selection.json", result)
    return {task: {"selected_model": details["selected_model"],
                   "validation_macro_f1": details["validation"][details["selected_model"]]["macro_f1"]}
            for task, details in result["tasks"].items()}


def evaluate() -> dict:
    data = _load_features()
    selection_path = ARTIFACTS / "wallhack_selection.json"
    if not selection_path.exists():
        raise FileNotFoundError("run `wallsense wallhack-train` first")
    selection = json.loads(selection_path.read_text())
    if selection["split_hash"] != str(data["split_hash"]):
        raise RuntimeError("model-selection split hash differs from feature cache")
    X, y, split = data["X"], data["y"], data["split"]
    test_mask = split == "test"
    result = {"source": "Wallhack1.8k", "version": "1.0.1", "split_hash": selection["split_hash"],
              "split_unit": "raw CSV recording", "claim_scope": "held-out recordings from represented capture setups",
              "test_groups": len(set(data["group"][test_mask])), "tasks": {}}
    for task, target, labels in (("activity", y, [0, 1, 2]), ("motion", (y != 0).astype(np.int8), [0, 1])):
        name = selection["tasks"][task]["selected_model"]
        model_path = ARTIFACTS / f"wallhack_{task}_{name}.joblib"
        model = joblib.load(model_path)
        predictions = model.predict(X[test_mask])
        domains = {}
        for scenario in ("LOS", "NLOS"):
            for antenna in ("BQ", "PIFA"):
                mask = test_mask & (data["scenario"] == scenario) & (data["antenna"] == antenna)
                if mask.sum():
                    domains[f"{scenario}/{antenna}"] = _metrics(target[mask], model.predict(X[mask]), labels)
        result["tasks"][task] = {"model": name, "model_sha256": sha256_file(model_path),
                                  "overall": _metrics(target[test_mask], predictions, labels), "domains": domains,
                                  "limitations": ["No validation for still-person presence, falls, or vitals.",
                                                  "Recording-level split may share people, rooms, or devices."]}
    write_json(ARTIFACTS / "wallhack_test_metrics.json", result)
    return {task: {"model": details["model"], "test_n": details["overall"]["n"],
                   "test_macro_f1": details["overall"]["macro_f1"]}
            for task, details in result["tasks"].items()}
