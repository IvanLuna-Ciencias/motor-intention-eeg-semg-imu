# motor-intention-eeg-semg-imu

Multimodal EEG–sEMG–IMU pipeline for upper-limb motor intention detection and exoskeleton-oriented human–robot interfaces.

## Overview

This repository contains a clean, scalable, and research-oriented codebase for a master's thesis project focused on multimodal motor intention detection using electroencephalography (EEG), surface electromyography (sEMG), and inertial measurement unit (IMU) signals.

The project is oriented toward upper-limb assistive robotics and human–robot interfaces, with a particular focus on exoskeleton-compatible motor intention detection.

The complete system is designed around a multimodal processing pipeline that includes:

- Multimodal signal acquisition.
- Temporal synchronization of EEG, sEMG, IMU, and event markers.
- Signal preprocessing.
- Feature extraction in time, frequency, and time-frequency domains.
- Feature selection and redundancy reduction.
- Hierarchical classification:
  - L1: rest vs movement intention.
  - L2: movement class discrimination.
- Offline evaluation.
- Online simulation.
- Real-time-oriented inference.
- Future exoskeleton-oriented integration.

## Repository status

Current version: **v0.1.0**

This first public version provides the initial clean repository scaffold, documentation, data policy, and base project organization.

It does **not** include:

- Raw participant data.
- Consent forms.
- Identifiable participant information.
- Private institutional documents.
- Complete experimental datasets.
- Full legacy/local scripts.
- Trained private models.
- Local outputs or temporary files.

The purpose of this version is to establish a professional starting point before migrating cleaned and functional scripts in separate branches.

## Research context

In assistive robotics, motor intention detection is a key component for achieving safe, natural, and adaptive human–robot interaction. This project explores a multimodal strategy based on EEG, sEMG, and IMU signals to infer upper-limb motor intention and support the future control of an assistive exoskeleton.

The research pipeline is motivated by the complementary nature of the acquired signals:

- **EEG** provides information related to cortical activity, motor preparation, and sensorimotor modulation.
- **sEMG** provides information related to peripheral muscular activation.
- **IMU** provides kinematic information related to movement expression, acceleration, and angular velocity.

The project follows a hierarchical classification strategy in which the first level detects whether the user is in rest or movement intention, and the second level discriminates the movement class after movement intention is detected.

## Thesis-associated system

The thesis project was developed around a multimodal human–machine interface for upper-limb motor intention detection and exoskeleton-oriented validation.

The experimental and computational workflow included:

- EEG acquisition using a MindRove ARC device.
- sEMG acquisition using a Biosignalsplux system.
- sEMG and IMU acquisition using a MYO Armband.
- Event-based experimental protocol.
- Multimodal synchronization.
- Window-based feature extraction.
- SVM-based hierarchical classification.
- Offline and online simulation.
- UDP communication for real-time-oriented integration.
- cRIO/LabVIEW Real-Time exoskeleton-oriented validation.

## Repository structure

```text
motor-intention-eeg-semg-imu/
│
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
│
├── configs/
│   ├── preprocessing/
│   ├── features/
│   ├── training/
│   └── realtime/
│
├── docs/
│   ├── project_overview.md
│   ├── acquisition_protocol.md
│   ├── data_structure.md
│   ├── data_availability.md
│   ├── preprocessing.md
│   ├── feature_extraction.md
│   ├── classification_pipeline.md
│   ├── realtime_inference.md
│   └── testing_checklist.md
│
├── data/
│   ├── README.md
│   └── sample/
│       └── README.md
│
├── scripts/
│
├── src/
│   └── motor_intention/
│       ├── __init__.py
│       ├── io/
│       ├── preprocessing/
│       ├── features/
│       ├── models/
│       ├── realtime/
│       └── visualization/
│
├── models/
│   └── README.md
│
├── results/
│   └── README.md
│
└── tests/
```

## Data policy

Raw biomedical data from participants are **not included** in this public repository.

The complete dataset is not publicly distributed due to privacy, ethical, and institutional restrictions. Access to the full dataset may be considered under reasonable request to the research group and subject to institutional approval, ethical requirements, participant privacy protection, and data-sharing agreements.

Only synthetic, anonymized, or minimal example files may be included under:

```text
data/sample/
```

These files are intended only to demonstrate the expected structure of the data and the pipeline inputs.

For more information, see:

- [`docs/data_availability.md`](docs/data_availability.md)
- [`docs/data_structure.md`](docs/data_structure.md)
- [`data/README.md`](data/README.md)

## Experimental protocol summary

The original study considered multimodal recordings from healthy volunteers performing upper-limb movement tasks.

The acquisition protocol included:

- Right upper-limb tasks.
- EEG, sEMG, and IMU signals.
- Two experimental sessions per participant.
- Three movement blocks:
  - Elbow flexion/extension.
  - Shoulder flexion/extension.
  - Shoulder medial/lateral rotation.
- Event-based trial segmentation.
- Controlled experimental phases such as alert, preparation, execution, hold, and rest.
- Offline, online, and exoskeleton-oriented validation stages.

The public repository does not include the original raw recordings.

## Computational environment

The thesis-associated implementation used two Python environments due to device compatibility requirements:

### Main environment

The main processing environment was based on **Python 3.10** and was used for:

- Main acquisition process.
- Signal synchronization.
- Preprocessing.
- Feature extraction.
- Classification.
- Evaluation.
- Statistical analysis.

