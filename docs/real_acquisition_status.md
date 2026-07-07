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

## MindRove protocol marker mode

The acquisition entry point now includes a protected MindRove protocol marker mode:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-mindrove --run-protocol-markers
~~~

This mode connects:

~~~text
ProtocolRunner
ProtocolEventRecorder
DeviceMarkerCallback
MindRoveEEGDevice
~~~

Current status:

- Runs the timed protocol.
- Forwards protocol markers to MindRove.
- Reads an EEG preview after the protocol.
- Closes the MindRove session safely.

Pending:

- Validate marker insertion with the real MindRove device.
- Save EEG stream data from the full protocol.
- Compare exported event CSV with MindRove marker timing.
- Extend the same protocol runner structure to sEMG and MYO acquisition.

## EEG-only full protocol acquisition mode

The acquisition entry point now includes a protected EEG-only full protocol acquisition mode:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-mindrove --run-eeg-protocol
~~~

Current status:

- Starts MindRove EEG streaming before the protocol.
- Runs the timed protocol using `ProtocolRunner`.
- Inserts protocol markers into the EEG stream using `DeviceMarkerCallback`.
- Records protocol events using `ProtocolEventRecorder`.
- Retrieves available EEG data after protocol completion.
- Saves EEG, events, and metadata files.
- Closes the MindRove session safely.

Design note:

The EEG stream is managed explicitly by the acquisition entry point. The protocol controls timing and markers, but hardware acquisition is not treated as a rigid timer-controlled process.

Pending validation:

- Test with the real MindRove device.
- Verify that saved EEG shape is correct.
- Verify that event CSV timing matches inserted EEG markers.
- Confirm behavior during manual interruption.

## sEMG-only full protocol acquisition mode

The acquisition entry point now includes a protected sEMG-only full protocol acquisition mode:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-biosignalsplux --run-semg-protocol
~~~

Current status:

- Creates the Biosignalsplux device class from configuration.
- Starts sEMG acquisition before the protocol.
- Runs the timed protocol using `ProtocolRunner`.
- Records protocol events using `ProtocolEventRecorder`.
- Stops sEMG acquisition explicitly after protocol completion.
- Retrieves available sEMG data.
- Saves sEMG, events, and metadata files.
- Closes Biosignalsplux resources safely.

Design note:

The protocol controls timing and events, but the sEMG acquisition lifetime is managed explicitly by the acquisition entry point.

Pending validation:

- Test with the real Biosignalsplux device.
- Verify that the acquisition thread starts and stops correctly.
- Verify that saved sEMG shape is correct.
- Confirm behavior during manual interruption.
- Validate that the `plux` API loop exits cleanly after `stop_acquisition()`.

## MYO-only full protocol acquisition mode

The acquisition entry point now includes a protected MYO-only full protocol acquisition mode:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-myo-receiver --run-myo-protocol
~~~

Current status:

- Starts the MYO TCP receiver before the protocol.
- Runs the timed protocol using `ProtocolRunner`.
- Records protocol events using `ProtocolEventRecorder`.
- Keeps the MYO receiver active while the protocol runs.
- Retrieves available MYO messages after protocol completion.
- Saves MYO, events, and metadata files.
- Stops the MYO TCP receiver safely.

Design note:

The protocol controls timing and events, but the MYO receiver lifetime is managed explicitly by the acquisition entry point.

Pending validation:

- Test with the synthetic MYO sender.
- Test with the real MYO SDK sender.
- Verify MYO message count and timestamp behavior.
- Confirm behavior during manual interruption.
- Validate synchronization between MYO timestamps and protocol events.

## MYO synthetic sender and protocol receiver validation

The MYO-only full protocol acquisition mode was validated using the synthetic MYO sender.

Test structure:

~~~text
Terminal 1:
run_acquisition_training.py with --use-myo-receiver --run-myo-protocol

Terminal 2:
run_myo_sender.py with a local YAML configuration pointing to the same receiver port
~~~

Result:

- The protocol receiver started correctly.
- The synthetic sender connected to the receiver.
- MYO-like messages were received during protocol execution.
- The acquisition script saved MYO messages, protocol events, and metadata.
- The receiver stopped safely after protocol completion.

Design note:

The MYO sender remains a separate process by design. This preserves compatibility with the original architecture, where the MYO SDK sender may require a separate Python environment.
