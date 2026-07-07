"""MindRove EEG acquisition wrapper.

This module provides a clean wrapper for MindRove EEG acquisition.

The public repository should remain importable and testable even when the
hardware-specific MindRove package is not installed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import numpy as np

from motor_intention.acquisition.device_config import MindRoveConfig


class MindRoveDependencyError(ImportError):
    """Raised when the MindRove Python API is not available."""


@dataclass(frozen=True)
class MindRoveModules:
    """Container for MindRove API modules/classes."""

    BoardShim: Any
    MindRoveInputParams: Any
    BoardIds: Any
    DataFilter: Any
    FilterTypes: Any
    DetrendOperations: Any


def import_mindrove_modules() -> MindRoveModules:
    """Import MindRove hardware-specific modules lazily."""
    try:
        from mindrove.board_shim import BoardIds, BoardShim, MindRoveInputParams
        from mindrove.data_filter import DataFilter, DetrendOperations, FilterTypes
    except ImportError as exc:
        raise MindRoveDependencyError(
            "The MindRove Python package is not available. "
            "Install/configure the MindRove API before using real EEG acquisition."
        ) from exc

    return MindRoveModules(
        BoardShim=BoardShim,
        MindRoveInputParams=MindRoveInputParams,
        BoardIds=BoardIds,
        DataFilter=DataFilter,
        FilterTypes=FilterTypes,
        DetrendOperations=DetrendOperations,
    )


class MindRoveEEGDevice:
    """Clean MindRove EEG device wrapper.

    This class can wrap a real MindRove BoardShim instance or a fake board
    object during tests.
    """

    def __init__(
        self,
        config: MindRoveConfig,
        board: Optional[Any] = None,
        modules: Optional[MindRoveModules] = None,
    ) -> None:
        self.config = config
        self.config.validate()

        self.modules = modules
        self.board = board
        self.board_id: Optional[Any] = None
        self.is_streaming = False

        if self.board is None:
            self.modules = self.modules or import_mindrove_modules()
            self.board = self._create_board()

    def _create_board(self) -> Any:
        """Create a MindRove BoardShim instance from configuration."""
        if self.modules is None:
            raise MindRoveDependencyError("MindRove modules were not loaded.")

        input_params = self.modules.MindRoveInputParams()

        if self.config.connection_mode == "Bluetooth":
            input_params.mac_address = self.config.mac_address

        # The original thesis-associated implementation used the WiFi board ID.
        self.board_id = self.modules.BoardIds.MINDROVE_WIFI_BOARD

        return self.modules.BoardShim(self.board_id, input_params)

    def prepare(self) -> None:
        """Prepare the EEG acquisition session."""
        self.board.prepare_session()

        if self.board_id is None and hasattr(self.board, "get_board_id"):
            self.board_id = self.board.get_board_id()

    def start_stream(self) -> None:
        """Start EEG streaming."""
        self.board.start_stream()
        self.is_streaming = True

    def stop_stream(self) -> None:
        """Stop EEG streaming."""
        try:
            self.board.stop_stream()
        finally:
            self.is_streaming = False

    def release(self) -> None:
        """Release the EEG acquisition session."""
        self.board.release_session()
        self.is_streaming = False

    def close(self) -> None:
        """Stop streaming and release resources safely."""
        try:
            if self.is_streaming:
                self.stop_stream()
        finally:
            self.release()

    def get_current_data(self, n_points: int) -> np.ndarray:
        """Return the most recent EEG board data."""
        return np.asarray(self.board.get_current_board_data(n_points))

    def get_all_data(self) -> np.ndarray:
        """Return all buffered EEG board data."""
        return np.asarray(self.board.get_board_data())

    def insert_marker(self, marker: float) -> None:
        """Insert a marker into the EEG stream."""
        self.board.insert_marker(marker)

    def get_sampling_rate_hz(self) -> float:
        """Return the EEG board sampling rate."""
        if self.modules is not None and self.board_id is not None:
            return float(self.modules.BoardShim.get_sampling_rate(self.board_id))

        if hasattr(self.board, "get_sampling_rate"):
            return float(self.board.get_sampling_rate())

        raise AttributeError("Sampling rate is not available for this board.")

    def get_eeg_channels(self) -> list[int]:
        """Return EEG channel indices."""
        if self.modules is not None and self.board_id is not None:
            return list(self.modules.BoardShim.get_exg_channels(self.board_id))

        if hasattr(self.board, "get_eeg_channels"):
            return list(self.board.get_eeg_channels())

        raise AttributeError("EEG channels are not available for this board.")
