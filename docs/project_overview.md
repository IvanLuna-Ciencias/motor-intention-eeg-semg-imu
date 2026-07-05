# Project overview

## Title

Multimodal EEG–sEMG–IMU pipeline for upper-limb motor intention detection and exoskeleton-oriented human–robot interfaces.

## Research context

This project focuses on the detection of upper-limb motor intention using multimodal biomedical and inertial signals. The system is designed around non-invasive acquisition modalities, including EEG, sEMG, and IMU signals, with the long-term goal of supporting assistive robotic interfaces such as upper-limb exoskeletons.

## General objective

To develop a multimodal signal-processing and machine-learning pipeline for detecting motor intention in upper-limb movements using EEG, sEMG, and IMU signals.

## Main components

The project is organized around the following stages:

1. Signal acquisition.
2. Temporal synchronization.
3. Signal preprocessing.
4. Feature extraction.
5. Hierarchical classification.
6. Offline evaluation.
7. Real-time-oriented inference and exoskeleton integration.

## Classification strategy

The planned classification architecture follows a hierarchical approach:

- **L1 classifier:** rest vs movement intention.
- **L2 classifier:** movement class discrimination after movement intention is detected.

This structure is intended to reduce the complexity of direct multiclass classification and to better represent an assistive control scenario.

## Application scope

The project is oriented toward:

- Biomedical signal processing.
- Human–machine interfaces.
- Human–robot interaction.
- Assistive robotics.
- Upper-limb exoskeleton control.
- Real-time motor intention detection.

## Repository purpose

This repository provides a clean, documented, and scalable version of the project. It is not intended to contain raw participant data or private institutional files.

The initial version provides the base structure for future migration of cleaned scripts, reusable modules, configuration files, and reproducible experiments.
