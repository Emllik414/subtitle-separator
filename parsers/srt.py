from datetime import timedelta

from .base import AbstractParser
from models.entry import SubtitleEntry, SubtitleFile
from models.enums import SubtitleFormat
from utils.time_utils import parse_srt_timestamp, format_srt_timestamp


class SrtParser(AbstractParser):
    @staticmethod
    def parse(raw_text: str) -> SubtitleFile:
        entries = []
        blocks = raw_text.strip().split("\n\n")
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            lines = block.split("\n")
            if len(lines) < 2:
                continue

            # Line 0: index (or optional cue id + index)
            idx_line = 0
            # Some SRT files have a cue identifier before the index
            while idx_line < len(lines) and not lines[idx_line].isdigit():
                idx_line += 1
            if idx_line >= len(lines):
                continue
            index = int(lines[idx_line])

            # Line idx_line+1: timestamp
            ts_line = lines[idx_line + 1] if idx_line + 1 < len(lines) else ""
            ts_parts = ts_line.split("-->")
            if len(ts_parts) != 2:
                continue
            start = parse_srt_timestamp(ts_parts[0])
            end = parse_srt_timestamp(ts_parts[1])

            # Remaining lines: subtitle text
            text_lines = lines[idx_line + 2:] if idx_line + 2 < len(lines) else []
            entries.append(SubtitleEntry(
                index=index,
                start_time=start,
                end_time=end,
                lines=text_lines,
            ))

        return SubtitleFile(entries=entries, format=SubtitleFormat.SRT)

    @staticmethod
    def write(sub_file: SubtitleFile) -> str:
        parts = []
        for i, entry in enumerate(sub_file.entries):
            parts.append(str(i + 1))
            start = format_srt_timestamp(entry.start_time)
            end = format_srt_timestamp(entry.end_time)
            parts.append(f"{start} --> {end}")
            for line in entry.lines:
                parts.append(line)
            parts.append("")  # blank line separator
        return "\n".join(parts)
