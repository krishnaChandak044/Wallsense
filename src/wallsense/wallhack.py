"""Wallhack1.8k raw-packet contract and feature extraction.

The published data field interleaves imaginary and real values. Amplitude is
order independent; phase respects that convention. No label is in features.
Each source CSV is a split group.
"""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .common import DATA

LABELS = {0: "no_presence", 1: "walking", 2: "walking_arm_waving"}
VALID_BINS = np.r_[6:32, 33:59]
WINDOW = 400
BANDS = ((.25, 1), (1, 3), (3, 8), (8, 20), (20, 50))
FEATURE_NAMES = tuple(
    f"{name}_{bin_id}" for name in
    ("relative_std", "relative_velocity", "relative_range", "phase_velocity", "phase_step_concentration")
    for bin_id in range(52)
) + tuple(f"band_{lo:g}_{hi:g}_{bin_id}" for lo, hi in BANDS for bin_id in range(52)) + (
    "amplitude_mean", "amplitude_std", "trace_variance", "packet_gap_fraction"
)


@dataclass(frozen=True)
class Recording:
    path: Path
    recording_id: str
    scenario: str
    antenna: str
    expected_label: int


def recordings(root: Path | None = None) -> list[Recording]:
    root = root or DATA / "wallhack1.8k"
    result = []
    for path in sorted(root.glob("*/*/*.csv")):
        scenario, antenna = path.parts[-3:-1]
        if scenario not in {"LOS", "NLOS"} or antenna not in {"BQ", "PIFA"}:
            continue
        stem = path.stem
        label = 0 if stem.startswith("b") else 2 if stem.startswith("ww") else 1 if stem.startswith("w") else None
        if label is None:
            continue
        result.append(Recording(path, f"{scenario}/{antenna}/{stem}", scenario, antenna, label))
    return result


def parse_iq(raw: str) -> np.ndarray:
    text = raw.strip()
    if not (text.startswith("[") and text.endswith("]")):
        raise ValueError("CSI field must be a bracketed numeric vector")
    values = np.fromstring(text[1:-1], sep=",", dtype=np.float32)
    if values.size != 256 or not np.isfinite(values).all():
        raise ValueError(f"expected 256 finite I/Q values, found {values.size}")
    return values.reshape(128, 2)


def load_recording(recording: Recording) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    samples: list[np.ndarray] = []
    labels: list[int] = []
    timestamps: list[int] = []
    rejected = Counter()
    with recording.path.open(newline="") as source:
        reader = csv.DictReader(source)
        required = {"data", "class", "local_timestamp"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"{recording.recording_id}: missing {required - set(reader.fieldnames or [])}")
        for row in reader:
            try:
                iq = parse_iq(row["data"])
                label = int(row["class"])
                timestamp = int(row["local_timestamp"])
                if label not in LABELS or label != recording.expected_label:
                    raise ValueError("unexpected label")
                samples.append(iq[VALID_BINS])
                labels.append(label)
                timestamps.append(timestamp)
            except (ValueError, TypeError, KeyError) as exc:
                rejected[str(exc).split(":")[0]] += 1
    if not samples:
        raise ValueError(f"{recording.recording_id}: no valid packets")
    return (np.stack(samples), np.asarray(labels, dtype=np.int8),
            np.asarray(timestamps, dtype=np.int64),
            {"valid_packets": len(samples), "rejected_packets": sum(rejected.values()), "rejection_reasons": dict(rejected)})


def features(iq_window: np.ndarray, timestamps: np.ndarray) -> np.ndarray:
    if iq_window.shape != (WINDOW, len(VALID_BINS), 2):
        raise ValueError(f"expected {(WINDOW, len(VALID_BINS), 2)}, got {iq_window.shape}")
    imag = iq_window[:, :, 0].astype(np.float64)
    real = iq_window[:, :, 1].astype(np.float64)
    amp = np.hypot(real, imag)
    baseline = np.maximum(np.median(amp, axis=0, keepdims=True), 1.0)
    relative = amp / baseline
    trend = np.linspace(0, 1, WINDOW)[:, None] * (relative[-1] - relative[0])
    detrended = relative - trend
    spectrum = np.abs(np.fft.rfft(detrended - detrended.mean(axis=0), axis=0)) ** 2
    freq = np.fft.rfftfreq(WINDOW, d=0.01)
    phase = np.arctan2(imag, real)
    phase_step = np.angle(np.exp(1j * np.diff(phase, axis=0)))
    gaps = np.diff(timestamps)
    positive = gaps[gaps > 0]
    nominal = np.median(positive) if positive.size else 10_000
    columns = [
        np.std(relative, axis=0),
        np.mean(np.abs(np.diff(relative, axis=0)), axis=0),
        np.quantile(relative, .95, axis=0) - np.quantile(relative, .05, axis=0),
        np.mean(np.abs(phase_step), axis=0),
        1 - np.abs(np.exp(1j * phase_step).mean(axis=0)),
    ]
    total_power = spectrum.sum(axis=0) + 1e-9
    for lo, hi in BANDS:
        columns.append(spectrum[(freq >= lo) & (freq < hi)].sum(axis=0) / total_power)
    vector = np.concatenate([*columns, np.array([
        float(np.mean(amp)), float(np.std(amp)),
        float(np.var(relative.mean(axis=1))),
        float(np.mean((gaps <= 0) | (gaps > 2.5 * nominal))),
    ])]).astype(np.float32)
    if not np.isfinite(vector).all():
        raise ValueError("non-finite feature vector")
    return vector


def window_features(iq: np.ndarray, labels: np.ndarray, timestamps: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    vectors, targets, offsets = [], [], []
    mixed = 0
    for start in range(0, len(labels) - WINDOW + 1, WINDOW):
        target = labels[start:start + WINDOW]
        if np.any(target != target[0]):
            mixed += 1
            continue
        vectors.append(features(iq[start:start + WINDOW], timestamps[start:start + WINDOW]))
        targets.append(int(target[0]))
        offsets.append(start)
    return np.asarray(vectors, dtype=np.float32).reshape(-1, len(FEATURE_NAMES)), np.asarray(targets, dtype=np.int8), np.asarray(offsets, dtype=np.int32), mixed
