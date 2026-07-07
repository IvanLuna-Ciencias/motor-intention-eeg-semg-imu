"""Biosignalsplux acquisition wrapper.

This module provides a clean wrapper for Biosignalsplux sEMG acquisition.

The implementation is designed so the public repository can be imported and
tested without requiring the proprietary/device-specific `plux` dependency.

Actual hardware acquisition requires:

- Biosignalsplux Python API.
- Correct DLL/API path configuration.
- A valid Biosignalsplux device address.
"""

from __future__ import annotations

import sys
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

from motor_intention.acquisition.device_config import BiosignalspluxConfig


class BiosignalspluxDependencyError(ImportError):
    """Raised when the Biosignalsplux Python API is not available."""


def import_plux(dll_path: str = ""):
    """Import the Biosignalsplux `plux` module.

    Parameters
    ----------
    dll_path:
        Optional path to the Biosignalsplux API/DLL folder.

    Returns
    -------
    module
        Imported `plux` module.

    Raises
    ------
    BiosignalspluxDependencyError
        If the `plux` module cannot be imported.
    """
    if dll_path:
        dll_dir = Path(dll_path)

        if not dll_dir.exists():
            raise BiosignalspluxDependencyError(
                f"Biosignalsplux DLL path does not exist: {dll_dir}"
            )

        if str(dll_dir) not in sys.path:
            sys.path.insert(0, str(dll_dir))

        if hasattr(__import__("os"), "add_dll_directory"):
            import os

            os.add_dll_directory(str(dll_dir))

    try:
        import plux  # type: ignore
    except ImportError as exc:
        raise BiosignalspluxDependencyError(
            "The Biosignalsplux `plux` module is not available. "
            "Install/configure the Biosignalsplux Python API or provide a valid "
            "DLL path in the acquisition configuration."
        ) from exc

    return plux


@dataclass
class BiosignalspluxBuffer:
    """Thread-safe buffer for sEMG samples."""

    n_channels: int = 2
    max_buffer_samples: int = 10000
    data_buffer: Dict[int, list] = field(default_factory=dict)
    all_data: Dict[int, list] = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock)

    def __post_init__(self) -> None:
        """Initialize channel buffers."""
        if not self.data_buffer:
            self.data_buffer = {idx: [] for idx in range(self.n_channels)}

        if not self.all_data:
            self.all_data = {idx: [] for idx in range(self.n_channels)}

    def append(self, data: Any) -> None:
        """Append one multi-channel sample."""
        with self.lock:
            for idx in range(self.n_channels):
                value = data[idx]
                self.all_data[idx].append(value)
                self.data_buffer[idx].append(value)

                if len(self.data_buffer[idx]) > self.max_buffer_samples:
                    self.data_buffer[idx] = self.data_buffer[idx][-self.max_buffer_samples :]

    def get_buffer(self, clear: bool = True) -> np.ndarray:
        """Return recent buffered data with shape n_channels x n_samples."""
        with self.lock:
            data_copy = {idx: self.data_buffer[idx][:] for idx in self.data_buffer}

            if clear:
                self.data_buffer = {idx: [] for idx in self.data_buffer}

        if not data_copy or len(data_copy[0]) == 0:
            return np.empty((self.n_channels, 0))

        return np.array([data_copy[idx] for idx in range(self.n_channels)])

    def get_all_data(self) -> np.ndarray:
        """Return all acquired data with shape n_channels x n_samples."""
        with self.lock:
            data_copy = {idx: self.all_data[idx][:] for idx in self.all_data}

        if not data_copy or len(data_copy[0]) == 0:
            return np.empty((self.n_channels, 0))

        return np.array([data_copy[idx] for idx in range(self.n_channels)])

    def clear(self) -> None:
        """Clear both recent and full buffers."""
        with self.lock:
            self.data_buffer = {idx: [] for idx in range(self.n_channels)}
            self.all_data = {idx: [] for idx in range(self.n_channels)}


def create_biosignalsplux_device_class(config: BiosignalspluxConfig):
    """Create a Biosignalsplux device class using the available `plux` API.

    This factory avoids importing `plux` at module import time, which keeps the
    public repository testable without hardware dependencies.
    """
    plux = import_plux(config.dll_path)

    class BiosignalspluxEMGDevice(plux.SignalsDev):  # type: ignore[name-defined]
        """Biosignalsplux sEMG acquisition device."""

        def __init__(self) -> None:
            super().__init__()
            self.config = config
            self.frequency = float(config.sampling_rate_hz)
            self.buffer = BiosignalspluxBuffer(n_channels=2)
            self.running = False

        def onRawFrame(self, nSeq, data):  # noqa: N802
            """Handle one raw frame from the Biosignalsplux API."""
            self.buffer.append(data[:2])

            if not self.running:
                return True

            return False

        def start_acquisition(self) -> None:
            """Start hardware acquisition."""
            self.running = True
            self.start(
                int(self.config.sampling_rate_hz),
                int(self.config.channels_mask),
                int(self.config.resolution_bits),
            )
            self.loop()

        def stop_acquisition(self) -> None:
            """Stop hardware acquisition."""
            self.running = False

        def get_buffer(self, clear: bool = True) -> np.ndarray:
            """Return recent buffered sEMG data."""
            return self.buffer.get_buffer(clear=clear)

        def get_all_data(self) -> np.ndarray:
            """Return all acquired sEMG data."""
            return self.buffer.get_all_data()

        def close_resources(self) -> None:
            """Close device resources."""
            self.running = False
            self.close()

    return BiosignalspluxEMGDevice
