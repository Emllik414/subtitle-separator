import re

from .base import AbstractParser
from models.entry import SubtitleEntry, SubtitleFile
from models.enums import SubtitleFormat
from utils.time_utils import parse_vtt_timestamp, format_vtt_timestamp


class VttParser(AbstractParser):
    @staticmethod
    def parse(raw_text: str) -> SubtitleFile:
        entries = []
        lines = raw_text.split("\n")

        # Extract header: everything before first blank line or first cue
        header_end = 0
        for i, line in enumerate(lines):
            if line.strip() == "" and i > 0:
                header_end = i
                break
        else:
            header_end = 0

        header = "\n".join(lines[:header_end])

        # Parse cues
        body_start = header_end + 1 if header_end < len(lines) else header_end
        body_lines = lines[body_start:]
        i = 0
        index = 1

        while i < len(body_lines):
            # Skip blank lines
            while i < len(body_lines) and body_lines[i].strip() == "":
                i += 1
            if i >= len(body_lines):
                break

            # Optional cue identifier
            identifier = ""
            cue_line = body_lines[i].strip()
            if "-->" not in cue_line and cue_line:
                identifier = cue_line
                i += 1
                if i >= len(body_lines):
                    break
                cue_line = body_lines[i].strip()

            # Timestamp line
            ts_match = re.match(
                r"([\d:.,]+\s*-->\s*[\d:.,]+)",
                cue_line
            )
            if not ts_match:
                i += 1
                continue

            ts_parts = re.split(r"\s*-->\s*", ts_match.group(1))
            if len(ts_parts) != 2:
                i += 1
                continue

            start = parse_vtt_timestamp(ts_parts[0])
            end = parse_vtt_timestamp(ts_parts[1])

            # Optional cue settings on same line
            cue_settings = cue_line[ts_match.end():].strip()

            i += 1
            # Collect text lines until blank line
            text_lines = []
            while i < len(body_lines) and body_lines[i].strip() != "":
                text_lines.append(body_lines[i].strip())
                i += 1

            metadata: dict = {}
            if identifier:
                metadata["identifier"] = identifier
            if cue_settings:
                metadata["cue_settings"] = cue_settings

            entries.append(SubtitleEntry(
                index=index,
                start_time=start,
                end_time=end,
                lines=text_lines,
                metadata=metadata,
            ))
            index += 1

        return SubtitleFile(entries=entries, format=SubtitleFormat.VTT, header=header)

    @staticmethod
    def write(sub_file: SubtitleFile) -> str:
        parts = []

        # Header
        if sub_file.header:
            parts.append(sub_file.header.strip())
        else:
            parts.append("WEBVTT")

        parts.append("")
        parts.append("")

        for entry in sub_file.entries:
            # Cue identifier
            identifier = entry.metadata.get("identifier", "")
            if identifier:
                parts.append(identifier)

            # Timestamp
            start = format_vtt_timestamp(entry.start_time)
            end = format_vtt_timestamp(entry.end_time)
            ts_line = f"{start} --> {end}"

            cue_settings = entry.metadata.get("cue_settings", "")
            if cue_settings:
                ts_line += " " + cue_settings

            parts.append(ts_line)

            # Text lines
            for line in entry.lines:
                parts.append(line)

            parts.append("")  # blank line separator

        return "\n".join(parts)
