"""Create synthetic acquisition sample files.

This script generates small synthetic EEG, sEMG, MYO, event, and metadata files
to demonstrate the expected public data structure without using real participant
data or hardware-dependent acquisition code.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from motor_intention.acquisition.storage import (
    default_metadata,
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


def create_synthetic_myo_messages(duration_sec: float, fs_hz: float = 50.0):
    """Create synthetic MYO-like messages."""
    rng = np.random.default_rng(seed=42)
    n_samples = int(duration_sec * fs_hz)

    messages = []

    for idx in range(n_samples):
        time_s = idx / fs_hz

        emg = rng.normal(loc=0.0, scale=20.0, size=8).round(3).tolist()
        orientation = rng.normal(loc=0.0, scale=0.1, size=4).round(4).tolist()
        accel = rng.normal(loc=0.0, scale=0.3, size=3).round(4).tolist()
        gyro = rng.normal(loc=0.0, scale=0.2, size=3).round(4).tolist()

        messages.append(
            {
                "timestamp_rel": round(time_s, 4),
                "emg": emg,
                "orientation": orientation,
                "imu": {
                    "accelerometer": accel,
                    "gyroscope": gyro,
                },
                "pose": "rest",
                "rssi": -55,
            }
        )

    return messages


def create_synthetic_events(total_trials: int):
    """Create synthetic event rows using the trial protocol utilities."""
    trial_list = build_trial_list(
        movement_block="Codo",
        total_trials=total_trials,
        seed=123,
    )

    protocol = TrialProtocol(trial_list=trial_list)
    current_time = 0.0

    protocol.start(time_s=current_time)

    while not protocol.is_finished:
        phase_duration = protocol.get_phase_duration()
        current_time += phase_duration
        protocol.advance_phase(time_s=current_time)

    return protocol.as_event_rows()


def main() -> None:
    output_dir = PROJECT_ROOT / "data" / "sample"
    output_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(seed=7)

    total_trials = 4
    duration_sec = estimate_protocol_duration_sec(total_trials)

    eeg_fs = 500.0
    semg_fs = 1000.0

    eeg_samples = int(duration_sec * eeg_fs)
    semg_samples = int(duration_sec * semg_fs)

    synthetic_eeg = rng.normal(
        loc=0.0,
        scale=10.0,
        size=(6, eeg_samples),
    )

    synthetic_semg = rng.normal(
        loc=0.0,
        scale=50.0,
        size=(2, semg_samples),
    )

    synthetic_events = create_synthetic_events(total_trials=total_trials)
    synthetic_myo = create_synthetic_myo_messages(duration_sec=duration_sec)

    metadata = default_metadata(
        subject_id="sub-synthetic001",
        session_id="ses-01",
        movement_block="Codo",
        eeg_sampling_hz=eeg_fs,
        semg_sampling_hz=semg_fs,
        myo_emg_sampling_hz=200.0,
        myo_imu_sampling_hz=50.0,
        notes="Synthetic example only. No real participant data.",
    )

    save_eeg_csv(
        data=synthetic_eeg,
        filename=output_dir / "synthetic_eeg.csv",
        sampling_rate_hz=eeg_fs,
    )

    save_semg_csv(
        data=synthetic_semg,
        filename=output_dir / "synthetic_semg_biosignals.csv",
        sampling_rate_hz=semg_fs,
    )

    save_events_csv(
        events=synthetic_events,
        filename=output_dir / "synthetic_events.csv",
    )

    save_myo_csv(
        messages=synthetic_myo,
        filename=output_dir / "synthetic_myo.csv",
    )

    save_metadata_json(
        metadata=metadata,
        filename=output_dir / "example_metadata.json",
    )

    print("Synthetic acquisition sample files created in:")
    print(output_dir)


if __name__ == "__main__":
    main()
