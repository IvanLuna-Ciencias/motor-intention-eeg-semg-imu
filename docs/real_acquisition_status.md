# Real acquisition status

This document summarizes the current status of the real acquisition entry point.

## Branch

Current development branch:

~~~text
feature/real-acquisition-entrypoint
~~~

## Main entry point

~~~text
scripts/acquisition/run_acquisition_training.py
~~~

## Current scope

The current entry point supports:

- Public-safe dry-run acquisition planning.
- YAML acquisition configuration loading.
- Anonymized session configuration.
- Balanced trial list generation.
- Standardized output filename generation.
- Optional metadata preview.
- Optional hardware smoke tests.

## Available modes

### Dry run

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4
~~~

This mode does not initialize hardware.

### Metadata preview

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4 --write-metadata-preview
~~~

This writes a metadata preview under:

~~~text
outputs/acquisition/
~~~

The `outputs/` folder is ignored by Git.

## Hardware smoke tests

Hardware blocks are disabled by default.

To run any hardware-related block, the `--execute-hardware` flag must be used together with the specific hardware flag.

## MindRove EEG smoke test

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-mindrove
~~~

Current status:

- Prepares MindRove session.
- Starts EEG stream.
- Inserts START marker.
- Reads a short EEG preview.
- Inserts STOP marker.
- Closes the session safely.

Pending:

- Validate with the real MindRove device in the acquisition computer.
- Save EEG data from the smoke test.
- Integrate EEG stream into the full trial protocol.

## Biosignalsplux sEMG smoke test

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-biosignalsplux
~~~

Current status:

- Checks that the Biosignalsplux API can be imported.
- Checks that a device class can be created from configuration.

Pending:

- Validate the real `plux` API behavior on the acquisition computer.
- Start and stop short sEMG streaming.
- Save sEMG data from the smoke test.
- Integrate sEMG stream into the full trial protocol.

## MYO TCP receiver smoke test

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-myo-receiver --myo-receiver-port 9997
~~~

Current status:

- Starts the MYO TCP receiver.
- Waits briefly.
- Reads received messages.
- Stops the receiver safely.
- Handles Windows socket shutdown cleanly.

Pending:

- Test together with the synthetic MYO sender.
- Test with the real MYO SDK sender.
- Save received MYO messages in the full acquisition protocol.

## Not included yet

The current entry point does not yet include:

- Full timed trial execution.
- Full multimodal recording.
- Synchronized event insertion across devices.
- LabVIEW/cRIO streaming.
- Online classification.
- SVM/CSP inference.
- Exoskeleton control commands.

## Public safety policy

Do not commit:

- Real participant names.
- Consent files.
- Raw recordings.
- Private hardware paths.
- Private DLL or SDK paths.
- Private IP addresses.
- Trained private models.
- Local output files.

## Next development step

The next planned module is:

~~~text
src/motor_intention/acquisition/protocol_runner.py
~~~

This module will coordinate the timed experimental protocol and will later connect the acquisition devices, event markers, and storage utilities.
