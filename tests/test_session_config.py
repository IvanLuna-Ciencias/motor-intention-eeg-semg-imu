"""Tests for acquisition session configuration utilities."""

from motor_intention.acquisition.session_config import (
    AcquisitionSessionConfig,
    build_output_filenames,
    sanitize_token,
)


def test_sanitize_token():
    assert sanitize_token("sub 001") == "sub_001"
    assert sanitize_token("ses/01") == "ses_01"
    assert sanitize_token(" Rot Hombro ") == "Rot_Hombro"


def test_session_config_base_filename():
    config = AcquisitionSessionConfig(
        subject_id="sub-001",
        session_id="ses-01",
        movement_block="Codo",
        total_trials=40,
        timestamp="20260706_120000",
    )

    assert config.base_filename() == "sub-001_ses-01_Codo_20260706_120000"


def test_session_config_metadata():
    config = AcquisitionSessionConfig(
        subject_id="sub-001",
        session_id="ses-01",
        movement_block="Hombro",
        total_trials=40,
        timestamp="20260706_120000",
    )

    metadata = config.to_metadata()

    assert metadata["subject_id"] == "sub-001"
    assert metadata["session_id"] == "ses-01"
    assert metadata["movement_block"] == "Hombro"
    assert metadata["total_trials"] == 40


def test_build_output_filenames(tmp_path):
    config = AcquisitionSessionConfig(
        subject_id="sub-001",
        session_id="ses-01",
        movement_block="Codo",
        total_trials=40,
        timestamp="20260706_120000",
    )

    filenames = build_output_filenames(config, tmp_path)

    assert filenames["folder"].name == "Codo"
    assert filenames["eeg"].name.endswith("_eeg.csv")
    assert filenames["semg"].name.endswith("_semg.csv")
    assert filenames["myo"].name.endswith("_myo.csv")
    assert filenames["events"].name.endswith("_events.csv")
    assert filenames["metadata"].name.endswith("_metadata.json")
