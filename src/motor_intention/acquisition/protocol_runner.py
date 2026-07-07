"""Protocol runner for acquisition sessions.

This module coordinates the timed experimental protocol independently from
hardware-specific acquisition devices.

It can run in deterministic non-realtime mode for tests, or in realtime mode
for future acquisition scripts.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

from motor_intention.protocols.trial_protocol import (
    TrialProtocol,
    build_trial_list,
    estimate_protocol_duration_sec,
)


EventRow = Tuple[float, float, str]
EventCallback = Callable[[float, float, str], None]


@dataclass(frozen=True)
class ProtocolRunnerConfig:
    """Configuration for a timed acquisition protocol run."""

    movement_block: str
    total_trials: int = 40
    seed: Optional[int] = None
    realtime: bool = False
    time_scale: float = 1.0

    def __post_init__(self) -> None:
        """Validate protocol runner configuration."""
        if self.total_trials <= 0:
            raise ValueError("total_trials must be greater than zero.")

        if self.total_trials % 2 != 0:
            raise ValueError("total_trials must be even.")

        if self.time_scale <= 0:
            raise ValueError("time_scale must be greater than zero.")


@dataclass(frozen=True)
class ProtocolRunnerResult:
    """Result returned after a protocol run."""

    trial_list: List[str]
    events: List[EventRow]
    estimated_duration_sec: float
    executed_duration_sec: float
    realtime: bool


class ProtocolRunner:
    """Run a trial protocol and emit event callbacks."""

    def __init__(
        self,
        config: ProtocolRunnerConfig,
        event_callbacks: Optional[List[EventCallback]] = None,
        sleep_fn: Callable[[float], None] = time.sleep,
    ) -> None:
        self.config = config
        self.event_callbacks = event_callbacks or []
        self.sleep_fn = sleep_fn

    def run(self) -> ProtocolRunnerResult:
        """Run the protocol and return generated events."""
        trial_list = build_trial_list(
            movement_block=self.config.movement_block,
            total_trials=self.config.total_trials,
            seed=self.config.seed,
        )

        protocol = TrialProtocol(trial_list=trial_list)

        emitted_count = 0
        current_time_s = 0.0

        def emit_new_events() -> List[EventRow]:
            nonlocal emitted_count

            rows = protocol.as_event_rows()
            new_rows = rows[emitted_count:]
            emitted_count = len(rows)

            for time_s, marker, label in new_rows:
                for callback in self.event_callbacks:
                    callback(time_s, marker, label)

            return new_rows

        all_events: List[EventRow] = []

        protocol.start(time_s=current_time_s)
        all_events.extend(emit_new_events())

        while not protocol.is_finished:
            phase_duration = protocol.get_phase_duration()

            if self.config.realtime:
                self.sleep_fn(phase_duration * self.config.time_scale)

            current_time_s += phase_duration
            protocol.advance_phase(time_s=current_time_s)
            all_events.extend(emit_new_events())

        estimated_duration = estimate_protocol_duration_sec(self.config.total_trials)

        return ProtocolRunnerResult(
            trial_list=trial_list,
            events=all_events,
            estimated_duration_sec=estimated_duration,
            executed_duration_sec=current_time_s,
            realtime=self.config.realtime,
        )
