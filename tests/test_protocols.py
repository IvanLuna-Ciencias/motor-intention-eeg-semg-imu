"""Tests for hardware-independent protocol utilities."""

from motor_intention.protocols.event_markers import (
    MANUAL_STOP_MARKER,
    PHASE_MARKERS,
    START_PROTOCOL_MARKER,
    get_block_movements,
    get_movement_display_name,
    get_phase_marker,
)
from motor_intention.protocols.trial_protocol import (
    TrialProtocol,
    build_trial_list,
    estimate_protocol_duration_sec,
)


def test_phase_markers():
    assert get_phase_marker("alert") == 10.0
    assert get_phase_marker("prep") == 11.0
    assert get_phase_marker("execute") == 12.0
    assert get_phase_marker("hold") == 13.0
    assert get_phase_marker("rest") == 14.0
    assert START_PROTOCOL_MARKER == 88.0
    assert MANUAL_STOP_MARKER == 99.0
    assert set(PHASE_MARKERS.keys()) == {"alert", "prep", "execute", "hold", "rest"}


def test_movement_blocks():
    assert get_block_movements("Codo") == ("F", "E")
    assert get_block_movements("Hombro") == ("FH", "EH")
    assert get_block_movements("RotHombro") == ("RInt", "RExt")
    assert get_movement_display_name("F") == "FLEXIÓN CODO"


def test_build_trial_list_is_balanced():
    trials = build_trial_list("Codo", total_trials=10, seed=123)

    assert len(trials) == 10
    assert trials.count("F") == 5
    assert trials.count("E") == 5


def test_protocol_start_and_stop_events():
    trials = build_trial_list("Codo", total_trials=2, seed=1)
    protocol = TrialProtocol(trial_list=trials)

    start_event = protocol.start(time_s=0.0)
    stop_event = protocol.stop(time_s=10.0)

    assert start_event.marker == 88.0
    assert stop_event.marker == 99.0
    assert protocol.is_finished is True
    assert len(protocol.events) == 2


def test_protocol_duration_estimate():
    duration = estimate_protocol_duration_sec(total_trials=4)

    assert duration == 32.0
