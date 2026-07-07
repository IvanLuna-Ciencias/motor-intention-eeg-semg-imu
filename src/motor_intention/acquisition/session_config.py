"""Session configuration utilities for multimodal acquisition.

This module defines anonymized session-level configuration helpers used by
acquisition scripts. It is hardware-independent and does not depend on EEG,
sEMG, MYO, LabVIEW, or cRIO APIs.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from motor_intention.protocols.event_markers import get_block_movements


@dataclass(frozen=True)
class AcquisitionSessionConfig:
    """Anonymized acquisition session configuration."""

    subject_id: str
    session_id: str
    movement_block: str
    total_trials: int = 40
    feedback_mode: str = "Visual"
    eeg_filter: str = "Sin Filtro"
    semg_filter: str = "Bandpass 10-450 Hz"
    connection_mode: str = "WiFi"
    timestamp: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate session configuration."""
        if not self.subject_id.strip():
            raise ValueError("subject_id cannot be empty.")

        if not self.session_id.strip():
            raise ValueError("session_id cannot be empty.")

        get_block_movements(self.movement_block)

        if self.total_trials <= 0:
            raise ValueError("total_trials must be greater than zero.")

        if self.total_trials % 2 != 0:
            raise ValueError("total_trials must be even for balanced movement blocks.")

    @property
    def timestamp_str(self) -> str:
        """Return a timestamp string suitable for filenames."""
        if self.timestamp:
            return self.timestamp

        return datetime.now().strftime("%Y%m%d_%H%M%S")

    @property
    def safe_subject_id(self) -> str:
        """Return a filesystem-safe subject identifier."""
        return sanitize_token(self.subject_id)

    @property
    def safe_session_id(self) -> str:
        """Return a filesystem-safe session identifier."""
        return sanitize_token(self.session_id)

    @property
    def safe_movement_block(self) -> str:
        """Return a filesystem-safe movement block identifier."""
        return sanitize_token(self.movement_block)

    def base_filename(self) -> str:
        """Build a standardized base filename."""
        return (
            f"{self.safe_subject_id}_"
            f"{self.safe_session_id}_"
            f"{self.safe_movement_block}_"
            f"{self.timestamp_str}"
        )

    def session_folder(self, root_dir: str | Path) -> Path:
        """Build a standardized session output folder."""
        return (
            Path(root_dir)
            / self.safe_subject_id
            / self.safe_session_id
            / self.safe_movement_block
        )

    def to_metadata(self) -> Dict[str, object]:
        """Convert session configuration to public-safe metadata."""
        return {
            "subject_id": self.subject_id,
            "session_id": self.session_id,
            "movement_block": self.movement_block,
            "total_trials": self.total_trials,
            "feedback_mode": self.feedback_mode,
            "eeg_filter": self.eeg_filter,
            "semg_filter": self.semg_filter,
            "connection_mode": self.connection_mode,
            "timestamp": self.timestamp_str,
        }


def sanitize_token(value: str) -> str:
    """Return a simple filesystem-safe token."""
    token = value.strip().replace(" ", "_")
    allowed = []

    for char in token:
        if char.isalnum() or char in ("_", "-", "."):
            allowed.append(char)
        else:
            allowed.append("_")

    sanitized = "".join(allowed)

    while "__" in sanitized:
        sanitized = sanitized.replace("__", "_")

    return sanitized.strip("_")


def build_output_filenames(
    config: AcquisitionSessionConfig,
    output_root: str | Path,
) -> Dict[str, Path]:
    """Build standardized output filenames for one acquisition session."""
    folder = config.session_folder(output_root)
    base = config.base_filename()

    return {
        "folder": folder,
        "eeg": folder / f"{base}_eeg.csv",
        "semg": folder / f"{base}_semg.csv",
        "myo": folder / f"{base}_myo.csv",
        "events": folder / f"{base}_events.csv",
        "metadata": folder / f"{base}_metadata.json",
    }
