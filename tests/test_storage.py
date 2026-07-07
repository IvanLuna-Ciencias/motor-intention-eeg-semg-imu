"""Tests for acquisition storage utilities."""

import json
from pathlib import Path

import numpy as np

from motor_intention.acquisition.storage import (
    default_metadata,
    save_eeg_csv,
    save_events_csv,
    save_metadata_json,
    save_myo_csv,
    save_semg_csv,
)


def test_save_eeg_and_semg_csv(tmp_path):
    eeg = np.zeros((6, 10))
    semg = np.ones((2, 20))

    eeg_file = save_eeg_csv(eeg, tmp_path / "eeg.csv", sampling_rate_hz=500.0)
    semg_file = save_semg_csv(semg, tmp_path / "semg.csv", sampling_rate_hz=1000.0)

    assert eeg_file.exists()
    assert semg_file.exists()

    eeg_lines = eeg_file.read_text(encoding="utf-8").splitlines()
    semg_lines = semg_file.read_text(encoding="utf-8").splitlines()

    assert eeg_lines[0].startswith("time_s,ch_0")
    assert semg_lines[0].startswith("time_s,emg_0")
    assert len(eeg_lines) == 11
    assert len(semg_lines) == 21


def test_save_events_csv(tmp_path):
    events = [
        (0.0, 88.0, "InicioProtocolo"),
        (1.0, 10.0, "Fase=alert,Trial=1,Mov=F"),
    ]

    event_file = save_events_csv(events, tmp_path / "events.csv")

    assert event_file.exists()
    lines = event_file.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "time_s,marker,label"
    assert len(lines) == 3


def test_save_metadata_json(tmp_path):
    metadata = default_metadata(
        subject_id="sub-synthetic001",
        session_id="ses-01",
        movement_block="Codo",
        eeg_sampling_hz=500.0,
    )

    metadata_file = save_metadata_json(metadata, tmp_path / "metadata.json")

    assert metadata_file.exists()

    loaded = json.loads(metadata_file.read_text(encoding="utf-8"))
    assert loaded["subject_id"] == "sub-synthetic001"
    assert loaded["movement_block"] == "Codo"


def test_save_myo_csv(tmp_path):
    messages = [
        {
            "timestamp_rel": 0.0,
            "emg": [0] * 8,
            "orientation": [1, 0, 0, 0],
            "imu": {
                "accelerometer": [0, 0, 1],
                "gyroscope": [0, 0, 0],
            },
            "pose": "rest",
            "rssi": -55,
        }
    ]

    myo_file = save_myo_csv(messages, tmp_path / "myo.csv")

    assert myo_file.exists()
    lines = myo_file.read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("time_s,emg_0")
    assert len(lines) == 2
