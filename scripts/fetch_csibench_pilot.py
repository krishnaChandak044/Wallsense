"""Fetch a bounded, user-disjoint CSI-Bench v12 fall pilot from Kaggle.

Requires the official `kaggle` CLI (invoked through `uvx`) and publicly available
FallDetection files. This deliberately does not download the 81 GB full release.
The resulting metrics must be called a *pilot subset*, never full benchmark.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "csi-bench"
ARTIFACTS = ROOT / "artifacts"
TEST_USERS = {"U12", "U13"}
VALIDATION_USERS = {"U16", "U18"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-user-class", type=int, default=35)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if args.per_user_class < 1 or args.workers < 1:
        parser.error("positive --per-user-class and --workers required")
    metadata = DATA / "FallDetection" / "metadata" / "sample_metadata.csv"
    if not metadata.exists():
        parser.error("download CSI-Bench FallDetection metadata first")
    frame = pd.read_csv(metadata)
    chosen = []
    for (user, label), group in frame.groupby(["user", "label"]):
        subset = group.sample(n=min(args.per_user_class, len(group)), random_state=20261027)
        for row in subset.itertuples():
            split = "test" if user in TEST_USERS else "validation" if user in VALIDATION_USERS else "train"
            relative = Path("FallDetection") / str(row.file_path).removeprefix("./")
            chosen.append({"id": str(row.id), "user": str(user), "label": str(label),
                           "split": split, "file": relative.as_posix(),
                           "environment": str(row.environment), "device": str(row.device)})
    chosen.sort(key=lambda item: item["id"])
    ARTIFACTS.mkdir(exist_ok=True)
    manifest = {"source": "CSI-Bench", "version": 12, "task": "FallDetection",
                "scope": "bounded pilot subset, not full CSI-Bench benchmark",
                "selection_seed": 20261027, "per_user_class_cap": args.per_user_class,
                "split_unit": "user", "test_users": sorted(TEST_USERS),
                "validation_users": sorted(VALIDATION_USERS), "samples": chosen}
    (ARTIFACTS / "csibench_pilot_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    pending = [item for item in chosen if not (DATA / item["file"]).exists()]
    print(f"Selected {len(chosen)} samples; {len(pending)} files to retrieve", flush=True)

    def fetch(item: dict) -> tuple[str, str | None]:
        command = ["uvx", "kaggle", "datasets", "download", "guozhenjennzhu/csi-bench/12",
                   "-f", item["file"], "-p", str(DATA), "--unzip", "-q"]
        for attempt in range(3):
            try:
                result = subprocess.run(command, capture_output=True, text=True, timeout=120)
            except subprocess.TimeoutExpired:
                continue
            if result.returncode == 0 and (DATA / item["file"]).is_file():
                return item["id"], None
        return item["id"], result.stderr[-400:] or f"exit {result.returncode}"

    errors = {}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for index, outcome in enumerate(as_completed(pool.submit(fetch, item) for item in pending), 1):
            sample_id, error = outcome.result()
            if error:
                errors[sample_id] = error
            if index % 50 == 0 or index == len(pending):
                print(f"{index}/{len(pending)} fetched; errors={len(errors)}", flush=True)
    (ARTIFACTS / "csibench_download_errors.json").write_text(json.dumps(errors, indent=2) + "\n")
    if errors:
        raise RuntimeError(f"{len(errors)} CSI-Bench files failed; see artifacts/csibench_download_errors.json")


if __name__ == "__main__":
    main()
