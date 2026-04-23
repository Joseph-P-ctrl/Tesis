from __future__ import annotations

import csv
import os
from datetime import datetime
from typing import Iterable, List

import numpy as np


def ensure_parent_dir(file_path: str) -> None:
    parent = os.path.dirname(file_path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def append_prediction_rows(csv_path: str, rows: Iterable[List[str]]) -> None:
    ensure_parent_dir(csv_path)
    file_exists = os.path.exists(csv_path)
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "frame_idx", "emotion", "confidence"])
        writer.writerows(rows)


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def stable_softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values)
