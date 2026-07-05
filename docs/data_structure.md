# Data structure

## Important notice

Raw participant data are not included in this public repository.

This document describes the expected data organization for local, private, or restricted use. The full experimental dataset is not publicly distributed due to privacy, ethical, and institutional restrictions.

Only synthetic, anonymized, or minimal example files should be included in the public repository.

## Recommended internal structure

For local or private use, the dataset may be organized as:

```text
data/
├── raw/
│   ├── sub-001/
│   │   ├── ses-01/
│   │   │   ├── eeg/
│   │   │   ├── semg_biosignals/
│   │   │   ├── myo/
│   │   │   ├── events/
│   │   │   └── metadata/
│   │   └── ses-02/
│   │       ├── eeg/
│   │       ├── semg_biosignals/
│   │       ├── myo/
│   │       ├── events/
│   │       └── metadata/
│   └── sub-002/
│
├── interim/
│   └── synchronized/
│
├── processed/
│   ├── windows/
│   ├── features/
│   └── labels/
│
├── external/
├── private/
├── consents/
└── sample/
```

The following folders are intended for local/private use only and are ignored by Git:

```text
data/raw/
data/interim/
data/processed/
data/external/
data/private/
data/consents/
```

Only `data/sample/` may contain public example files.

## Participant and session naming

A recommended naming convention is:

```text
sub-001/
sub-002/
sub-003/
```

For sessions:

```text
ses-01/
ses-02/
```

This convention avoids storing participant names or identifiable information in file names.

## Suggested movement block organization

The original experimental design considered three movement blocks:

1. Elbow flexion/extension.
2. Shoulder flexion/extension.
3. Shoulder medial/lateral rotation.

A possible internal structure is:

```text
sub-001/
└── ses-01/
    ├── block-01_elbow_flex_ext/
    ├── block-02_shoulder_flex_ext/
    └── block-03_shoulder_rotation/
```

Alternatively, the block identifier may be stored in the metadata and event files instead of using separate folders.

## Expected signal files

Depending on the acquisition system, each session may contain files similar to:

```text
eeg.csv
semg_biosignals.csv
myo.csv
events.csv
metadata.json
```

or, when using a more explicit naming scheme:

```text
sub-001_ses-01_block-02_eeg.csv
sub-001_ses-01_block-02_semg_biosignals.csv
sub-001_ses-01_block-02_myo.csv
sub-001_ses-01_block-02_events.csv
sub-001_ses-01_block-02_metadata.json
```

## EEG file structure

A minimal EEG table may include:

| Column | Description |
|---|---|
| `time_s` | Timestamp in seconds. |
| `ch_0` | EEG channel 0. |
| `ch_1` | EEG channel 1. |
| `ch_2` | EEG channel 2. |
| `ch_3` | EEG channel 3. |
| `ch_4` | EEG channel 4. |
| `ch_5` | EEG channel 5. |

Additional channels may be included depending on the acquisition system.

The original thesis project focused on central sensorimotor EEG channels approximately corresponding to C1–C6.

## Biosignalsplux sEMG file structure

A minimal Biosignalsplux sEMG table may include:

| Column | Description |
|---|---|
| `time_s` | Timestamp in seconds. |
| `emg_0` | sEMG channel 0. |
| `emg_1` | sEMG channel 1. |

The muscle placement may vary depending on the movement block. Therefore, muscle/channel mapping should be documented in the metadata file.

## MYO file structure

A minimal MYO table may include:

| Column | Description |
|---|---|
| `timestamp` or `time_s` | MYO timestamp or synchronized timestamp. |
| `emg_0` to `emg_7` | MYO sEMG channels. |
| `orient_0` to `orient_3` | Orientation/quaternion values. |
| `accel_0` to `accel_2` | Accelerometer axes. |
| `gyro_0` to `gyro_2` | Gyroscope axes. |
| `pose` | MYO pose label, if available. |
| `rssi` | Signal strength, if available. |

The MYO Armband may require a separate acquisition environment due to compatibility constraints.

## Event file structure

A minimal event table may include:

| Column | Description |
|---|---|
| `time_s` | Event timestamp in seconds. |
| `marker` | Event marker code or name. |
| `label` | Human-readable event label. |
| `trial` | Trial number. |
| `phase` | Trial phase. |
| `movement` | Movement class. |
| `block` | Movement block identifier. |
| `session` | Session identifier. |
| `subject` | Coded subject identifier. |

Recommended phase labels:

```text
alert
preparation
execution
hold
rest
```

Recommended movement labels:

```text
rest
flexion
extension
medial_rotation
lateral_rotation
```

For public sample data, simplified labels may be used as long as they are clearly documented.

## Metadata file structure

A metadata file may include:

```json
{
  "subject_id": "sub-001",
  "session_id": "ses-01",
  "block_id": "block-02",
  "movement_block": "shoulder_flexion_extension",
  "dominant_arm": "right",
  "eeg_device": "MindRove ARC",
  "semg_device": "Biosignalsplux",
  "imu_device": "MYO Armband",
  "eeg_sampling_hz": 500,
  "semg_sampling_hz": 1000,
  "myo_emg_sampling_hz": 200,
  "myo_imu_sampling_hz": 50,
  "notes": "Synthetic example only. No real participant data."
}
```

Public metadata files must not include identifiable participant information.

## Processed feature structure

After synchronization, preprocessing, windowing, and feature extraction, a processed feature table may include:

| Column | Description |
|---|---|
| `subject` | Coded subject identifier. |
| `session` | Session identifier. |
| `block` | Movement block. |
| `trial` | Trial number. |
| `window_start_s` | Start time of the analysis window. |
| `window_end_s` | End time of the analysis window. |
| `phase` | Dominant or assigned phase label. |
| `movement` | Movement label. |
| `l1_label` | Rest vs movement label. |
| `l2_label` | Movement class label. |
| `feature_*` | Extracted EEG, sEMG, MYO, or IMU features. |

## Labeling strategy

The hierarchical classification strategy may use labels such as:

### L1 labels

| Label | Meaning |
|---|---|
| `0` | Rest. |
| `1` | Movement intention / active movement-related state. |

### L2 labels

| Label | Meaning |
|---|---|
| `0` | Flexion. |
| `1` | Extension. |

The exact mapping must be documented when cleaned scripts are migrated.

## Public sample data

Public sample data should be:

- Synthetic.
- Fully anonymized.
- Minimal.
- Small in size.
- Clearly marked as example data.
- Not derived from identifiable participant recordings unless explicitly approved.

Allowed public examples may include:

```text
data/sample/synthetic_eeg.csv
data/sample/synthetic_semg_biosignals.csv
data/sample/synthetic_myo.csv
data/sample/synthetic_events.csv
data/sample/example_metadata.json
```

## Files intentionally excluded from Git

The `.gitignore` file excludes raw biomedical files, tabular signal files, trained models, generated results, temporary files, virtual environments, and private folders.

This is intentional to reduce the risk of accidentally publishing:

- Raw participant data.
- Consent forms.
- Identifiable metadata.
- Heavy intermediate files.
- Trained models derived from restricted data.
- Local paths or private configuration files.
