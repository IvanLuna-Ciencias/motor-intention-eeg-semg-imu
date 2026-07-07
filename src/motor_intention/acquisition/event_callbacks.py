"""Event callbacks for acquisition protocol execution.

These callbacks connect protocol events with recorders or hardware-like devices.
They are intentionally small and testable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Tuple


EventRow = Tuple[float, float, str]


@dataclass
class ProtocolEventRecorder:
    """Record protocol events emitted by ProtocolRunner."""

    events: List[EventRow] = field(default_factory=list)

    def __call__(self, time_s: float, marker: float, label: str) -> None:
        """Record one event."""
        self.events.append((float(time_s), float(marker), str(label)))

    def as_event_rows(self) -> List[EventRow]:
        """Return recorded events."""
        return list(self.events)

    def clear(self) -> None:
        """Clear recorded events."""
        self.events.clear()


@dataclass
class DeviceMarkerCallback:
    """Forward protocol markers to a device method.

    The device is expected to expose a marker method, for example:

    - insert_marker(marker)
    - send_marker(marker)

    For MindRove, the expected method is insert_marker(marker).
    """

    device: Any
    method_name: str = "insert_marker"
    inserted_markers: List[float] = field(default_factory=list)

    def __call__(self, time_s: float, marker: float, label: str) -> None:
        """Send one marker to the configured device method."""
        method = getattr(self.device, self.method_name)
        method(float(marker))
        self.inserted_markers.append(float(marker))
