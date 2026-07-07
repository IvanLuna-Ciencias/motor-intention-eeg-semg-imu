"""Tests for Biosignalsplux acquisition wrapper."""

import numpy as np
import pytest

from motor_intention.acquisition.biosignalsplux import (
    BiosignalspluxBuffer,
    BiosignalspluxDependencyError,
    import_plux,
)


def test_biosignalsplux_buffer_append_and_get():
    buffer = BiosignalspluxBuffer(n_channels=2)

    buffer.append([1.0, 2.0])
    buffer.append([3.0, 4.0])

    data = buffer.get_buffer()

    assert isinstance(data, np.ndarray)
    assert data.shape == (2, 2)
    assert data[0].tolist() == [1.0, 3.0]
    assert data[1].tolist() == [2.0, 4.0]


def test_biosignalsplux_buffer_clear():
    buffer = BiosignalspluxBuffer(n_channels=2)

    buffer.append([1.0, 2.0])
    buffer.clear()

    assert buffer.get_buffer().shape == (2, 0)
    assert buffer.get_all_data().shape == (2, 0)


def test_import_plux_invalid_path_raises():
    with pytest.raises(BiosignalspluxDependencyError):
        import_plux("this/path/does/not/exist")
