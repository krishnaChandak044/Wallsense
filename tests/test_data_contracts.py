import csv
import json

import numpy as np
import pytest
import h5py

from wallsense.csibench import inspect_task
from wallsense.csipilot import NAMES, extract_features, read_h5
from wallsense.pipeline import split_for
from wallsense.wallhack import FEATURE_NAMES, Recording, WINDOW, features, load_recording, parse_iq, recordings


def test_wallhack_iq_contract():
    row = "[" + ",".join(str(i) for i in range(256)) + "]"
    parsed = parse_iq(row)
    assert parsed.shape == (128, 2)
    assert parsed[0].tolist() == [0, 1]
    for invalid in ("1,2,3", "[1,2]", "[" + ",".join(["nan"] * 256) + "]"):
        with pytest.raises(ValueError):
            parse_iq(invalid)


def test_split_is_recording_safe_and_has_three_classes(tmp_path):
    for scenario in ("LOS", "NLOS"):
        for antenna in ("BQ", "PIFA"):
            directory = tmp_path / scenario / antenna
            directory.mkdir(parents=True)
            for stem in ("b1", "w1", "w2", "w3", "w4", "w5", "ww1", "ww2", "ww3", "ww4", "ww5"):
                (directory / f"{stem}.csv").touch()
    items = recordings(tmp_path)
    assert len(items) == 44
    partitions = {part: {item.recording_id for item in items if split_for(item.recording_id) == part}
                  for part in ("train", "validation", "test")}
    assert len(set.union(*partitions.values())) == 44
    assert not (partitions["train"] & partitions["validation"])
    assert not (partitions["train"] & partitions["test"])
    assert not (partitions["validation"] & partitions["test"])
    for part, ids in partitions.items():
        assert {item.expected_label for item in items if item.recording_id in ids} == {0, 1, 2}, part


def test_corrupt_wallhack_row_is_counted(tmp_path):
    path = tmp_path / "w1.csv"
    good = "[" + ",".join(["1"] * 256) + "]"
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["data", "class", "local_timestamp"])
        writer.writeheader()
        writer.writerow({"data": good, "class": 1, "local_timestamp": 10000})
        writer.writerow({"data": "[broken]", "class": 1, "local_timestamp": 20000})
    record = Recording(path, "LOS/BQ/w1", "LOS", "BQ", 1)
    iq, labels, times, audit = load_recording(record)
    assert iq.shape == (1, 52, 2)
    assert labels.tolist() == [1]
    assert times.tolist() == [10000]
    assert audit["rejected_packets"] == 1


def test_features_have_no_label_and_are_finite():
    rng = np.random.default_rng(7)
    iq = rng.normal(size=(WINDOW, 52, 2)).astype(np.float32)
    times = np.arange(WINDOW, dtype=np.int64) * 10000
    vector = features(iq, times)
    assert vector.shape == (len(FEATURE_NAMES),)
    assert np.isfinite(vector).all()


def test_csibench_split_overlap_rejected(tmp_path):
    root = tmp_path / "FallDetection"
    (root / "metadata").mkdir(parents=True)
    (root / "splits").mkdir()
    (root / "metadata" / "sample_metadata.csv").write_text("id,file_path,label,user\n1,sub_Human/a.h5,fall,U01\n2,sub_Human/b.h5,normal,U02\n")
    (root / "metadata" / "label_mapping.json").write_text(json.dumps({"fall": 1, "normal": 0}))
    for name, ids in (("train_id", [1]), ("val_id", [2]), ("test_id", [1])):
        (root / "splits" / f"{name}.json").write_text(json.dumps(ids))
    with pytest.raises(ValueError, match="overlapping"):
        inspect_task(tmp_path)


def test_csibench_h5_orientation_and_shape(tmp_path):
    path = tmp_path / "sample.h5"
    source = np.ones((64, 500, 1), dtype=np.float32)
    source[2, 5, 0] = 9
    with h5py.File(path, "w") as dest:
        dest.create_dataset("CSI_amps", data=source)
    parsed = read_h5(path)
    assert parsed.shape == (500, 64)
    assert parsed[5, 2] == 9
    vector = extract_features(parsed)
    assert vector.shape == (len(NAMES),)
    assert np.isfinite(vector).all()
