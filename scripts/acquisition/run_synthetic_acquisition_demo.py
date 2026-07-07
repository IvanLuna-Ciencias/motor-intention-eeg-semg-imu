"""Run a complete synthetic acquisition demo.

This script simulates a full multimodal acquisition session without requiring
EEG, sEMG, MYO, LabVIEW, or cRIO hardware.

It uses the clean public modules for:

- Session configuration.
- Device configuration.
- Trial protocol generation.
- Synthetic signal generation.
- Standardized CSV/JSON storage.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Tuple

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from motor_intention.acquisition.device_config import load_acquisition_device_config
from motor_intention.acquisition.session_config import (
    AcquisitionSessionConfig,
    build_output_filenames,
)
from motor_intention.acquisition.storage import (
    save_eeg_csv,
    save_events_csv,
    save_metadata_json,
    save_myo_csv,
    save_semg_csv,
)
from motor_intention.protocols.trial_protocol import (
    TrialProtocol,
    build_trial_list,
    estimate_protocol_duration_sec,
)


DEFAULT_CONFIG = PROJECT_ROOT / "configs" / "acquisition" / "acquisition.example.yaml"


def create_synthetic_eeg(
    n_channels: int,
    n_samples: int,
    sampling_rate_hz: float,
    seed: int = 7,
) -> np.ndarray:
    """Create synthetic EEG-like data."""
    rng = np.random.default_rng(seed)
    time_s = np.arange(n_samples) / sampling_rate_hz

    data = rng.normal(loc=0.0, scale=8.0, size=(n_channels, n_samples))

    # Add weak synthetic sensorimotor-like rhythms.
    for channel_idx in range(n_channels):
        mu_component = 2.0 * np.sin(2.0 * np.pi * 10.0 * time_s)
        beta_component = 1.0 * np.sin(2.0 * np.pi * 20.0 * time_s)
        data[channel_idx] += mu_component + beta_component

    return data


def create_synthetic_semg(
    n_channels: int,
    n_samples: int,
    sampling_rate_hz: float,
    seed: int = 11,
) -> np.ndarray:
    """Create synthetic sEMG-like data."""
    rng = np.random.default_rng(seed)
    time_s = np.arange(n_samples) / sampling_rate_hz

    data = rng.normal(loc=0.0, scale=20.0, size=(n_channels, n_samples))

    envelope = 1.0 + 0.5 * np.sin(2.0 * np.pi * 0.5 * time_s)
    data *= envelope

    return data


def create_synthetic_myo_messages(
    duration_sec: float,
    imu_rate_hz: float,
    seed: int = 42,
) -> List[dict]:
    """Create synthetic MYO-like messages."""
    rng = np.random.default_rng(seed)
    n_samples = int(duration_sec * imu_rate_hz)

    messages = []

    for sample_idx in range(n_samples):
        time_s = sample_idx / imu_rate_hz

        messages.append(
            {
                "timestamp_rel": round(time_s, 4),
                "timestamp_origin": round(time_s, 4),
                "emg": rng.normal(loc=0.0, scale=20.0, size=8).round(3).tolist(),
                "orientation": rng.normal(loc=0.0, scale=0.1, size=4).round(4).tolist(),
                "imu": {
                    "accelerometer": rng.normal(
                        loc=0.0,
                        scale=0.3,
                        size=3,
                    ).round(4).tolist(),
                    "gyroscope": rng.normal(
                        loc=0.0,
                        scale=0.2,
                        size=3,
                    ).round(4).tolist(),
                },
                "pose": "rest",
                "rssi": -55,
            }
        )

    return messages


def create_synthetic_protocol_events(
    movement_block: str,
    total_trials: int,
    seed: int = 123,
) -> Tuple[List[Tuple[float, float, str]], List[str]]:
    """Create synthetic protocol events and return the randomized trial list."""
    trial_list = build_trial_list(
        movement_block=movement_block,
        total_trials=total_trials,
        seed=seed,
    )

    protocol = TrialProtocol(trial_list=trial_list)
    current_time_s = 0.0

    protocol.start(time_s=current_time_s)

    while not protocol.is_finished:
        current_time_s += protocol.get_phase_duration()
        protocol.advance_phase(time_s=current_time_s)

    return protocol.as_event_rows(), trial_list


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a complete synthetic multimodal acquisition demo."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to acquisition YAML configuration.",
    )
    parser.add_argument(
        "--subject-id",
        default="sub-synthetic001",
        help="Anonymized subject identifier.",
    )
    parser.add_argument(
        "--session-id",
        default="ses-01",
        help="Anonymized session identifier.",
    )
    parser.add_argument(
        "--movement-block",
        default="Codo",
        choices=["Codo", "Hombro", "RotHombro"],
        help="Movement block to simulate.",
    )
    parser.add_argument(
        "--total-trials",
        type=int,
        default=4,
        help="Total number of synthetic trials.",
    )
    parser.add_argument(
        "--timestamp",
        default="20260706_120000",
        help="Fixed timestamp for reproducible demo filenames.",
    )

    args = parser.parse_args()

    device_config = load_acquisition_device_config(args.config)

    session_config = AcquisitionSessionConfig(
        subject_id=args.subject_id,
        session_id=args.session_id,
        movement_block=args.movement_block,
        total_trials=args.total_trials,
        feedback_mode="Visual",
        eeg_filter="Sin Filtro",
        semg_filter="Sin Filtro",
        connection_mode=device_config.mindrove.connection_mode,
        timestamp=args.timestamp,
    )

    output_files = build_output_filenames(
        config=session_config,
        output_root=PROJECT_ROOT / device_config.output_root,
    )

    duration_sec = estimate_protocol_duration_sec(session_config.total_trials)

    eeg_fs = 500.0
    semg_fs = float(device_config.biosignalsplux.sampling_rate_hz)
    myo_imu_fs = float(device_config.myo.synthetic_rate_hz)

    eeg_data = create_synthetic_eeg(
        n_channels=6,
        n_samples=int(duration_sec * eeg_fs),
        sampling_rate_hz=eeg_fs,
    )

    semg_data = create_synthetic_semg(
        n_channels=2,
        n_samples=int(duration_sec * semg_fs),
        sampling_rate_hz=semg_fs,
    )

    myo_messages = create_synthetic_myo_messages(
        duration_sec=duration_sec,
        imu_rate_hz=myo_imu_fs,
    )

    event_rows, trial_list = create_synthetic_protocol_events(
        movement_block=session_config.movement_block,
        total_trials=session_config.total_trials,
    )

    metadata = session_config.to_metadata()
    metadata.update(device_config.to_dict())
    metadata.update(
        {
            "demo_type": "synthetic_acquisition",
            "trial_list": trial_list,
            "duration_sec": duration_sec,
            "eeg_sampling_hz": eeg_fs,
            "semg_sampling_hz": semg_fs,
            "myo_synthetic_rate_hz": myo_imu_fs,
            "notes": "Synthetic demo only. No real participant data.",
        }
    )

    save_eeg_csv(eeg_data, output_files["eeg"], sampling_rate_hz=eeg_fs)
    save_semg_csv(semg_data, output_files["semg"], sampling_rate_hz=semg_fs)
    save_myo_csv(myo_messages, output_files["myo"])
    save_events_csv(event_rows, output_files["events"])
    save_metadata_json(metadata, output_files["metadata"])

    print("Synthetic acquisition demo completed.")
    print(f"Output folder: {output_files['folder']}")
    print("Generated files:")
    print(f"  EEG:      {output_files['eeg'].name}")
    print(f"  sEMG:     {output_files['semg'].name}")
    print(f"  MYO:      {output_files['myo'].name}")
    print(f"  Events:   {output_files['events'].name}")
    print(f"  Metadata: {output_files['metadata'].name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
