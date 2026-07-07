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
