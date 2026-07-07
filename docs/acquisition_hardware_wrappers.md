# Acquisition hardware wrappers

This document summarizes the public hardware wrapper structure used for real multimodal acquisition.

The repository includes clean wrappers for:

~~~text
src/motor_intention/acquisition/mindrove.py
src/motor_intention/acquisition/biosignalsplux.py
src/motor_intention/communication/tcp_myo.py
~~~

These modules are designed to keep the public repository importable and testable even when the hardware-specific dependencies are not installed.

## Design goal

The original thesis acquisition scripts integrated several systems in a single workflow:

- MindRove EEG acquisition.
- Biosignalsplux sEMG acquisition.
- MYO Armband EMG/IMU bridge.
- Event markers.
- Trial protocol timing.
- File storage.
- Optional LabVIEW/cRIO communication.
- Optional online classification.

For the public repository, these responsibilities are separated into smaller modules.

## MindRove EEG wrapper

Module:

~~~text
src/motor_intention/acquisition/mindrove.py
~~~

Purpose:

- Lazily import the MindRove Python API.
- Prepare and release EEG sessions.
- Start and stop EEG streaming.
- Insert EEG stream markers.
- Read current or full EEG board data.
- Keep the repository testable without MindRove installed.

Configuration source:

~~~text
MindRoveConfig
~~~

defined in:

~~~text
src/motor_intention/acquisition/device_config.py
~~~

## Biosignalsplux sEMG wrapper

Module:

~~~text
src/motor_intention/acquisition/biosignalsplux.py
~~~

Purpose:

- Lazily import the Biosignalsplux `plux` API.
- Avoid hardcoded local DLL paths.
- Store sEMG samples in a thread-safe buffer.
- Separate acquisition buffer logic from hardware initialization.
- Keep the repository testable without Biosignalsplux installed.

Configuration source:

~~~text
BiosignalspluxConfig
~~~

defined in:

~~~text
src/motor_intention/acquisition/device_config.py
~~~

## MYO TCP bridge

Module:

~~~text
src/motor_intention/communication/tcp_myo.py
~~~

Purpose:

- Receive MYO-like JSON messages through TCP.
- Keep the real MYO SDK process separated from the main Python 3.10 acquisition workflow.
- Support synthetic sender testing without hardware.
- Store received messages with local reception timestamps.

Related scripts:

~~~text
scripts/acquisition/run_myo_receiver_demo.py
scripts/acquisition/run_myo_sender.py
~~~

## Configuration files

Public example configuration:

~~~text
configs/acquisition/acquisition.example.yaml
~~~

This file should be copied locally and adapted to each hardware setup.

Do not commit:

- Private participant information.
- Local DLL or SDK paths.
- Private IP addresses.
- Real MAC addresses when not appropriate for public release.
- Raw experimental recordings.
- Private model paths.

## Testing strategy

The wrappers are tested using:

- Fake board objects.
- Synthetic MYO clients.
- Buffer-only tests.
- Dependency-safe import checks.

This allows continuous testing without requiring hardware access.

## Current public scope

The public wrappers define the structure for real acquisition, but the repository does not include private device credentials, participant data, institutional paths, or raw thesis recordings.

Future versions may include a clean real-acquisition entry point that combines:

- `AcquisitionSessionConfig`
- `AcquisitionDeviceConfig`
- `TrialProtocol`
- `MindRoveEEGDevice`
- `BiosignalspluxEMGDevice`
- `MyoTCPReceiver`
- Standardized storage utilities
