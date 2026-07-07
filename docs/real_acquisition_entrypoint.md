# Real acquisition training entry point

This document describes the public-safe real acquisition training entry point.

Script:

~~~text
scripts/acquisition/run_acquisition_training.py
~~~

## Current scope

The current version is a dry-run skeleton. It does not initialize real hardware yet.

It currently supports:

- Loading acquisition YAML configuration.
- Creating anonymized session configuration.
- Building a balanced trial list.
- Estimating acquisition duration.
- Building standardized output filenames.
- Printing an acquisition plan.
- Optionally writing a metadata preview.

## Run dry-run plan

Example:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4
~~~

## Write metadata preview

Example:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4 --write-metadata-preview
~~~

This writes a metadata preview under:

~~~text
outputs/acquisition/
~~~

The `outputs/` folder is ignored by Git and should not be committed.

## Hardware execution status

Real hardware execution is intentionally disabled in this first public skeleton.

The next planned steps are:

1. Add MindRove EEG preparation and acquisition block.
2. Add Biosignalsplux sEMG acquisition block.
3. Add MYO TCP receiver integration.
4. Save synchronized EEG, sEMG, MYO, events, and metadata.
5. Add LabVIEW/cRIO streaming in a later phase.
6. Add online classification in a later phase.

## Public safety

This script should not include:

- Participant names.
- Private device addresses.
- Private IP addresses.
- Local DLL paths.
- Local SDK paths.
- Raw recordings.
- Private trained model paths.

## MindRove smoke test

The entry point includes an optional MindRove EEG smoke test.

It is disabled by default and only runs when both flags are used:

```bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-mindrove
## MindRove smoke test

The entry point includes an optional MindRove EEG smoke test.

It is disabled by default and only runs when both flags are used:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-mindrove
~~~

The smoke test performs only a short connectivity check:

- Prepare MindRove session.
- Start EEG stream.
- Insert START marker.
- Read a short EEG preview.
- Insert STOP marker.
- Close the session.

This is not yet the full experimental acquisition protocol.

## Biosignalsplux smoke test

The entry point also includes an optional Biosignalsplux sEMG smoke test.

It is disabled by default and only runs when both flags are used:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-biosignalsplux
~~~

The current smoke test validates that the Biosignalsplux API can be imported and that a device class can be created from the public configuration.

Full sEMG streaming will be added after validating the hardware-specific API behavior on the acquisition computer.

## MYO TCP receiver smoke test

The entry point also includes an optional MYO TCP receiver smoke test.

It is disabled by default and only runs when both flags are used:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-myo-receiver
~~~

For local testing, a temporary port can be selected:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-myo-receiver --myo-receiver-port 9997
~~~

The smoke test starts the TCP receiver briefly and then closes it safely. It does not require the real MYO Armband.

## Protocol events preview

The real acquisition entry point now uses the clean protocol runner module:

~~~text
src/motor_intention/acquisition/protocol_runner.py
~~~

A protocol events preview can be generated without hardware using:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4 --write-events-preview
~~~

This writes a synthetic protocol events CSV under:

~~~text
outputs/acquisition/
~~~

This preview is useful for validating trial order, phase timing, and event markers before connecting real hardware.

## MindRove full protocol marker test

The entry point can now run the timed protocol and forward every protocol marker to MindRove.

This mode is disabled by default and requires:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-mindrove --run-protocol-markers
~~~

For shorter local validation, the realtime protocol can be accelerated:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-mindrove --run-protocol-markers --protocol-time-scale 0.1
~~~

This mode uses:

~~~text
ProtocolRunner
ProtocolEventRecorder
DeviceMarkerCallback
MindRoveEEGDevice
~~~

Current purpose:

- Validate full protocol timing.
- Insert protocol markers into the EEG stream.
- Confirm that the marker callback layer works with MindRove.
- Keep acquisition and event logic separated.

This is not yet the full multimodal acquisition protocol.

## EEG-only full protocol acquisition

The entry point now includes a protected EEG-only full protocol acquisition mode using MindRove.

It requires:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-mindrove --run-eeg-protocol
~~~

For shorter validation, the realtime protocol can be accelerated:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-mindrove --run-eeg-protocol --protocol-time-scale 0.1
~~~

This mode:

- Starts the MindRove EEG stream before the protocol.
- Keeps the EEG stream active while the protocol runs.
- Inserts protocol markers into the EEG stream.
- Retrieves available EEG data after the protocol finishes.
- Saves EEG data, events, and metadata.
- Closes the MindRove session safely.

The protocol runner controls timing and markers, but the acquisition stream is managed explicitly by the acquisition entry point.

## sEMG-only full protocol acquisition

The entry point now includes a protected sEMG-only full protocol acquisition mode using Biosignalsplux.

It requires:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-biosignalsplux --run-semg-protocol
~~~

For shorter validation, the realtime protocol can be accelerated:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-biosignalsplux --run-semg-protocol --protocol-time-scale 0.1
~~~

This mode:

- Starts Biosignalsplux sEMG acquisition before the protocol.
- Keeps sEMG acquisition active while the protocol runs.
- Records protocol events using `ProtocolEventRecorder`.
- Stops sEMG acquisition explicitly after the protocol.
- Retrieves available sEMG data.
- Saves sEMG data, events, and metadata.
- Closes Biosignalsplux resources safely.

The protocol runner controls timing and events, but the acquisition lifetime is managed explicitly by the acquisition entry point.

## MYO-only full protocol acquisition

The entry point now includes a protected MYO-only full protocol acquisition mode using the TCP receiver.

It requires:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-myo-receiver --run-myo-protocol
~~~

For shorter validation, the realtime protocol can be accelerated:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-myo-receiver --run-myo-protocol --protocol-time-scale 0.1 --myo-receiver-port 9997
~~~

This mode:

- Starts the MYO TCP receiver before the protocol.
- Keeps the receiver active while the protocol runs.
- Records protocol events using `ProtocolEventRecorder`.
- Retrieves available MYO messages after the protocol finishes.
- Saves MYO messages, events, and metadata.
- Stops the MYO receiver safely.

The receiver can be tested with the synthetic MYO sender or with the real MYO SDK sender.

## EEG+MYO full protocol acquisition

The entry point now includes a protected EEG+MYO full protocol acquisition mode.

It requires:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-mindrove --use-myo-receiver --run-eeg-myo-protocol
~~~

For local validation with the MYO synthetic sender, use a temporary MYO receiver port:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-mindrove --use-myo-receiver --run-eeg-myo-protocol --myo-receiver-port 9997
~~~

This mode:

- Starts MindRove EEG streaming before the protocol.
- Starts the MYO TCP receiver before the protocol.
- Keeps both acquisition streams active while the protocol runs.
- Inserts protocol markers into the EEG stream.
- Records protocol events using `ProtocolEventRecorder`.
- Retrieves available EEG data and MYO messages after the protocol finishes.
- Saves EEG, MYO, events, and metadata.
- Closes MindRove and the MYO receiver safely.

The MYO sender remains a separate process by design.

## EEG+sEMG+MYO full multimodal protocol acquisition

The entry point now includes a protected full multimodal protocol acquisition mode.

It requires:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-mindrove --use-biosignalsplux --use-myo-receiver --run-multimodal-protocol
~~~

For local MYO receiver testing, a temporary receiver port can be selected:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-001 --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-mindrove --use-biosignalsplux --use-myo-receiver --run-multimodal-protocol --myo-receiver-port 9997
~~~

This mode:

- Starts MindRove EEG streaming before the protocol.
- Starts Biosignalsplux sEMG acquisition before the protocol.
- Starts the MYO TCP receiver before the protocol.
- Keeps all acquisition streams active while the protocol runs.
- Inserts protocol markers into the EEG stream.
- Records protocol events using `ProtocolEventRecorder`.
- Retrieves available EEG, sEMG, and MYO data after the protocol finishes.
- Saves EEG, sEMG, MYO, events, and metadata.
- Closes all hardware resources safely.

The protocol runner controls timing and events, while acquisition lifetimes are managed explicitly by the acquisition entry point.
