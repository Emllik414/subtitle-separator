from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta

from models.enums import SubtitleFormat


@dataclass
class SubtitleEntry:
    index: int
    start_time: timedelta
    end_time: timedelta
    lines: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class SubtitleFile:
    entries: list[SubtitleEntry] = field(default_factory=list)
    format: SubtitleFormat = SubtitleFormat.SRT
    header: str = ""
