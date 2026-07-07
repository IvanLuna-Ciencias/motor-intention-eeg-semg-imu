"""Storage utilities for multimodal acquisition files.

This module provides hardware-independent utilities to save EEG, sEMG, MYO,
event, and metadata files using a consistent public repository format.

No participant-identifiable information should be stored with these utilities.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence

import numpy as np


def ensure_directory(path: str | Path) -> Path:
    """Create a directory if it does not exist and return it as a Path."""
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def save_eeg_csv(
    data: np.ndarray,
    filename: str | Path,
    sampling_rate_hz: float,
    channel_prefix: str = "ch",
) -> Path:
    """Save EEG-like data to CSV.

    Parameters
    ----------
    data:
        Array with shape ``n_channels x n_samples``.
    filename:
        Output CSV filename.
    sampling_rate_hz:
        Sampling rate in Hz.
    channel_prefix:
        Prefix used for channel names.

    Returns
    -------
    pathlib.Path
        Path to the saved file.
    """
    output_path = Path(filename)
    ensure_directory(output_path.parent)

    array = np.asarray(data)

    if array.ndim != 2:
        raise ValueError("data must have shape n_channels x n_samples.")

    n_channels, n_samples = array.shape
    time_s = np.arange(n_samples, dtype=float) / float(sampling_rate_hz)

    header = ["time_s"] + [f"{channel_prefix}_{idx}" for idx in range(n_channels)]

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)

        for sample_idx in range(n_samples):
            row = [time_s[sample_idx]] + array[:, sample_idx].tolist()
            writer.writerow(row)

    return output_path


def save_semg_csv(
    data: np.ndarray,
    filename: str | Path,
    sampling_rate_hz: float,
    channel_prefix: str = "emg",
) -> Path:
    """Save sEMG data to CSV.

    Parameters
    ----------
    data:
        Array with shape ``n_channels x n_samples``.
    filename:
        Output CSV filename.
    sampling_rate_hz:
        Sampling rate in Hz.
    channel_prefix:
        Prefix used for sEMG channel names.

    Returns
    -------
    pathlib.Path
        Path to the saved file.
    """
    return save_eeg_csv(
        data=data,
        filename=filename,
        sampling_rate_hz=sampling_rate_hz,
        channel_prefix=channel_prefix,
    )


def save_events_csv(
    events: Iterable[Sequence[Any]],
    filename: str | Path,
) -> Path:
    """Save event markers to CSV.

    Each event row should contain:

    - time_s
    - marker
    - label
    """
    output_path = Path(filename)
    ensure_directory(output_path.parent)

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["time_s", "marker", "label"])

        for event in events:
            if len(event) != 3:
                raise ValueError(
                    "Each event must contain exactly three values: "
                    "time_s, marker, label."
                )
            writer.writerow(event)

    return output_path


def save_metadata_json(
    metadata: Mapping[str, Any],
    filename: str | Path,
) -> Path:
    """Save anonymized acquisition metadata to JSON."""
    output_path = Path(filename)
    ensure_directory(output_path.parent)

    with output_path.open("w", encoding="utf-8") as json_file:
        json.dump(dict(metadata), json_file, indent=2, ensure_ascii=False)

    return output_path


def save_myo_csv(
    messages: Iterable[Mapping[str, Any]],
    filename: str | Path,
) -> Path:
    """Save MYO receiver messages to CSV.

    Expected message keys may include:

    - timestamp_rel or timestamp
    - emg
    - orientation
    - imu.accelerometer
    - imu.gyroscope
    - pose
    - rssi
    """
    output_path = Path(filename)
    ensure_directory(output_path.parent)

    header = (
        ["time_s"]
        + [f"emg_{idx}" for idx in range(8)]
        + [f"orient_{idx}" for idx in range(4)]
        + [f"accel_{idx}" for idx in range(3)]
        + [f"gyro_{idx}" for idx in range(3)]
        + ["pose", "rssi"]
    )

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)

        for message in messages:
            time_s = message.get("timestamp_rel", message.get("timestamp", ""))

            emg = message.get("emg") or [""] * 8
            if len(emg) < 8:
                emg = list(emg) + [""] * (8 - len(emg))

            orientation = message.get("orientation") or [""] * 4
            if len(orientation) < 4:
                orientation = list(orientation) + [""] * (4 - len(orientation))

            imu = message.get("imu") or {}
            accel = imu.get("accelerometer", [""] * 3)
            gyro = imu.get("gyroscope", [""] * 3)

            if len(accel) < 3:
                accel = list(accel) + [""] * (3 - len(accel))
            if len(gyro) < 3:
                gyro = list(gyro) + [""] * (3 - len(gyro))

            pose = message.get("pose", "")
            rssi = message.get("rssi", "")

            row = (
                [time_s]
                + list(emg[:8])
                + list(orientation[:4])
                + list(accel[:3])
                + list(gyro[:3])
                + [pose, rssi]
            )
            writer.writerow(row)

    return output_path


def build_session_folder(
    root_dir: str | Path,
    subject_id: str,
    session_id: str,
    movement_block: str,
) -> Path:
    """Build a standardized anonymized session folder path."""
    safe_subject = subject_id.strip().replace(" ", "_")
    safe_session = session_id.strip().replace(" ", "_")
    safe_block = movement_block.strip().replace(" ", "_")

    return ensure_directory(Path(root_dir) / safe_subject / safe_session / safe_block)


def default_metadata(
    subject_id: str,
    session_id: str,
    movement_block: str,
    eeg_sampling_hz: float | None = None,
    semg_sampling_hz: float | None = None,
    myo_emg_sampling_hz: float | None = None,
    myo_imu_sampling_hz: float | None = None,
    notes: str = "",
) -> Dict[str, Any]:
    """Create a basic anonymized metadata dictionary."""
    return {
        "subject_id": subject_id,
        "session_id": session_id,
        "movement_block": movement_block,
        "eeg_sampling_hz": eeg_sampling_hz,
        "semg_sampling_hz": semg_sampling_hz,
        "myo_emg_sampling_hz": myo_emg_sampling_hz,
        "myo_imu_sampling_hz": myo_imu_sampling_hz,
        "notes": notes,
    }
