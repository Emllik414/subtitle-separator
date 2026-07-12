from copy import deepcopy
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
    """Merge two monolingual subtitle files into one bilingual file."""
    primary_map = {entry.index: entry for entry in primary.entries}
    secondary_map = {entry.index: entry for entry in secondary.entries}

    all_indices = sorted(set(primary_map) | set(secondary_map))
    merged_entries = []
    conflicts = []
    tolerance = abs(timestamp_tolerance_ms)

    for idx in all_indices:
        original_primary = primary_map.get(idx)
        original_secondary = secondary_map.get(idx)
        primary_entry = original_primary
        secondary_entry = original_secondary

        if primary_entry is None:
            conflicts.append((idx, MergeConflictType.MISSING_PRIMARY, "Primary missing"))
            if on_entry_count_mismatch == "truncate":
                break
            primary_entry = SubtitleEntry(
                index=idx,
                start_time=secondary_entry.start_time,
                end_time=secondary_entry.end_time,
                lines=[""],
                metadata={},
            )

        if secondary_entry is None:
            conflicts.append((idx, MergeConflictType.MISSING_SECONDARY, "Secondary missing"))
            if on_entry_count_mismatch == "truncate":
                break
            secondary_entry = SubtitleEntry(
                index=idx,
                start_time=primary_entry.start_time,
                end_time=primary_entry.end_time,
                lines=[""],
                metadata={},
            )

        start_diff = abs((primary_entry.start_time - secondary_entry.start_time).total_seconds() * 1000)
        end_diff = abs((primary_entry.end_time - secondary_entry.end_time).total_seconds() * 1000)
        max_diff = max(start_diff, end_diff)
        if max_diff > tolerance:
            conflicts.append((
                idx,
                MergeConflictType.TIMESTAMP_MISMATCH,
                f"Start diff: {start_diff:.0f}ms, End diff: {end_diff:.0f}ms",
            ))

        timestamp_entry = primary_entry if timestamp_source == "primary" else secondary_entry
        combined_lines = (
            primary_entry.lines + secondary_entry.lines
            if ordering == "primary_first"
            else secondary_entry.lines + primary_entry.lines
        )

        preferred = original_primary if header_source == "primary" else original_secondary
        fallback = original_secondary if header_source == "primary" else original_primary
        metadata_source = preferred or fallback
        metadata = deepcopy(metadata_source.metadata) if metadata_source else {}

        merged_entries.append(SubtitleEntry(
            index=idx,
            start_time=timestamp_entry.start_time,
            end_time=timestamp_entry.end_time,
            lines=combined_lines,
            metadata=metadata,
        ))

    header_file = primary if header_source == "primary" else secondary
    return MergeResult(
        merged_file=SubtitleFile(
            entries=merged_entries,
            format=primary.format,
            header=header_file.header,
        ),
        conflicts=conflicts,
    )
