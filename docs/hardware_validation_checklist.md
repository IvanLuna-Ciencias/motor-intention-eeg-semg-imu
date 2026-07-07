# Hardware validation checklist

This document defines the hardware validation checklist for the full protocol acquisition modes.

## Goal

Validate that the public acquisition entry point works correctly with real hardware before adding LabVIEW/cRIO streaming or online classification.

Main entry point:

~~~text
scripts/acquisition/run_acquisition_training.py
~~~

## General rules

Before every hardware validation:

- Use anonymized subject/session IDs.
- Use a local acquisition YAML configuration.
- Do not commit raw recordings.
- Do not commit private IP addresses.
- Do not commit local DLL or SDK paths.
- Check that output files are created under `outputs/acquisition/`.
- Confirm that all devices close safely after completion or interruption.

## Stage 1: Dry run

Command:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-test --session-id ses-01 --movement-block Codo --total-trials 4
~~~

Expected:

- No hardware is initialized.
- Acquisition plan is printed.
- Trial list is generated.
- Output filenames are shown.

## Stage 2: Events preview

Command:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-test --session-id ses-01 --movement-block Codo --total-trials 4 --write-events-preview
~~~

Expected:

- Events CSV is generated.
- Trial phases and markers are coherent.
- Output remains under `outputs/acquisition/`.

## Stage 3: MindRove smoke test

Command:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-test --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-mindrove
~~~

Expected:

- MindRove session is prepared.
- EEG stream starts.
- START and STOP markers are inserted.
- EEG preview shape is printed.
- Session closes safely.

Check:

- Sampling rate is correct.
- EEG channels are correct.
- No resource is left open.

## Stage 4: EEG-only full protocol

Command:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-test --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-mindrove --run-eeg-protocol
~~~

Expected:

- EEG stream starts before the protocol.
- Protocol markers are inserted.
- EEG data are saved.
- Events CSV is saved.
- Metadata JSON is saved.
- MindRove closes safely.

Check:

- EEG CSV has expected channels.
- Events CSV has coherent timing.
- Metadata includes mode and output files.
- Manual interruption closes safely.

## Stage 5: Biosignalsplux smoke test

Command:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-test --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-biosignalsplux
~~~

Expected:

- Biosignalsplux API imports correctly.
- Device class is created.
- Configuration values are printed.

Check:

- DLL/API path is local and not committed.
- Device address is local and not committed.

## Stage 6: sEMG-only full protocol

Command:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-test --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-biosignalsplux --run-semg-protocol
~~~

Expected:

- sEMG acquisition starts before the protocol.
- Protocol events are recorded.
- sEMG data are saved.
- Events CSV is saved.
- Metadata JSON is saved.
- Biosignalsplux resources close safely.

Check:

- sEMG CSV has expected channels.
- Acquisition thread exits correctly.
- Manual interruption closes safely.

## Stage 7: MYO-only full protocol with synthetic sender

Terminal 1:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-test --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-myo-receiver --run-myo-protocol --myo-receiver-port 9997
~~~

Terminal 2:

~~~bash
python scripts/acquisition/run_myo_sender.py --config outputs/local/myo_sender_9997.yaml
~~~

Expected:

- MYO receiver starts before the protocol.
- Synthetic sender connects.
- MYO messages are received.
- MYO CSV is saved.
- Events CSV is saved.
- Metadata JSON is saved.
- Receiver closes safely.

Check:

- MYO message count is greater than zero.
- Timestamps are coherent.
- Sender exits cleanly if receiver closes.

## Stage 8: EEG+MYO full protocol

Command:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-test --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-mindrove --use-myo-receiver --run-eeg-myo-protocol --myo-receiver-port 9997
~~~

Expected:

- MindRove stream starts.
- MYO receiver starts.
- Protocol markers are inserted into EEG.
- MYO messages are received if sender is active.
- EEG, MYO, events, and metadata are saved.
- Both resources close safely.

Check:

- EEG markers match exported event CSV.
- MYO timestamps align with protocol window.
- Manual interruption closes both resources.

## Stage 9: Full multimodal protocol

Command:

~~~bash
python scripts/acquisition/run_acquisition_training.py --subject-id sub-test --session-id ses-01 --movement-block Codo --total-trials 4 --execute-hardware --use-mindrove --use-biosignalsplux --use-myo-receiver --run-multimodal-protocol --myo-receiver-port 9997
~~~

Expected:

- EEG stream starts.
- sEMG acquisition starts.
- MYO receiver starts.
- Protocol markers are inserted into EEG.
- EEG, sEMG, MYO, events, and metadata are saved.
- All resources close safely.

Check:

- EEG CSV shape is correct.
- sEMG CSV shape is correct.
- MYO CSV has messages when sender is active.
- Events CSV is coherent.
- Metadata references all output files.
- Manual interruption closes all devices.

## Validation notes

For each validation, record:

- Date.
- Computer used.
- Python environment.
- Hardware connected.
- Command used.
- Result.
- Observed errors.
- Output file shapes.
- Whether shutdown was clean.

## Next step after validation

After successful hardware validation, the next development phase should be:

~~~text
LabVIEW/cRIO streaming integration
~~~

followed by:

~~~text
online classification integration
~~~
