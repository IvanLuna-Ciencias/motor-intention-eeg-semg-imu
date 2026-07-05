# Acquisition protocol

## Overview

The experimental protocol is designed to acquire multimodal signals related to upper-limb motor intention and movement execution.

The acquisition system may include:

- EEG signals.
- Surface EMG signals.
- IMU signals.
- Event markers.
- Optional real-time communication with external control or robotic systems.

## Signal modalities

### EEG

EEG is used to capture cortical activity related to motor preparation, intention, and execution. Relevant features may include spectral power, band ratios, event-related desynchronization/synchronization, and time-frequency descriptors.

### sEMG

Surface EMG is used to capture muscular activation associated with upper-limb movement. Relevant features may include amplitude descriptors, frequency-domain descriptors, and activation-related measures.

### IMU

IMU signals are used to capture movement dynamics, orientation, acceleration, and angular velocity. These signals can support movement detection and class discrimination, especially when combined with EEG and sEMG.

## Event markers

Event markers should be used to identify the experimental phases of each trial. A typical event file may include:

- Timestamp.
- Trial identifier.
- Phase label.
- Movement label.
- Start/end markers.

## General trial structure

A trial may include phases such as:

1. Alert or cue.
2. Preparation.
3. Execution.
4. Hold.
5. Rest.

The exact duration of each phase should be documented in the corresponding experiment configuration or protocol file.

## Notes on synchronization

Synchronization between modalities is critical. Each signal source should include timestamps or a reliable alignment strategy.

The repository will later include scripts for:

- Loading modality-specific files.
- Aligning signals using timestamps and event markers.
- Checking timing consistency.
- Exporting synchronized windows for feature extraction and classification.

## Ethical and privacy considerations

No identifiable participant information, consent forms, or raw biomedical data should be committed to this repository.

The complete dataset is subject to privacy, ethical, and institutional restrictions.
