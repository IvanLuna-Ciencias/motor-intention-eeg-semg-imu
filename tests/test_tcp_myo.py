"""Tests for MYO TCP communication utilities."""

import json
import socket
import time

from motor_intention.communication.tcp_myo import MyoReceiverConfig, MyoTCPReceiver


def _send_json_line(host, port, payload):
    with socket.create_connection((host, port), timeout=2.0) as client:
        # Receive START command from server.
        client.recv(1024)

        client.sendall((json.dumps(payload) + "\n").encode("utf-8"))
        time.sleep(0.05)


def test_myo_tcp_receiver_receives_json_message():
    config = MyoReceiverConfig(host="127.0.0.1", port=9998)
    receiver = MyoTCPReceiver(config=config)

    receiver.start()
    time.sleep(0.1)

    payload = {
        "emg": [1, 2, 3, 4, 5, 6, 7, 8],
        "orientation": [1, 0, 0, 0],
        "imu": {
            "accelerometer": [0, 0, 1],
            "gyroscope": [0, 0, 0],
        },
        "pose": "rest",
        "rssi": -55,
    }

    _send_json_line("127.0.0.1", 9998, payload)
    time.sleep(0.1)

    messages = receiver.get_messages()
    receiver.stop()

    assert len(messages) == 1
    assert messages[0]["emg"] == [1, 2, 3, 4, 5, 6, 7, 8]
    assert messages[0]["pose"] == "rest"
    assert "timestamp_received_s" in messages[0]
    assert "timestamp_rel" in messages[0]


def test_myo_tcp_receiver_clear_buffer():
    config = MyoReceiverConfig(host="127.0.0.1", port=9997)
    receiver = MyoTCPReceiver(config=config)

    receiver.start()
    time.sleep(0.1)

    payload = {"emg": [0] * 8, "pose": "rest"}

    _send_json_line("127.0.0.1", 9997, payload)
    time.sleep(0.1)

    assert len(receiver.get_messages()) == 1

    receiver.clear()

    assert receiver.get_messages() == []

    receiver.stop()
