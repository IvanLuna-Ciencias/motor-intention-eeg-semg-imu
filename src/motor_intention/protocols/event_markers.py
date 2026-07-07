"""Experimental event markers and movement labels.

This module defines the hardware-independent event markers, trial phases,
movement codes, and label conventions used by the acquisition protocol.

The definitions here are intentionally independent from MindRove,
Biosignalsplux, MYO, LabVIEW, or cRIO-specific code.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


# ---------------------------------------------------------------------
# Trial phases
# ---------------------------------------------------------------------

PHASE_DURATIONS_SEC: Dict[str, float] = {
    "alert": 1.0,
    "prep": 2.0,
    "execute": 2.0,
    "hold": 2.0,
    "rest": 1.0,
}

PHASE_ORDER: Tuple[str, ...] = (
    "alert",
    "prep",
    "execute",
    "hold",
    "rest",
)

PHASE_MARKERS: Dict[str, float] = {
    "alert": 10.0,
    "prep": 11.0,
    "execute": 12.0,
    "hold": 13.0,
    "rest": 14.0,
}

START_PROTOCOL_MARKER: float = 88.0
MANUAL_STOP_MARKER: float = 99.0


# ---------------------------------------------------------------------
# Movement codes
# ---------------------------------------------------------------------

MOVEMENT_LABELS: Dict[str, str] = {
    "F": "elbow_flexion",
    "E": "elbow_extension",
    "FH": "shoulder_flexion",
    "EH": "shoulder_extension",
    "RInt": "shoulder_medial_rotation",
    "RExt": "shoulder_lateral_rotation",
}

MOVEMENT_DISPLAY_NAMES_ES: Dict[str, str] = {
    "F": "FLEXIÓN CODO",
    "E": "EXTENSIÓN CODO",
    "FH": "FLEXIÓN HOMBRO",
    "EH": "EXTENSIÓN HOMBRO",
    "RInt": "ROTACIÓN INTERNA HOMBRO",
    "RExt": "ROTACIÓN EXTERNA HOMBRO",
}

MOVEMENT_BLOCKS: Dict[str, Tuple[str, str]] = {
    "Codo": ("F", "E"),
    "Hombro": ("FH", "EH"),
    "RotHombro": ("RInt", "RExt"),
}


# ---------------------------------------------------------------------
# Class labels
# ---------------------------------------------------------------------

L1_LABELS: Dict[str, int] = {
    "rest": 0,
    "movement": 1,
}

L2_LABELS: Dict[str, int] = {
    "flexion": 0,
    "extension": 1,
}


@dataclass(frozen=True)
class EventMarker:
    """Single event marker record."""

    time_s: float
    marker: float
    label: str


def get_phase_marker(phase: str) -> float:
    """Return the numeric marker associated with a trial phase."""
    try:
        return PHASE_MARKERS[phase]
    except KeyError as exc:
        valid = ", ".join(PHASE_MARKERS)
        raise ValueError(f"Unknown phase '{phase}'. Valid phases: {valid}") from exc


def get_movement_display_name(movement_code: str) -> str:
    """Return a Spanish display name for a movement code."""
    try:
        return MOVEMENT_DISPLAY_NAMES_ES[movement_code]
    except KeyError as exc:
        valid = ", ".join(MOVEMENT_DISPLAY_NAMES_ES)
        raise ValueError(
            f"Unknown movement code '{movement_code}'. Valid codes: {valid}"
        ) from exc


def get_block_movements(movement_block: str) -> Tuple[str, str]:
    """Return the two movement codes associated with a movement block."""
    try:
        return MOVEMENT_BLOCKS[movement_block]
    except KeyError as exc:
        valid = ", ".join(MOVEMENT_BLOCKS)
        raise ValueError(
            f"Unknown movement block '{movement_block}'. Valid blocks: {valid}"
        ) from exc
