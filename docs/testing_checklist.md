# Testing checklist

This document summarizes basic checks for the public repository.

## Acquisition modules

The acquisition-related modules currently included in the public repository are hardware-independent.

They include:

~~~text
src/motor_intention/protocols/event_markers.py
src/motor_intention/protocols/trial_protocol.py
src/motor_intention/acquisition/storage.py
src/motor_intention/communication/tcp_myo.py
scripts/acquisition/create_synthetic_acquisition_sample.py
~~~

## Synthetic acquisition sample

To generate synthetic EEG, sEMG, MYO, event, and metadata files, run:

~~~bash
python scripts/acquisition/create_synthetic_acquisition_sample.py
~~~

The generated files are stored in:

~~~text
data/sample/
~~~

Expected files:

~~~text
synthetic_eeg.csv
synthetic_semg_biosignals.csv
synthetic_myo.csv
synthetic_events.csv
example_metadata.json
~~~

These files are synthetic only and do not contain real participant data.

## Running tests

Install development dependencies:

~~~bash
pip install -r requirements-dev.txt
~~~

Run tests:

~~~bash
pytest
~~~

Expected result:

~~~text
11 passed
~~~

## Current scope

The current tests verify:

- Experimental event markers.
- Movement block definitions.
- Randomized balanced trial generation.
- Protocol start and stop events.
- Protocol duration estimation.
- EEG CSV saving.
- sEMG CSV saving.
- MYO CSV saving.
- Event CSV saving.
- Metadata JSON saving.

## Hardware-dependent scripts

The following legacy scripts are not yet part of the public package:

~~~text
myo_sender.py
myo_receiver.py
main_acquisition.py
main_acquisition_LV.py
main_acquisition_LV_FINALES.py
~~~

They will be migrated later after removing:

- Local paths.
- Private model paths.
- Device-specific SDK paths.
- Hardcoded IP addresses.
- Participant-identifiable fields.
- Mixed acquisition/classification/robot-control logic.

## MYO sender script check

The public MYO sender entry point can be checked without hardware by running:

~~~bash
python scripts/acquisition/run_myo_sender.py --help
~~~

This command should display the script options without connecting to the MYO Armband.
