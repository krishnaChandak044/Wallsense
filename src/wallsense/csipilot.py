"""CSI-Bench FallDetection v12 user-held-out pilot subset baseline.

This intentionally uses only the bounded subset in the local manifest. It is
not an official full-benchmark result and makes no NLOS or clinical claim.
"""

from __future__ import annotations

import json
from collections import Counter

import h5py
import joblib
import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .common import ARTIFACTS, DATA, sha256_bytes, sha256_file, write_json
from .pipeline import SEED, _metrics

NAMES = tuple(f"{name}_{quantile}" for name in
              ("relative_std", "relative_velocity", "relative_range", "low_power", "mid_power", "high_power")
              for quantile in ("q10", "q50", "q90")) + ("mean_trace_std", "mean_trace_velocity")


def read_h5(path) -> np.ndarray:
    with h5py.File(path, "r") as source:
        if "CSI_amps" not in source:
            raise ValueError(f"{path.name}: missing CSI_amps")
        raw = source["CSI_amps"][:]
    if raw.ndim != 3 or raw.shape[2] != 1 or raw.shape[0] < 16 or raw.shape[1] < 100:
        raise ValueError(f"{path.name}: unsupported CSI_amps shape {raw.shape}")
    if not np.isfinite(raw).all():
        raise ValueError(f"{path.name}: non-finite CSI_amps")
    return raw[:, :, 0].T.astype(np.float32)  # source: features × time × 1; canonical: time × features


def extract_features(signal: np.ndarray) -> np.ndarray:
    if signal.ndim != 2 or signal.shape[0] < 100 or signal.shape[1] < 16:
        raise ValueError("CSI-Bench signal must be time × channels")
    baseline = np.maximum(np.median(np.abs(signal), axis=0, keepdims=True), 1e-3)
    relative = np.clip(signal / baseline, -50, 50)
    centered = relative - relative.mean(axis=0, keepdims=True)
    spectrum = np.abs(np.fft.rfft(centered, axis=0)) ** 2
    bins = np.fft.rfftfreq(len(signal))
    total = spectrum.sum(axis=0) + 1e-9
    columns = [np.std(relative, axis=0), np.mean(np.abs(np.diff(relative, axis=0)), axis=0),
               np.quantile(relative, .95, axis=0) - np.quantile(relative, .05, axis=0)]
    for lo, hi in ((.002, .02), (.02, .1), (.1, .5)):
        columns.append(spectrum[(bins >= lo) & (bins < hi)].sum(axis=0) / total)
    result = np.concatenate([np.quantile(column, [.1, .5, .9]) for column in columns] + [
        np.array([np.std(relative.mean(axis=1)), np.mean(np.abs(np.diff(relative.mean(axis=1))))])
    ]).astype(np.float32)
    if result.shape != (len(NAMES),) or not np.isfinite(result).all():
        raise ValueError("invalid CSI-Bench feature vector")
    return result


def prepare() -> dict:
    path = ARTIFACTS / "csibench_pilot_manifest.json"
    if not path.is_file():
        raise FileNotFoundError("run scripts/fetch_csibench_pilot.py first")
    manifest = json.loads(path.read_text())
    samples = manifest["samples"]
    if manifest.get("version") != 12 or manifest.get("task") != "FallDetection":
        raise ValueError("unexpected CSI-Bench pilot manifest")
    users = {part: {row["user"] for row in samples if row["split"] == part} for part in ("train", "validation", "test")}
    if users["train"] & users["validation"] or users["train"] & users["test"] or users["validation"] & users["test"]:
        raise ValueError("user overlap across CSI-Bench pilot splits")
    X, y, splits, ids, user_ids, devices, environments = [], [], [], [], [], [], []
    for row in samples:
        file_path = DATA / "csi-bench" / row["file"]
        if not file_path.is_file():
            raise FileNotFoundError(f"missing CSI-Bench pilot file: {row['file']}")
        X.append(extract_features(read_h5(file_path)))
        y.append(int(row["label"] == "Fall"))
        splits.append(row["split"])
        ids.append(row["id"])
        user_ids.append(row["user"])
        devices.append(row["device"])
        environments.append(row["environment"])
    split_payload = {"task": manifest["task"], "version": manifest["version"], "selection_seed": manifest["selection_seed"],
                     "group_unit": "user", "groups": {name: sorted(group) for name, group in users.items()},
                     "sample_ids": {name: sorted(row["id"] for row in samples if row["split"] == name) for name in users}}
    split_hash = sha256_bytes(json.dumps(split_payload, sort_keys=True, separators=(",", ":")).encode())
    output = {"X": np.asarray(X, dtype=np.float32), "y": np.asarray(y, dtype=np.int8),
              "split": np.asarray(splits), "id": np.asarray(ids), "user": np.asarray(user_ids),
              "device": np.asarray(devices), "environment": np.asarray(environments),
              "feature_names": np.asarray(NAMES), "split_hash": np.asarray(split_hash)}
    np.savez_compressed(ARTIFACTS / "csibench_pilot_features.npz", **output)
    write_json(ARTIFACTS / "csibench_pilot_split.json", {**split_payload, "sha256": split_hash})
    summary = {"scope": "bounded user-held-out pilot subset", "n": len(y),
               "labels": dict(Counter("Fall" if item else "Nonfall" for item in y)),
               "splits": {name: int(sum(item == name for item in splits)) for name in users}, "split_hash": split_hash}
    write_json(ARTIFACTS / "csibench_pilot_prepare.json", summary)
    return summary


