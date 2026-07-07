"""Run real multimodal acquisition for training data collection.

This is the public-safe entry point intended to replace the original monolithic
thesis acquisition scripts.

Current scope:
- Load acquisition YAML configuration.
- Create anonymized session configuration.
- Build trial protocol.
- Build standardized output filenames.
- Generate a dry-run acquisition plan.
- Optionally write metadata preview.
- Optionally run a MindRove EEG smoke test when explicitly requested.

Full hardware protocol execution will be added progressively after validating
each device wrapper independently.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from motor_intention.acquisition.device_config import (
    AcquisitionDeviceConfig,
    load_acquisition_device_config,
)
from motor_intention.acquisition.biosignalsplux import (
    BiosignalspluxDependencyError,
    create_biosignalsplux_device_class,
)
from motor_intention.acquisition.mindrove import (
    MindRoveDependencyError,
    MindRoveEEGDevice,
)
from motor_intention.acquisition.session_config import (
    AcquisitionSessionConfig,
    build_output_filenames,
)
from motor_intention.acquisition.storage import save_events_csv, save_metadata_json
from motor_intention.communication.tcp_myo import MyoReceiverConfig, MyoTCPReceiver
from motor_intention.protocols.event_markers import (
    MANUAL_STOP_MARKER,
    START_PROTOCOL_MARKER,
)
from motor_intention.acquisition.protocol_runner import (
    ProtocolRunner,
    ProtocolRunnerConfig,
)


DEFAULT_CONFIG = PROJECT_ROOT / "configs" / "acquisition" / "acquisition.example.yaml"


def build_acquisition_plan(
    session_config: AcquisitionSessionConfig,
    output_files: Dict[str, Path],
    trial_list: List[str],
    duration_sec: float,
) -> Dict[str, object]:
    """Build a public-safe acquisition execution plan."""
    return {
        "subject_id": session_config.subject_id,
        "session_id": session_config.session_id,
        "movement_block": session_config.movement_block,
        "total_trials": session_config.total_trials,
        "estimated_duration_sec": duration_sec,
        "trial_list": trial_list,
        "output_folder": str(output_files["folder"]),
        "output_files": {
            key: str(value)
            for key, value in output_files.items()
            if key != "folder"
        },
    }


def print_acquisition_plan(plan: Dict[str, object]) -> None:
    """Print acquisition plan in a readable form."""
    print("Acquisition training plan")
    print("-------------------------")
    print(f"Subject ID:          {plan['subject_id']}")
    print(f"Session ID:          {plan['session_id']}")
    print(f"Movement block:      {plan['movement_block']}")
    print(f"Total trials:        {plan['total_trials']}")
    print(f"Estimated duration:  {plan['estimated_duration_sec']} s")
    print(f"Output folder:       {plan['output_folder']}")
    print("")
    print("Trial list:")
    print(f"  {plan['trial_list']}")
    print("")
    print("Output files:")

    output_files = plan["output_files"]
    assert isinstance(output_files, dict)

    for key, value in output_files.items():
        print(f"  {key}: {value}")


def run_myo_receiver_smoke_test(
    device_config: AcquisitionDeviceConfig,
    duration_sec: float,
    port_override: int | None = None,
) -> Dict[str, object]:
    """Run a short MYO TCP receiver smoke test.

    This smoke test starts the TCP receiver briefly and then closes it safely.
    It does not require the real MYO Armband.
    """
    print("")
    print("MYO TCP receiver smoke test")
    print("---------------------------")

    receiver_port = (
        port_override
        if port_override is not None
        else device_config.myo.receiver_port
    )

    receiver_config = MyoReceiverConfig(
        host=device_config.myo.receiver_host,
        port=receiver_port,
    )

    receiver = MyoTCPReceiver(config=receiver_config)

    print(f"Starting MYO TCP receiver at {receiver_config.host}:{receiver_config.port}")
    receiver.start()

    try:
        time.sleep(duration_sec)
        messages = receiver.get_messages()

        print(f"Receiver duration: {duration_sec} s")
        print(f"Received messages: {len(messages)}")

        return {
            "myo_receiver_smoke_test": "completed",
            "myo_receiver_host": receiver_config.host,
            "myo_receiver_port": receiver_config.port,
            "myo_receiver_duration_sec": duration_sec,
            "myo_receiver_messages": len(messages),
        }

    finally:
        print("Stopping MYO TCP receiver...")
        receiver.stop()


def run_biosignalsplux_smoke_test(
    device_config: AcquisitionDeviceConfig,
) -> Dict[str, object]:
    """Run a short Biosignalsplux sEMG smoke test.

    This smoke test validates that the Biosignalsplux API can be imported and
    that a device class can be created from the public configuration.

    Full streaming will be added after validating the hardware-specific API
    behavior on the acquisition computer.
    """
    print("")
    print("Biosignalsplux sEMG smoke test")
    print("------------------------------")

    device_class = create_biosignalsplux_device_class(
        config=device_config.biosignalsplux,
    )

    print("Biosignalsplux device class created successfully.")
    print(f"Sampling rate: {device_config.biosignalsplux.sampling_rate_hz} Hz")
    print(f"Channels mask: {device_config.biosignalsplux.channels_mask}")
    print(f"Resolution:    {device_config.biosignalsplux.resolution_bits} bits")

    return {
        "biosignalsplux_smoke_test": "completed",
        "biosignalsplux_device_class": device_class.__name__,
        "biosignalsplux_sampling_rate_hz": (
            device_config.biosignalsplux.sampling_rate_hz
        ),
        "biosignalsplux_channels_mask": device_config.biosignalsplux.channels_mask,
        "biosignalsplux_resolution_bits": (
            device_config.biosignalsplux.resolution_bits
        ),
    }


def run_mindrove_smoke_test(
    device_config: AcquisitionDeviceConfig,
    n_points: int,
    stream_duration_sec: float,
) -> Dict[str, object]:
    """Run a short MindRove EEG smoke test."""
    print("")
    print("MindRove EEG smoke test")
    print("-----------------------")

    device = MindRoveEEGDevice(config=device_config.mindrove)

    try:
        print("Preparing MindRove session...")
        device.prepare()

        sampling_rate_hz = device.get_sampling_rate_hz()
        eeg_channels = device.get_eeg_channels()

        print(f"Sampling rate: {sampling_rate_hz} Hz")
        print(f"EEG channels:  {eeg_channels}")

        print("Starting EEG stream...")
        device.start_stream()

        print(f"Inserting START marker: {START_PROTOCOL_MARKER}")
        device.insert_marker(START_PROTOCOL_MARKER)

        time.sleep(stream_duration_sec)

        preview_data = device.get_current_data(n_points)

        print(f"Inserting STOP marker: {MANUAL_STOP_MARKER}")
        device.insert_marker(MANUAL_STOP_MARKER)

        print(f"Preview data shape: {preview_data.shape}")

        return {
            "mindrove_smoke_test": "completed",
            "mindrove_sampling_rate_hz": sampling_rate_hz,
            "mindrove_eeg_channels": eeg_channels,
            "mindrove_preview_shape": list(preview_data.shape),
            "mindrove_stream_duration_sec": stream_duration_sec,
            "mindrove_preview_n_points": n_points,
        }

    finally:
        print("Closing MindRove session...")
        device.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run real multimodal acquisition for training data collection."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to acquisition YAML configuration.",
    )
    parser.add_argument(
        "--subject-id",
        required=True,
        help="Anonymized subject identifier, for example sub-001.",
    )
    parser.add_argument(
        "--session-id",
        required=True,
        help="Anonymized session identifier, for example ses-01.",
    )
    parser.add_argument(
        "--movement-block",
        required=True,
        choices=["Codo", "Hombro", "RotHombro"],
        help="Movement block to acquire.",
    )
    parser.add_argument(
        "--total-trials",
        type=int,
        default=40,
        help="Total number of trials. Must be even.",
    )
    parser.add_argument(
        "--timestamp",
        default=None,
        help="Optional fixed timestamp for reproducible filenames.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=123,
        help="Random seed for balanced trial order.",
    )
    parser.add_argument(
        "--write-metadata-preview",
        action="store_true",
        help="Write a metadata preview JSON file without acquiring real data.",
    )
    parser.add_argument(
        "--write-events-preview",
        action="store_true",
        help="Write a protocol events preview CSV file without acquiring real data.",
    )
    parser.add_argument(
        "--execute-hardware",
        action="store_true",
        help="Execute explicitly selected hardware blocks.",
    )
    parser.add_argument(
        "--use-mindrove",
        action="store_true",
        help="Run a short MindRove EEG smoke test. Requires --execute-hardware.",
    )
    parser.add_argument(
        "--use-biosignalsplux",
        action="store_true",
        help="Run a short Biosignalsplux sEMG smoke test. Requires --execute-hardware.",
    )
    parser.add_argument(
        "--use-myo-receiver",
        action="store_true",
        help="Run a short MYO TCP receiver smoke test. Requires --execute-hardware.",
    )
    parser.add_argument(
        "--myo-receiver-sec",
        type=float,
        default=1.0,
        help="MYO TCP receiver smoke test duration in seconds.",
    )
    parser.add_argument(
        "--myo-receiver-port",
        type=int,
        default=None,
        help="Optional temporary MYO receiver port override for testing.",
    )
    parser.add_argument(
        "--mindrove-preview-points",
        type=int,
        default=250,
        help="Number of EEG points to read during MindRove smoke test.",
    )
    parser.add_argument(
        "--mindrove-stream-sec",
        type=float,
        default=1.0,
        help="MindRove smoke test stream duration in seconds.",
    )

    args = parser.parse_args()

    device_config = load_acquisition_device_config(args.config)

    session_config = AcquisitionSessionConfig(
        subject_id=args.subject_id,
        session_id=args.session_id,
        movement_block=args.movement_block,
        total_trials=args.total_trials,
        feedback_mode="Visual",
        eeg_filter="Configured externally",
        semg_filter="Configured externally",
        connection_mode=device_config.mindrove.connection_mode,
        timestamp=args.timestamp,
    )

    output_files = build_output_filenames(
        config=session_config,
        output_root=PROJECT_ROOT / device_config.output_root,
    )

    protocol_runner = ProtocolRunner(
        config=ProtocolRunnerConfig(
            movement_block=session_config.movement_block,
            total_trials=session_config.total_trials,
            seed=args.seed,
            realtime=False,
        )
    )

    protocol_result = protocol_runner.run()
    trial_list = protocol_result.trial_list
    event_rows = protocol_result.events
    duration_sec = protocol_result.estimated_duration_sec

    plan = build_acquisition_plan(
        session_config=session_config,
        output_files=output_files,
        trial_list=trial_list,
        duration_sec=duration_sec,
    )

    print_acquisition_plan(plan)

    metadata = session_config.to_metadata()
    metadata.update(
        {
            "entry_point": "scripts/acquisition/run_acquisition_training.py",
            "mode": "hardware_execution"
            if args.execute_hardware
            else "dry_run_plan",
            "trial_list": trial_list,
            "estimated_duration_sec": duration_sec,
            "protocol_event_count": len(event_rows),
            "device_config": device_config.to_dict(),
            "selected_hardware_blocks": {
                "mindrove": args.use_mindrove,
                "biosignalsplux": args.use_biosignalsplux,
                "myo_tcp_receiver": args.use_myo_receiver,
            },
            "notes": (
                "This metadata preview does not contain real acquired data. "
                "Full protocol execution will be added progressively."
            ),
        }
    )

    if args.write_metadata_preview:
        metadata_path = output_files["metadata"]
        save_metadata_json(metadata, metadata_path)
        print("")
        print(f"Metadata preview saved to: {metadata_path}")

    if args.write_events_preview:
        events_path = output_files["events"]
        save_events_csv(event_rows, events_path)
        print("")
        print(f"Events preview saved to: {events_path}")

    if not args.execute_hardware:
        print("")
        print("Dry run completed. No real hardware was initialized.")
        return 0

    if (
        args.execute_hardware
        and not args.use_mindrove
        and not args.use_biosignalsplux
        and not args.use_myo_receiver
    ):
        print("")
        print("Hardware execution was requested, but no hardware block was selected.")
        print("Use --use-mindrove, --use-biosignalsplux, or --use-myo-receiver to run a smoke test.")
        return 2

    if args.use_mindrove:
        try:
            mindrove_result = run_mindrove_smoke_test(
                device_config=device_config,
                n_points=args.mindrove_preview_points,
                stream_duration_sec=args.mindrove_stream_sec,
            )
            metadata.update(mindrove_result)

        except MindRoveDependencyError as exc:
            print("")
            print("MindRove smoke test could not run.")
            print(str(exc))
            return 3

    if args.use_biosignalsplux:
        try:
            biosignalsplux_result = run_biosignalsplux_smoke_test(
                device_config=device_config,
            )
            metadata.update(biosignalsplux_result)

        except BiosignalspluxDependencyError as exc:
            print("")
            print("Biosignalsplux smoke test could not run.")
            print(str(exc))
            return 4

    if args.use_myo_receiver:
        myo_result = run_myo_receiver_smoke_test(
            device_config=device_config,
            duration_sec=args.myo_receiver_sec,
            port_override=args.myo_receiver_port,
        )
        metadata.update(myo_result)

    print("")
    print("Selected hardware block execution completed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())