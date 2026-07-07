# Acquisition software audit

This document summarizes the legacy acquisition scripts used during the development of the multimodal EEG-sEMG-IMU motor intention detection system.

The purpose of this document is to identify the role of each script before migrating the code into a clean, modular, and public repository structure.

## Legacy scripts reviewed

The acquisition-related scripts currently reviewed are:

~~~text
myo_sender.py
myo_receiver.py
main_acquisition.py
main_acquisition_LV.py
main_acquisition_LV_FINALES.py
~~~

## Initial interpretation

### myo_sender.py

This script runs the MYO Armband acquisition process.

Main responsibilities:

- Acquire 8-channel MYO EMG.
- Acquire orientation, accelerometer, gyroscope, pose, and RSSI data.
- Display MYO EMG data in a live window.
- Send JSON messages to the main acquisition process through TCP.
- Receive START and STOP commands.
- Save a local MYO CSV file.

This script should be treated as a hardware-dependent acquisition client.

### myo_receiver.py

This script runs in the main acquisition environment.

Main responsibilities:

- Open a TCP server.
- Receive JSON messages from the MYO sender.
- Store incoming MYO data in a thread-safe buffer.
- Send START and STOP commands to the MYO sender.
- Provide buffered MYO data to the main acquisition script.

This script should be treated as the bridge between the MYO sender environment and the main Python acquisition environment.

### main_acquisition.py

This script is the main multimodal acquisition workflow.

Main responsibilities:

- Configure EEG acquisition.
- Configure sEMG acquisition.
- Start the MYO receiver.
- Run calibration windows.
- Run the experimental protocol.
- Save EEG, sEMG, MYO, event, and metadata files.

The current version may also include online classification logic, so it should not be migrated directly as a pure acquisition script.

### main_acquisition_LV.py

This script appears to be a LabVIEW-oriented version for local online testing.

Main responsibilities:

- Run multimodal acquisition.
- Run online classification.
- Stream classifier output to a LabVIEW-compatible endpoint.
- Use local communication settings.

This script should be treated as a local integration prototype.

### main_acquisition_LV_FINALES.py

This script appears to be the most complete real-time integration version.

Main responsibilities:

- Run multimodal acquisition.
- Run online classification.
- Stream classifier output to the robotic/cRIO-LabVIEW system.
- Save acquisition and event files.

This script should be treated as the main reference for the final real-time robotic integration workflow, but not copied directly into the public package.

## Main cleanup requirements

Before migrating these scripts, the following issues must be addressed:

- Remove hardcoded local paths.
- Remove private model paths.
- Remove hardcoded device SDK paths.
- Remove hardcoded IP addresses from public defaults.
- Replace participant names with anonymized subject/session identifiers.
- Separate acquisition from classification.
- Separate classification from LabVIEW/cRIO communication.
- Separate GUI code from acquisition logic where possible.
- Standardize timestamps.
- Standardize output file formats.
- Add configuration files for device-specific settings.

## Proposed module organization

The clean repository should separate acquisition into modules:

~~~text
src/motor_intention/acquisition/
src/motor_intention/protocols/
src/motor_intention/communication/
scripts/acquisition/
~~~

Recommended future modules:

~~~text
src/motor_intention/acquisition/mindrove.py
src/motor_intention/acquisition/biosignalsplux.py
src/motor_intention/acquisition/myo_receiver.py
src/motor_intention/acquisition/storage.py
src/motor_intention/acquisition/synchronization.py

src/motor_intention/protocols/event_markers.py
src/motor_intention/protocols/trial_protocol.py
src/motor_intention/protocols/instructions.py

src/motor_intention/communication/tcp_myo.py
src/motor_intention/communication/lv_stream.py

scripts/acquisition/run_myo_sender.py
scripts/acquisition/run_acquisition_training.py
scripts/acquisition/run_acquisition_online_local.py
scripts/acquisition/run_acquisition_realtime_crio.py
~~~

## Initial migration decision

The legacy scripts should not be copied directly into `src/`.

The first clean code modules should be:

~~~text
src/motor_intention/protocols/event_markers.py
src/motor_intention/protocols/trial_protocol.py
~~~

These modules are hardware-independent and define the experimental protocol structure before adding device-specific acquisition code.