def _load() -> dict:
    path = ARTIFACTS / "csibench_pilot_features.npz"
    if not path.is_file():
        raise FileNotFoundError("run `wallsense csi-prepare` first")
    with np.load(path, allow_pickle=False) as source:
        return {key: source[key] for key in source.files}


def train() -> dict:
    data = _load()
    X, y, split = data["X"], data["y"], data["split"]
    train_mask, val_mask = split == "train", split == "validation"
    if set(y[train_mask]) != {0, 1} or set(y[val_mask]) != {0, 1}:
        raise ValueError("both classes required in train and validation")
    candidates = {"dummy": DummyClassifier(strategy="most_frequent"),
                  "logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, class_weight="balanced", random_state=SEED)),
                  "extra_trees": ExtraTreesClassifier(n_estimators=200, min_samples_leaf=3, class_weight="balanced", random_state=SEED, n_jobs=-1)}
    scores = {}
    for name, model in candidates.items():
        model.fit(X[train_mask], y[train_mask])
        scores[name] = _metrics(y[val_mask], model.predict(X[val_mask]), [0, 1])
        joblib.dump(model, ARTIFACTS / f"csibench_fall_{name}.joblib")
    best = max(scores, key=lambda name: (scores[name]["macro_f1"], name))
    result = {"scope": "bounded user-held-out pilot subset", "split_hash": str(data["split_hash"]),
              "selected_model": best, "validation": scores,
              "train_users": sorted(set(data["user"][train_mask])),
              "validation_users": sorted(set(data["user"][val_mask]))}
    write_json(ARTIFACTS / "csibench_fall_selection.json", result)
    return {"selected_model": best, "validation_macro_f1": scores[best]["macro_f1"]}


def evaluate() -> dict:
    data = _load()
    selection = json.loads((ARTIFACTS / "csibench_fall_selection.json").read_text())
    if selection["split_hash"] != str(data["split_hash"]):
        raise RuntimeError("CSI-Bench model and split hash mismatch")
    model_path = ARTIFACTS / f"csibench_fall_{selection['selected_model']}.joblib"
    model = joblib.load(model_path)
    mask = data["split"] == "test"
    pred = model.predict(data["X"][mask])
    result = {"source": "CSI-Bench", "version": 12, "task": "FallDetection",
              "scope": "bounded user-held-out pilot subset, not full dataset or official benchmark",
              "split_hash": selection["split_hash"], "split_unit": "user",
              "test_users": sorted(set(data["user"][mask])), "model": selection["selected_model"],
              "model_sha256": sha256_file(model_path), "overall": _metrics(data["y"][mask], pred, [0, 1]),
              "label_mapping": {"0": "Nonfall", "1": "Fall"},
              "limitations": ["Capture conditions do not establish through-wall fall detection.",
                              "Clip classification is not event-level fall detection.",
                              "This is a selected subset of Kaggle version 12, not the full CSI-Bench result."]}
    write_json(ARTIFACTS / "csibench_fall_test_metrics.json", result)
    return {"test_n": result["overall"]["n"], "test_macro_f1": result["overall"]["macro_f1"], "test_users": result["test_users"]}
