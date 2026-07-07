"""Tests for acquisition device configuration utilities."""

from motor_intention.acquisition.device_config import (
    AcquisitionDeviceConfig,
    BiosignalspluxConfig,
    LabVIEWConfig,
    MindRoveConfig,
    MyoBridgeConfig,
    acquisition_device_config_from_dict,
    load_acquisition_device_config,
    save_acquisition_device_config,
)


def test_default_device_config_validation():
    config = AcquisitionDeviceConfig(
        mindrove=MindRoveConfig(),
        biosignalsplux=BiosignalspluxConfig(),
        myo=MyoBridgeConfig(),
        labview=LabVIEWConfig(),
    )

    config.validate()

    assert config.output_root == "outputs/acquisition"
    assert config.mindrove.connection_mode == "WiFi"
    assert config.myo.receiver_port == 9999


def test_device_config_from_dict():
    data = {
        "mindrove": {
            "connection_mode": "WiFi",
            "eeg_units": "uV",
        },
        "biosignalsplux": {
            "address": "demo-address",
            "sampling_rate_hz": 1000.0,
            "channels_mask": 3,
            "resolution_bits": 16,
            "dll_path": "",
        },
        "myo": {
            "receiver_host": "127.0.0.1",
            "receiver_port": 9999,
            "sender_mode": "synthetic",
            "synthetic_rate_hz": 50.0,
            "synthetic_duration_sec": 5.0,
            "sdk_path_env_var": "MYO_SDK_PATH",
        },
        "labview": {
            "enabled": False,
            "host": "127.0.0.1",
            "port": 5005,
            "keepalive_hz": 25.0,
        },
        "output_root": "outputs/test",
    }

    config = acquisition_device_config_from_dict(data)

    assert config.biosignalsplux.address == "demo-address"
    assert config.output_root == "outputs/test"
    assert config.labview.enabled is False


def test_save_and_load_device_config(tmp_path):
    config = AcquisitionDeviceConfig(
        mindrove=MindRoveConfig(),
        biosignalsplux=BiosignalspluxConfig(address="demo-address"),
        myo=MyoBridgeConfig(receiver_port=9998),
        labview=LabVIEWConfig(enabled=True, host="127.0.0.1"),
        output_root="outputs/demo",
    )

    config_path = save_acquisition_device_config(
        config,
        tmp_path / "acquisition.yaml",
    )

    loaded = load_acquisition_device_config(config_path)

    assert loaded.biosignalsplux.address == "demo-address"
    assert loaded.myo.receiver_port == 9998
    assert loaded.labview.enabled is True
    assert loaded.output_root == "outputs/demo"
