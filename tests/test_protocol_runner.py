"""Tests for acquisition protocol runner."""

from motor_intention.acquisition.protocol_runner import (
    ProtocolRunner,
    ProtocolRunnerConfig,
)
from motor_intention.protocols.trial_protocol import estimate_protocol_duration_sec


def test_protocol_runner_non_realtime_generates_events():
    config = ProtocolRunnerConfig(
        movement_block="Codo",
        total_trials=4,
        seed=123,
        realtime=False,
    )

    runner = ProtocolRunner(config=config)
    result = runner.run()

    assert len(result.trial_list) == 4
    assert set(result.trial_list) == {"F", "E"}
    assert len(result.events) > 0
    assert result.estimated_duration_sec == estimate_protocol_duration_sec(4)
    assert result.executed_duration_sec == estimate_protocol_duration_sec(4)
    assert result.realtime is False


def test_protocol_runner_event_callback_receives_events():
    received_events = []

    def callback(time_s, marker, label):
        received_events.append((time_s, marker, label))

    config = ProtocolRunnerConfig(
        movement_block="Hombro",
        total_trials=4,
        seed=123,
        realtime=False,
    )

    runner = ProtocolRunner(
        config=config,
        event_callbacks=[callback],
    )

    result = runner.run()

    assert len(received_events) == len(result.events)
    assert len(received_events) > 0


def test_protocol_runner_realtime_uses_sleep_function():
    sleep_calls = []

    def fake_sleep(duration_sec):
        sleep_calls.append(duration_sec)

    config = ProtocolRunnerConfig(
        movement_block="RotHombro",
        total_trials=2,
        seed=123,
        realtime=True,
        time_scale=0.5,
    )

    runner = ProtocolRunner(
        config=config,
        sleep_fn=fake_sleep,
    )

    result = runner.run()

    assert result.realtime is True
    assert len(sleep_calls) > 0
    assert all(duration > 0 for duration in sleep_calls)
