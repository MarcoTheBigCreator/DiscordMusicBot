"""Typed queue entries; temporary streams are never persisted."""

import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class State(StrEnum):
    IDLE = "idle"
    PREPARING = "preparing"
    PLAYING = "playing"
    PAUSED = "paused"


@dataclass
class Track:
    title: str
    original_url: str
    source: str = field(repr=False)
    # None explicitly invalidates a stream; zero can be a valid clock reading.
    resolved_at: float | None = field(default_factory=time.monotonic)


@dataclass
class QueueEntry:
    track: Track
    channel: Any
    requester: Any
    request_id: str = "-"
    received_at: float | None = None
    enqueued_at: float = field(default_factory=time.monotonic)

    @property
    def title(self):
        return self.track.title
