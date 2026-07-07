# Synthetic acquisition demo

This document describes the complete synthetic acquisition demo included in the public repository.

The demo simulates a full multimodal acquisition session without requiring real EEG, sEMG, MYO, LabVIEW, or cRIO hardware.

## Purpose

The purpose of this demo is to verify the public acquisition structure using synthetic data only.

It demonstrates:

- Session configuration.
- Device configuration loading.
- Trial protocol generation.
- Synthetic EEG signal generation.
- Synthetic sEMG signal generation.
- Synthetic MYO-like message generation.
- Event marker generation.
- Metadata creation.
- Standardized output file naming.

## Script

The demo script is located at:

~~~text
scripts/acquisition/run_synthetic_acquisition_demo.py
~~~

## Run the demo

From the repository root, run:

~~~bash
python scripts/acquisition/run_synthetic_acquisition_demo.py
~~~

By default, the script generates a synthetic session for:

~~~text
subject_id: sub-synthetic001
session_id: ses-01
movement_block: Codo
total_trials: 4
~~~

## Output folder

The generated files are stored in:

~~~text
outputs/acquisition/sub-synthetic001/ses-01/Codo/
~~~

Expected files:

~~~text
sub-synthetic001_ses-01_Codo_20260706_120000_eeg.csv
sub-synthetic001_ses-01_Codo_20260706_120000_semg.csv
sub-synthetic001_ses-01_Codo_20260706_120000_myo.csv
sub-synthetic001_ses-01_Codo_20260706_120000_events.csv
sub-synthetic001_ses-01_Codo_20260706_120000_metadata.json
~~~

## Custom options

The script supports command-line options:

~~~bash
python scripts/acquisition/run_synthetic_acquisition_demo.py --help
~~~

Example:

~~~bash
python scripts/acquisition/run_synthetic_acquisition_demo.py --movement-block Hombro --total-trials 6
~~~

Valid movement blocks are:

~~~text
Codo
Hombro
RotHombro
~~~

## Data policy

The generated files are synthetic only.

They do not contain:

- Real participant data.
- Consent information.
- Identifiable metadata.
- Private institutional data.
- Raw experimental recordings.

## Git policy

The `outputs/` folder is ignored by Git and should not be committed.

This demo is intended for local testing and reproducibility of the repository structure.