The current `requirements.txt` file is intended for this main environment.

### MYO sender environment

A separate **Python 3.9** environment was used for the MYO Armband sender process due to compatibility requirements. This sender transmitted MYO data through UDP to the main process.

The MYO-specific environment will be documented later when the corresponding cleaned acquisition scripts are migrated.

## Installation

Clone the repository:

```bash
git clone https://github.com/IvanLuna-Ciencias/motor-intention-eeg-semg-imu.git
cd motor-intention-eeg-semg-imu
```

Create the main Python environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install the main dependencies:

```bash
pip install -r requirements.txt
```

## Planned workflow

The intended processing workflow is:

```text
Raw signals + event markers
        ↓
Dataset preparation and synchronization
        ↓
Preprocessing
        ↓
Windowing
        ↓
Feature extraction
        ↓
Feature selection and redundancy reduction
        ↓
L1 classifier: rest vs movement
        ↓
L2 classifier: movement class
        ↓
Evaluation and visualization
        ↓
Demo inference / real-time-oriented integration
```

## Classification strategy

The project uses a hierarchical classification approach:

### L1 classifier

The first level detects whether a window corresponds to:

- Rest.
- Movement intention / active movement-related state.

### L2 classifier

If L1 detects movement intention, the second level discriminates the movement class.

This structure reduces the complexity of direct multiclass classification and is more compatible with real-time assistive control scenarios, where false activations and unstable transitions must be controlled carefully.

## Real-time-oriented integration

The long-term goal of this repository is to support a clean implementation of a real-time-oriented multimodal human–machine interface.

The intended architecture includes:

- Signal acquisition and synchronization in Python.
- Sliding-window feature extraction.
- Hierarchical inference.
- Temporal decision stabilization.
- UDP communication with external systems.
- Exoskeleton-oriented command generation.
- Safety-oriented state-machine logic.

## Version roadmap

- **v0.1.0**: Initial clean repository scaffold, documentation, data policy, and base organization.
- **v0.2.0**: Migration of cleaned dataset preparation and synchronization scripts.
- **v0.3.0**: Preprocessing and feature extraction modules.
- **v0.4.0**: L1/L2 training and evaluation pipeline.
- **v0.5.0**: Demo inference with synthetic/sample data.
- **v0.6.0**: Real-time-oriented inference demo.
- **v1.0.0**: Stable thesis-associated release.

## Development strategy

This repository will be developed incrementally.

The `main` branch should remain clean, stable, and presentable. Functional scripts will be migrated later through separate development branches, for example:

```text
feature/data-synchronization
feature/preprocessing
feature/eeg-features
feature/semg-features
feature/imu-features
feature/l1-classifier
feature/l2-classifier
feature/realtime-demo
```

This avoids uploading disorganized local folders and helps preserve a professional project history.

## Citation

Citation information will be added when the associated thesis, article, or archived software release becomes publicly available.

## License

This project is licensed under the MIT License. See [`LICENSE`](LICENSE) for details.

## Author

Iván Alberto Luna Hernández  
Master's research project in Bioengineering  
Upper-limb motor intention detection, biomedical signal processing, and assistive robotics.

## Public acquisition layer

This repository includes a public acquisition layer extracted and cleaned from the original thesis acquisition scripts.

The goal of this layer is to provide a modular, testable, and public-safe structure for multimodal acquisition without exposing private participant data, local hardware paths, private IP addresses, or raw experimental recordings.

### Included acquisition components

The current public acquisition layer includes:

~~~text
src/motor_intention/protocols/event_markers.py
src/motor_intention/protocols/trial_protocol.py
src/motor_intention/acquisition/storage.py
src/motor_intention/acquisition/session_config.py
src/motor_intention/acquisition/device_config.py
src/motor_intention/acquisition/mindrove.py
src/motor_intention/acquisition/biosignalsplux.py
src/motor_intention/communication/tcp_myo.py
~~~

### Synthetic acquisition demo

A complete synthetic acquisition demo is available at:

~~~text
scripts/acquisition/run_synthetic_acquisition_demo.py
~~~

Run it with:

~~~bash
python scripts/acquisition/run_synthetic_acquisition_demo.py
~~~

The demo generates synthetic EEG, sEMG, MYO, event, and metadata files under:

~~~text
outputs/acquisition/
~~~

The generated files are synthetic only and should not be committed.

### MYO TCP bridge

The repository includes a clean MYO TCP bridge that can be tested without hardware using:

~~~text
scripts/acquisition/run_myo_receiver_demo.py
scripts/acquisition/run_myo_sender.py
~~~

This supports synthetic JSON-lines messages and separates the MYO SDK process from the main acquisition workflow.

### Hardware wrappers

Dependency-safe wrappers are included for:

~~~text
MindRove EEG
Biosignalsplux sEMG
MYO TCP bridge
~~~

These wrappers are designed so the repository remains importable and testable even when hardware-specific dependencies are not installed.

### Configuration files

Public-safe example configuration files are provided in:

~~~text
configs/acquisition/acquisition.example.yaml
configs/acquisition/myo_sender.example.yaml
~~~

Private hardware paths, participant information, private IP addresses, and real recordings should be kept in local configuration files and should not be committed.

### Acquisition documentation

Additional documentation is available in:

~~~text
docs/acquisition_software_audit.md
docs/acquisition_hardware_wrappers.md
docs/myo_bridge.md
docs/synthetic_acquisition_demo.md
docs/testing_checklist.md
~~~
