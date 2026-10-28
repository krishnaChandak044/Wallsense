"""Explicit local commands; no synthetic fallback when a dataset is missing."""

from __future__ import annotations

import argparse
import json

from .common import ARTIFACTS, write_json
from .csibench import inspect_task
from .csipilot import evaluate as csi_evaluate, prepare as csi_prepare, train as csi_train
from .pipeline import evaluate, inventory, prepare, train


def main() -> None:
    parser = argparse.ArgumentParser(prog="wallsense")
    parser.add_argument("command", choices=("wallhack-inventory", "wallhack-prepare", "wallhack-train", "wallhack-evaluate", "csi-inventory", "csi-prepare", "csi-train", "csi-evaluate"))
    parser.add_argument("--task", choices=("FallDetection", "BreathingDetection"), default="FallDetection")
    args = parser.parse_args()
    if args.command == "wallhack-inventory":
        value = inventory()
        result = {"recordings": len(value["recordings"]), "group_counts": value["group_counts"]}
    elif args.command == "wallhack-prepare":
        result = prepare()
    elif args.command == "wallhack-train":
        result = train()
    elif args.command == "wallhack-evaluate":
        result = evaluate()
    elif args.command == "csi-inventory":
        result = inspect_task(task=args.task)
        write_json(ARTIFACTS / f"csibench_{args.task}_inventory.json", result)
    elif args.command == "csi-prepare":
        result = csi_prepare()
    elif args.command == "csi-train":
        result = csi_train()
    else:
        result = csi_evaluate()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
