from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Literal

from models.entry import SubtitleEntry, SubtitleFile


class MergeConflictType(Enum):
    MISSING_PRIMARY = auto()
    MISSING_SECONDARY = auto()
    TIMESTAMP_MISMATCH = auto()


@dataclass
class MergeResult:
    merged_file: SubtitleFile
    conflicts: list[tuple[int, MergeConflictType, str]] = field(default_factory=list)


def merge(
    primary: SubtitleFile,
    secondary: SubtitleFile,
    *,
    timestamp_source: Literal["primary", "secondary"] = "primary",
    ordering: Literal["primary_first", "secondary_first"] = "primary_first",
    on_entry_count_mismatch: Literal["warn_pad", "truncate"] = "warn_pad",
    timestamp_tolerance_ms: int = 100,
    header_source: Literal["primary", "secondary"] = "primary",
) -> MergeResult:
    """
    Merge two monolingual subtitle files into one bilingual file.
    Entries are matched by index number.
    """
    # Build index -> entry maps
    primary_map: dict[int, SubtitleEntry] = {e.index: e for e in primary.entries}
    secondary_map: dict[int, SubtitleEntry] = {e.index: e for e in secondary.entries}

    all_indices = sorted(set(primary_map.keys()) | set(secondary_map.keys()))
    merged_entries = []
    conflicts = []
    tolerance = abs(timestamp_tolerance_ms)  # ms

    for idx in all_indices:
        p_entry = primary_map.get(idx)
        s_entry = secondary_map.get(idx)

        if p_entry is None:
            conflicts.append((idx, MergeConflictType.MISSING_PRIMARY, "Primary missing"))
            if on_entry_count_mismatch == "truncate":
                break
            # Pad: use secondary as-is, empty primary line
            p_entry = SubtitleEntry(
                index=idx,
                start_time=s_entry.start_time,
                end_time=s_entry.end_time,
                lines=[""],
                metadata={},
            )

        if s_entry is None:
            conflicts.append((idx, MergeConflictType.MISSING_SECONDARY, "Secondary missing"))
            if on_entry_count_mismatch == "truncate":
                break
            s_entry = SubtitleEntry(
                index=idx,
                start_time=p_entry.start_time,
                end_time=p_entry.end_time,
                lines=[""],
                metadata={},
            )

        # Timestamp check
        start_diff = abs((p_entry.start_time - s_entry.start_time).total_seconds() * 1000)
        end_diff = abs((p_entry.end_time - s_entry.end_time).total_seconds() * 1000)
        max_diff = max(start_diff, end_diff)

        if max_diff > tolerance:
            conflicts.append((
                idx, MergeConflictType.TIMESTAMP_MISMATCH,
                f"Start diff: {start_diff:.0f}ms, End diff: {end_diff:.0f}ms"
            ))

        # Determine timestamps
        if timestamp_source == "primary":
            start_time, end_time = p_entry.start_time, p_entry.end_time
        else:
            start_time, end_time = s_entry.start_time, s_entry.end_time

        # Combine lines
        if ordering == "primary_first":
            combined_lines = p_entry.lines + s_entry.lines
        else:
            combined_lines = s_entry.lines + p_entry.lines

        merged_entries.append(SubtitleEntry(
            index=idx,
            start_time=start_time,
            end_time=end_time,
            lines=combined_lines,
        ))

    header = primary.header if header_source == "primary" else secondary.header

    return MergeResult(
        merged_file=SubtitleFile(entries=merged_entries, format=primary.format, header=header),
        conflicts=conflicts,
    )
