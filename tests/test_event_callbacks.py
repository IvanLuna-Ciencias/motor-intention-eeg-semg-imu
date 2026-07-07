"""Tests for acquisition event callbacks."""

from motor_intention.acquisition.event_callbacks import (
    DeviceMarkerCallback,
    ProtocolEventRecorder,
)
from motor_intention.acquisition.protocol_runner import (
    ProtocolRunner,
    ProtocolRunnerConfig,
)


class FakeMarkerDevice:
    def __init__(self):
        self.markers = []

    def insert_marker(self, marker):
        self.markers.append(marker)


def test_protocol_event_recorder_records_events():
    recorder = ProtocolEventRecorder()

    recorder(0.0, 88.0, "START")
    recorder(1.0, 10.0, "Phase:alert")

    assert recorder.as_event_rows() == [
        (0.0, 88.0, "START"),
        (1.0, 10.0, "Phase:alert"),
    ]

    recorder.clear()

    assert recorder.as_event_rows() == []


def test_device_marker_callback_forwards_markers():
    device = FakeMarkerDevice()
    callback = DeviceMarkerCallback(device=device)

    callback(0.0, 88.0, "START")
    callback(1.0, 99.0, "STOP")

    assert device.markers == [88.0, 99.0]
    assert callback.inserted_markers == [88.0, 99.0]


def test_protocol_runner_with_recorder_and_marker_callback():
    recorder = ProtocolEventRecorder()
    device = FakeMarkerDevice()
    marker_callback = DeviceMarkerCallback(device=device)

    runner = ProtocolRunner(
        config=ProtocolRunnerConfig(
            movement_block="Codo",
            total_trials=2,
            seed=123,
            realtime=False,
        ),
        event_callbacks=[recorder, marker_callback],
    )

    result = runner.run()

    assert len(recorder.as_event_rows()) == len(result.events)
    assert len(device.markers) == len(result.events)
    assert device.markers == marker_callback.inserted_markers
