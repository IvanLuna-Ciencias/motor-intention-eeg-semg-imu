"""Device configuration utilities for multimodal acquisition.

This module defines public-safe configuration containers for acquisition
hardware and communication endpoints.

It does not initialize hardware. It only stores and validates configuration.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

import yaml


@dataclass(frozen=True)
class MindRoveConfig:
    """MindRove EEG configuration."""

    connection_mode: str = "WiFi"
    mac_address: str = ""
    eeg_units: str = "uV"

    def validate(self) -> None:
        """Validate MindRove configuration."""
        valid_modes = {"WiFi", "Bluetooth"}

        if self.connection_mode not in valid_modes:
            raise ValueError(
                f"Invalid MindRove connection_mode '{self.connection_mode}'. "
                f"Valid modes: {sorted(valid_modes)}"
            )

        if self.connection_mode == "Bluetooth" and not self.mac_address.strip():
            raise ValueError("mac_address is required when using Bluetooth mode.")


@dataclass(frozen=True)
class BiosignalspluxConfig:
    """Biosignalsplux sEMG configuration."""

    address: str = ""
    sampling_rate_hz: float = 1000.0
    channels_mask: int = 0x03
    resolution_bits: int = 16
    dll_path: str = ""

    def validate(self) -> None:
        """Validate Biosignalsplux configuration."""
        if self.sampling_rate_hz <= 0:
            raise ValueError("sampling_rate_hz must be greater than zero.")

        if self.resolution_bits <= 0:
            raise ValueError("resolution_bits must be greater than zero.")


@dataclass(frozen=True)
class MyoBridgeConfig:
    """MYO TCP bridge configuration."""

    receiver_host: str = "127.0.0.1"
    receiver_port: int = 9999
    sender_mode: str = "synthetic"
    synthetic_rate_hz: float = 50.0
    synthetic_duration_sec: float = 10.0
    sdk_path_env_var: str = "MYO_SDK_PATH"

    def validate(self) -> None:
        """Validate MYO bridge configuration."""
        if self.receiver_port <= 0:
            raise ValueError("receiver_port must be greater than zero.")

        if self.sender_mode not in {"synthetic", "sdk"}:
            raise ValueError("sender_mode must be either 'synthetic' or 'sdk'.")

        if self.synthetic_rate_hz <= 0:
            raise ValueError("synthetic_rate_hz must be greater than zero.")

        if self.synthetic_duration_sec <= 0:
            raise ValueError("synthetic_duration_sec must be greater than zero.")


@dataclass(frozen=True)
class LabVIEWConfig:
    """LabVIEW/cRIO streaming configuration."""

    enabled: bool = False
    host: str = "127.0.0.1"
    port: int = 5005
    keepalive_hz: float = 25.0

    def validate(self) -> None:
        """Validate LabVIEW/cRIO configuration."""
        if self.port <= 0:
            raise ValueError("port must be greater than zero.")

        if self.keepalive_hz <= 0:
            raise ValueError("keepalive_hz must be greater than zero.")


@dataclass(frozen=True)
class AcquisitionDeviceConfig:
    """Full acquisition device configuration."""

    mindrove: MindRoveConfig
    biosignalsplux: BiosignalspluxConfig
    myo: MyoBridgeConfig
    labview: LabVIEWConfig
    output_root: str = "outputs/acquisition"

    def validate(self) -> None:
        """Validate all nested configuration sections."""
        self.mindrove.validate()
        self.biosignalsplux.validate()
        self.myo.validate()
        self.labview.validate()

    def output_root_path(self) -> Path:
        """Return output root as a Path."""
        return Path(self.output_root)

    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as a nested dictionary."""
        return {
            "mindrove": self.mindrove.__dict__,
            "biosignalsplux": self.biosignalsplux.__dict__,
            "myo": self.myo.__dict__,
            "labview": self.labview.__dict__,
            "output_root": self.output_root,
        }


def load_acquisition_device_config(path: str | Path) -> AcquisitionDeviceConfig:
    """Load acquisition device configuration from a YAML file."""
    config_path = Path(path)

    with config_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}

    return acquisition_device_config_from_dict(data)


def acquisition_device_config_from_dict(
    data: Mapping[str, Any],
) -> AcquisitionDeviceConfig:
    """Create AcquisitionDeviceConfig from a dictionary."""
    mindrove_data = data.get("mindrove", {}) or {}
    biosignalsplux_data = data.get("biosignalsplux", {}) or {}
    myo_data = data.get("myo", {}) or {}
    labview_data = data.get("labview", {}) or {}

    config = AcquisitionDeviceConfig(
        mindrove=MindRoveConfig(**mindrove_data),
        biosignalsplux=BiosignalspluxConfig(**biosignalsplux_data),
        myo=MyoBridgeConfig(**myo_data),
        labview=LabVIEWConfig(**labview_data),
        output_root=str(data.get("output_root", "outputs/acquisition")),
    )

    config.validate()
    return config


def save_acquisition_device_config(
    config: AcquisitionDeviceConfig,
    path: str | Path,
) -> Path:
    """Save acquisition device configuration to a YAML file."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(
            config.to_dict(),
            file,
            sort_keys=False,
            allow_unicode=True,
        )

    return output_path
