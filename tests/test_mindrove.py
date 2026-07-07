"""Tests for MindRove acquisition wrapper."""

import numpy as np
import pytest

from motor_intention.acquisition.device_config import MindRoveConfig
from motor_intention.acquisition.mindrove import (
    MindRoveDependencyError,
    MindRoveEEGDevice,
    import_mindrove_modules,
)


class FakeMindRoveBoard:
    """Minimal fake board used for wrapper tests."""

    def __init__(self):
        self.prepared = False
        self.streaming = False
        self.released = False
        self.markers = []

    def prepare_session(self):
        self.prepared = True

    def start_stream(self):
        self.streaming = True

    def stop_stream(self):
        self.streaming = False

    def release_session(self):
        self.released = True

    def get_current_board_data(self, n_points):
        return np.zeros((6, n_points))

    def get_board_data(self):
        return np.ones((6, 10))

    def insert_marker(self, marker):
        self.markers.append(marker)

    def get_sampling_rate(self):
        return 500.0

    def get_eeg_channels(self):
        return [0, 1, 2, 3, 4, 5]


def test_mindrove_wrapper_with_fake_board():
    board = FakeMindRoveBoard()
    config = MindRoveConfig(connection_mode="WiFi")

    device = MindRoveEEGDevice(config=config, board=board)

    device.prepare()
    device.start_stream()
    current_data = device.get_current_data(20)
    all_data = device.get_all_data()
    device.insert_marker(88.0)
    device.stop_stream()
    device.release()

    assert board.prepared is True
    assert board.released is True
    assert device.is_streaming is False
    assert current_data.shape == (6, 20)
    assert all_data.shape == (6, 10)
    assert board.markers == [88.0]


def test_mindrove_sampling_and_channels_with_fake_board():
    board = FakeMindRoveBoard()
    config = MindRoveConfig(connection_mode="WiFi")

    device = MindRoveEEGDevice(config=config, board=board)

    assert device.get_sampling_rate_hz() == 500.0
    assert device.get_eeg_channels() == [0, 1, 2, 3, 4, 5]


def test_mindrove_bluetooth_requires_mac_address():
    with pytest.raises(ValueError):
        MindRoveEEGDevice(
            config=MindRoveConfig(connection_mode="Bluetooth", mac_address=""),
            board=FakeMindRoveBoard(),
        )


def test_import_mindrove_modules_dependency_error_or_success():
    try:
        modules = import_mindrove_modules()
    except MindRoveDependencyError:
        assert True
    else:
        assert hasattr(modules, "BoardShim")
        assert hasattr(modules, "MindRoveInputParams")
