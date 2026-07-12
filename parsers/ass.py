import re
from datetime import timedelta

from .base import AbstractParser
from models.entry import SubtitleEntry, SubtitleFile
from models.enums import SubtitleFormat
from utils.time_utils import parse_ass_timestamp, format_ass_timestamp


class AssParser(AbstractParser):
    @staticmethod
    def parse(raw_text: str) -> SubtitleFile:
        entries = []
        in_events = False
        format_fields: list[str] = []
        header_lines = []

        for line in raw_text.split("\n"):
            stripped = line.strip()

            if not in_events:
                header_lines.append(line)
                if stripped.lower().startswith("[events]"):
                    in_events = True
                continue

            if stripped.startswith("Format:"):
                # Parse format definition
                fmt_str = stripped[len("Format:"):].strip()
                format_fields = [f.strip() for f in fmt_str.split(",")]
                header_lines.append(line)
                continue

            if stripped.startswith("Dialogue:") or stripped.startswith("Comment:"):
                # Parse dialogue/comment line
                content = stripped[stripped.index(":") + 1:].strip()
                # Split respecting ASS comma escaping (\,)
                fields = _split_ass_fields(content, len(format_fields))

                if len(fields) < 3:
                    header_lines.append(line)
                    continue

                # Build field name -> value map
                field_map: dict[str, str] = {}
                for i, name in enumerate(format_fields):
                    if i < len(fields):
                        field_map[name.lower()] = fields[i]
                    else:
                        field_map[name.lower()] = ""

                start_str = field_map.get("start", "")
                end_str = field_map.get("end", "")
                if not start_str or not end_str:
                    header_lines.append(line)
                    continue

                start = parse_ass_timestamp(start_str)
                end = parse_ass_timestamp(end_str)
                text = field_map.get("text", "")
                text_lines = text.split("\\N")

                idx = len(entries) + 1  # sequential, 1-based

                metadata: dict = {}
                # Store original layer in metadata for round-trip
                layer_str = field_map.get("layer", "0")
                metadata["layer"] = layer_str
                for key in ("style", "actor", "marginl", "marginr", "marginv", "effect"):
                    if key in field_map:
                        metadata[key] = field_map[key]

                entries.append(SubtitleEntry(
                    index=idx,
                    start_time=start,
                    end_time=end,
                    lines=text_lines,
                    metadata=metadata,
                ))
            else:
                # Preserve non-dialogue lines in [Events] (like empty lines or comments)
                if stripped:
                    header_lines.append(line)

        header = "\n".join(header_lines)
        return SubtitleFile(entries=entries, format=SubtitleFormat.ASS, header=header)

    @staticmethod
    def write(sub_file: SubtitleFile) -> str:
        parts = []
        header = sub_file.header

        # Split header into pre-format and format parts
        header_lines = header.split("\n")
        format_line_idx = -1
        format_fields = []
        for i, line in enumerate(header_lines):
            if line.strip().startswith("Format:") and i >= _find_events_section(header_lines):
                format_line_idx = i
                fmt_str = line.strip()[len("Format:"):].strip()
                format_fields = [f.strip() for f in fmt_str.split(",")]
                break

        if not format_fields:
            # Reconstruct events section
            parts.append(header)
            parts.append("")
            parts.append("[Events]")
            parts.append("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text")
            format_fields = ["Layer", "Start", "End", "Style", "Name", "MarginL", "MarginR", "MarginV", "Effect", "Text"]
            format_line_idx = -1

        # Write header up to and including Format line
        for i, line in enumerate(header_lines):
            if i <= format_line_idx or format_line_idx == -1:
                parts.append(line)
            if i == format_line_idx:
                break
        if format_line_idx == -1:
            parts.append("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text")

        # Write dialogue entries
        for entry in sub_file.entries:
            field_values = _build_ass_fields(entry, format_fields)
            parts.append("Dialogue: " + ",".join(field_values))

        return "\n".join(parts)


def _find_events_section(lines: list[str]) -> int:
    for i, line in enumerate(lines):
        if line.strip().lower().startswith("[events]"):
            return i
    return len(lines)


def _split_ass_fields(content: str, num_fields: int | None = None) -> list[str]:
    """Split ASS dialogue fields respecting backslash-comma escaping.

    If num_fields is provided, limits splits to produce exactly that many
    fields -- the last field (Text) retains any embedded commas.
    """
    result = []
    current = ""
    i = 0
    splits_remaining = max(num_fields - 1, 0) if num_fields else -1
    while i < len(content):
        if content[i] == "\\" and i + 1 < len(content) and content[i + 1] == ",":
            current += ","
            i += 2
        elif splits_remaining == 0:
            current += content[i:]
            break
        elif content[i] == ",":
            result.append(current.strip())
            current = ""
            i += 1
            if splits_remaining > 0:
                splits_remaining -= 1
        else:
            current += content[i]
            i += 1
    result.append(current.strip())
    if num_fields:
        while len(result) < num_fields:
            result.append("")
    return result


def _escape_ass_text(text: str) -> str:
    """Escape commas and newlines for ASS Text field."""
    return text.replace(",", "\\,")


def _build_ass_fields(entry: SubtitleEntry, format_fields: list[str]) -> list[str]:
    """Build comma-separated field values from an entry, respecting ASS format."""
    field_lower = [f.lower().strip() for f in format_fields]
    values: dict[str, str] = {}
    for key in ("style", "actor", "marginl", "marginr", "marginv", "effect"):
        values[key] = str(entry.metadata.get(key, ""))
    values["text"] = "\\N".join(entry.lines) if entry.lines else ""
    values["start"] = format_ass_timestamp(entry.start_time)
    values["end"] = format_ass_timestamp(entry.end_time)
    values["layer"] = str(entry.metadata.get("layer", entry.index - 1 if entry.index > 0 else 0))
    values["name"] = ""
    values["marginl"] = values.get("marginl", "0")
    values["marginr"] = values.get("marginr", "0")
    values["marginv"] = values.get("marginv", "0")
    values["effect"] = values.get("effect", "")

    result = []
    for f in field_lower:
        val = values.get(f, "")
        if f == "text":
            val = _escape_ass_text(val)
        result.append(val)
    return result
