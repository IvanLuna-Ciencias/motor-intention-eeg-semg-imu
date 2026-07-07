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
