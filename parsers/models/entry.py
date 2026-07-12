from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from .enums import SubtitleFormat


@dataclass
class SubtitleEntry:
    index: int
    start_time: timedelta
    end_time: timedelta
    lines: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SubtitleFile:
    entries: list[SubtitleEntry]
    format: SubtitleFormat
    header: str = ""
