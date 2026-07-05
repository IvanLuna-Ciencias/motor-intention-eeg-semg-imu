# Data

This directory does not contain raw participant data.

Raw biomedical data, consent forms, identifiable metadata, and private institutional files must not be committed to this repository.

## Public data policy

Only synthetic, anonymized, or minimal example files may be included for demonstration purposes.

The complete dataset is not publicly distributed due to privacy, ethical, and institutional restrictions.

Access to the full dataset may be considered under reasonable request to the research group and subject to:

- Institutional approval.
- Ethical requirements.
- Participant privacy protection.
- Data-sharing agreements.
- Research purpose and scope.
- Availability of an anonymized or restricted version of the dataset.

## Intended local-only folders

The following folders may exist locally but are ignored by Git:

```text
data/raw/
data/interim/
data/processed/
data/external/
data/private/
data/consents/
data/participants/
data/identifiable/
```

These folders should remain outside public version control.

## Public sample folder

The only data folder intended for public examples is:

```text
data/sample/
```

This folder may contain synthetic, anonymized, or minimal example files that demonstrate the expected input structure.

## Do not commit

Do not commit:

- Raw EEG recordings.
- Raw sEMG recordings.
- Raw IMU recordings.
- Full participant sessions.
- Consent forms.
- Personal information.
- Participant names.
- Clinical or sensitive metadata.
- Internal institutional documents.
- Large processed matrices.
- Full trained models derived from restricted data.
- Temporary outputs.
- Local paths.

## Recommended practice

Before every commit, run:

```bash
git status
```

If any real data file appears as tracked or staged, remove it before committing.
