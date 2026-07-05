# Sample data

This folder is reserved for synthetic, anonymized, or minimal example data.

Files in this folder should only be used to demonstrate:

- Expected file names.
- Expected columns.
- Expected timestamps.
- Expected event markers.
- Expected metadata structure.
- Expected input/output organization.

No real identifiable participant data should be stored here.

## Allowed examples

Allowed public examples may include:

```text
synthetic_eeg.csv
synthetic_semg_biosignals.csv
synthetic_myo.csv
synthetic_events.csv
example_metadata.json
```

These files should be small and clearly documented.

## Example EEG columns

```text
time_s,ch_0,ch_1,ch_2,ch_3,ch_4,ch_5
```

## Example Biosignalsplux sEMG columns

```text
time_s,emg_0,emg_1
```

## Example MYO columns

```text
time_s,emg_0,emg_1,emg_2,emg_3,emg_4,emg_5,emg_6,emg_7,accel_0,accel_1,accel_2,gyro_0,gyro_1,gyro_2
```

## Example event columns

```text
time_s,marker,label,trial,phase,movement
```

## Important restriction

Any sample derived from real recordings must be fully anonymized and approved for public release before being committed.

When in doubt, use synthetic data.
