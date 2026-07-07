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

Hardware execution will be added progressively after validating each device
wrapper independently.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from motor_intention.acquisition.device_config import load_acquisition_device_config
from motor_intention.acquisition.session_config import (
    AcquisitionSessionConfig,
    build_output_filenames,
)
from motor_intention.acquisition.storage import save_metadata_json
from motor_intention.protocols.trial_protocol import (
    build_trial_list,
    estimate_protocol_duration_sec,
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
        "--execute-hardware",
        action="store_true",
        help="Execute real hardware acquisition. Not enabled yet in this public skeleton.",
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

    trial_list = build_trial_list(
        movement_block=session_config.movement_block,
        total_trials=session_config.total_trials,
        seed=args.seed,
    )

    duration_sec = estimate_protocol_duration_sec(session_config.total_trials)

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
            "mode": "hardware_execution_pending"
            if args.execute_hardware
            else "dry_run_plan",
            "trial_list": trial_list,
            "estimated_duration_sec": duration_sec,
            "device_config": device_config.to_dict(),
            "notes": (
                "This metadata preview does not contain real acquired data. "
                "Hardware execution will be added progressively."
            ),
        }
    )

    if args.write_metadata_preview:
        metadata_path = output_files["metadata"]
        save_metadata_json(metadata, metadata_path)
        print("")
        print(f"Metadata preview saved to: {metadata_path}")

    if args.execute_hardware:
        print("")
        print("Hardware execution is not enabled yet in this public skeleton.")
        print("Next steps will add MindRove, Biosignalsplux, and MYO acquisition blocks.")
        return 2

    print("")
    print("Dry run completed. No real hardware was initialized.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
