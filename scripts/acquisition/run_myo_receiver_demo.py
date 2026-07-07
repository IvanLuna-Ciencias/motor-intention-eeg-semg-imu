"""Run a demo MYO TCP receiver.

This script starts the public MYO TCP receiver and optionally saves received
synthetic MYO messages to a CSV file.

It is intended for testing the MYO bridge without the real MYO Armband.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from motor_intention.acquisition.storage import save_myo_csv
from motor_intention.communication.tcp_myo import MyoReceiverConfig, MyoTCPReceiver


def main() -> int:
    parser = argparse.ArgumentParser(description="Run demo MYO TCP receiver.")
    parser.add_argument("--host", default="127.0.0.1", help="Receiver host.")
    parser.add_argument("--port", type=int, default=9999, help="Receiver port.")
    parser.add_argument(
        "--duration-sec",
        type=float,
        default=15.0,
        help="Maximum receiver duration in seconds.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "data" / "sample" / "synthetic_myo_from_tcp.csv",
        help="Output CSV file for received MYO messages.",
    )

    args = parser.parse_args()

    config = MyoReceiverConfig(host=args.host, port=args.port)
    receiver = MyoTCPReceiver(config=config)

    print(f"Starting MYO TCP receiver at {args.host}:{args.port}")
    receiver.start()

    start_time = time.perf_counter()

    try:
        while time.perf_counter() - start_time < args.duration_sec:
            if not receiver.is_running:
                break

            messages = receiver.get_messages()
            print(f"\rReceived messages: {len(messages)}", end="")
            time.sleep(0.25)

    except KeyboardInterrupt:
        print("\nReceiver interrupted by user.")

    finally:
        receiver.stop()
        messages = receiver.get_messages()
        print(f"\nFinal received messages: {len(messages)}")

        if messages:
            output_path = save_myo_csv(messages, args.output)
            print(f"Saved received MYO messages to: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
