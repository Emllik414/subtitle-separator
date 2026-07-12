import re
from datetime import timedelta


def parse_srt_timestamp(s: str) -> timedelta:
    """Parse HH:MM:SS,mmm or HH:MM:ss,msec format to timedelta."""
    m = re.match(r"(\d+):(\d{2}):(\d{2})[,.](\d{3})", s.strip())
    if not m:
        raise ValueError(f"Invalid SRT timestamp: {s!r}")
    h, mi, sec, ms = int(m[1]), int(m[2]), int(m[3]), int(m[4])
    return timedelta(hours=h, minutes=mi, seconds=sec, milliseconds=ms)


def parse_ass_timestamp(s: str) -> timedelta:
    """Parse H:MM:SS.cc (centiseconds) or H:MM:SS.ms format to timedelta."""
    m = re.match(r"(-?\d+):(\d{2}):(\d{2})[.,](\d{2,3})", s.strip())
    if not m:
        raise ValueError(f"Invalid ASS timestamp: {s!r}")
    h, mi, sec, frac = int(m[1]), int(m[2]), int(m[3]), int(m[4])
    if len(m[4]) == 2:
        frac *= 10  # centiseconds -> milliseconds
    sign = -1 if h < 0 else 1
    h = abs(h)
    return timedelta(hours=h, minutes=mi, seconds=sec, milliseconds=frac) if sign == 1 else timedelta(
        hours=-h, minutes=-mi, seconds=-sec, milliseconds=-frac
    )


def parse_vtt_timestamp(s: str) -> timedelta:
    """Parse HH:MM:SS.mmm or MM:SS.mmm format to timedelta."""
    s = s.strip()
    m = re.match(r"(\d+):(\d{2}):(\d{2})[.,](\d{3})", s)
    if m:
        h, mi, sec, ms = int(m[1]), int(m[2]), int(m[3]), int(m[4])
        return timedelta(hours=h, minutes=mi, seconds=sec, milliseconds=ms)
    m = re.match(r"(\d+):(\d{2})[.,](\d{3})", s)
    if m:
        mi, sec, ms = int(m[1]), int(m[2]), int(m[3])
        return timedelta(minutes=mi, seconds=sec, milliseconds=ms)
    raise ValueError(f"Invalid VTT timestamp: {s!r}")


def format_srt_timestamp(td: timedelta) -> str:
    total_ms = int(td.total_seconds() * 1000)
    if total_ms < 0:
        total_ms = 0
    h = total_ms // 3600000
    m = (total_ms % 3600000) // 60000
    s = (total_ms % 60000) // 1000
    ms = total_ms % 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def format_ass_timestamp(td: timedelta) -> str:
    total_ms = int(td.total_seconds() * 1000)
    if total_ms < 0:
        total_ms = 0
    h = total_ms // 3600000
    m = (total_ms % 3600000) // 60000
    s = (total_ms % 60000) // 1000
    cs = (total_ms % 1000) // 10
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def format_vtt_timestamp(td: timedelta) -> str:
    total_ms = int(td.total_seconds() * 1000)
    if total_ms < 0:
        total_ms = 0
    h = total_ms // 3600000
    m = (total_ms % 3600000) // 60000
    s = (total_ms % 60000) // 1000
    ms = total_ms % 1000
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"
