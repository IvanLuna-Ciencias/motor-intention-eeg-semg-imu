# Acquisition runtime principles

This document defines runtime principles for full protocol acquisition.

## Continuous acquisition principle

Real hardware acquisition should not be stopped only because a fixed protocol timer finishes.

The acquisition design should follow this sequence:

1. Prepare hardware devices.
2. Start streaming or recording.
3. Run the timed protocol as an event and marker generator.
4. Keep acquisition active while the protocol runs.
5. Stop acquisition only through an explicit stop request, safe shutdown, or controlled end of the acquisition script.
6. Retrieve available data after stopping.
7. Save EEG, sEMG, MYO, events, and metadata.
8. Release hardware resources safely.

## Reason

Earlier acquisition implementations had timing issues when recording was too tightly coupled to fixed-duration protocol timing.

To preserve robust behavior, the protocol runner should coordinate events and markers, but it should not be the only mechanism controlling the lifetime of hardware recording.

## Practical rule

The protocol controls:

- Trial order.
- Phase transitions.
- Event labels.
- Marker insertion.
- Timing structure.

The acquisition manager controls:

- Device preparation.
- Device start.
- Continuous streaming.
- Stop conditions.
- Data retrieval.
- File saving.
- Safe resource release.

## Stop conditions

Supported stop conditions should include:

- Normal script completion after the selected acquisition mode.
- Manual interruption with `KeyboardInterrupt`.
- Explicit future STOP command.
- Device-specific error handling.

## Full protocol development order

The full acquisition protocol should be developed in stages:

1. EEG-only full protocol acquisition.
2. sEMG-only full protocol acquisition.
3. MYO-only full protocol acquisition.
4. Multimodal EEG+sEMG+MYO acquisition.
5. LabVIEW/cRIO streaming.
6. Online classification.
7. Exoskeleton control commands.

## Public safety

Full protocol acquisition must not commit:

- Raw participant recordings.
- Identifiable subject data.
- Private hardware paths.
- Private IP addresses.
- Local SDK/DLL paths.
- Generated output folders.
