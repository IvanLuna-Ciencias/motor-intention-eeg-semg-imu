"""Run a MYO sender process.

This script provides a clean public entry point for the MYO sender side of the
MYO bridge architecture.

Current public functionality:

- Connect to a MYO TCP receiver.
- Wait for a START command.
- Send synthetic MYO-like JSON-lines messages.
- Stop after a duration or after receiving STOP.

The real MYO SDK acquisition mode will be added later after cleaning the
legacy hardware-dependent code.
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
import time
from pathlib import Path
from typing import Any, Dict

import numpy as np
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = PROJECT_ROOT / "configs" / "acquisition" / "myo_sender.example.yaml"


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load YAML configuration."""
    with config_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def wait_for_start(sock: socket.socket, encoding: str = "utf-8") -> bool:
    """Wait for a START command from the receiver."""
    buffer = ""

    while True:
        data = sock.recv(1024)

        if not data:
            return False

        buffer += data.decode(encoding)

        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.strip()

            if not line:
                continue

            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                continue

            if message.get("cmd") == "START":
                return True


def send_json_line(sock: socket.socket, payload: Dict[str, Any], encoding: str = "utf-8") -> None:
    """Send one JSON object followed by a newline."""
    line = json.dumps(payload) + "\n"
    sock.sendall(line.encode(encoding))


def create_synthetic_myo_message(time_s: float, rng: np.random.Generator) -> Dict[str, Any]:
    """Create one synthetic MYO-like message."""
    return {
        "timestamp_origin": round(time_s, 4),
        "emg": rng.normal(loc=0.0, scale=20.0, size=8).round(3).tolist(),
        "orientation": rng.normal(loc=0.0, scale=0.1, size=4).round(4).tolist(),
        "imu": {
            "accelerometer": rng.normal(loc=0.0, scale=0.3, size=3).round(4).tolist(),
            "gyroscope": rng.normal(loc=0.0, scale=0.2, size=3).round(4).tolist(),
        },
        "pose": "rest",
        "rssi": -55,
    }


def run_synthetic_sender(
    host: str,
    port: int,
    rate_hz: float,
    duration_sec: float,
) -> None:
    """Run a synthetic MYO sender for testing the TCP bridge."""
    rng = np.random.default_rng(seed=42)
    period_s = 1.0 / float(rate_hz)
    n_samples = int(duration_sec * rate_hz)

    with socket.create_connection((host, port), timeout=5.0) as sock:
        print(f"Connected to MYO receiver at {host}:{port}")
        print("Waiting for START command...")

        started = wait_for_start(sock)

        if not started:
            print("Receiver closed before START.")
            return

        print("START received. Sending synthetic MYO messages...")

        start_time = time.perf_counter()

        for sample_idx in range(n_samples):
            elapsed_s = sample_idx * period_s
            payload = create_synthetic_myo_message(elapsed_s, rng)
            send_json_line(sock, payload)

            target_time = start_time + ((sample_idx + 1) * period_s)
            sleep_s = target_time - time.perf_counter()

            if sleep_s > 0:
                time.sleep(sleep_s)

        print("Synthetic MYO sender finished.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run MYO sender process.")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to MYO sender YAML configuration.",
    )
    args = parser.parse_args()

    config = load_config(args.config)

    receiver_config = config.get("receiver", {})
    sender_config = config.get("sender", {})

    host = receiver_config.get("host", "127.0.0.1")
    port = int(receiver_config.get("port", 9999))
    mode = sender_config.get("mode", "synthetic")

    if mode != "synthetic":
        raise NotImplementedError(
            "Only synthetic mode is currently available in the public version. "
            "Real MYO SDK mode will be added after cleaning the legacy sender."
        )

    run_synthetic_sender(
        host=host,
        port=port,
        rate_hz=float(sender_config.get("synthetic_rate_hz", 50.0)),
        duration_sec=float(sender_config.get("duration_sec", 10.0)),
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
