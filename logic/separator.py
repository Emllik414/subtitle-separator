from dataclasses import dataclass, field
from copy import deepcopy

from models.entry import SubtitleEntry, SubtitleFile


@dataclass
class SeparationResult:
    lang1_file: SubtitleFile
    lang2_file: SubtitleFile
    ambiguous_entries: list[int] = field(default_factory=list)
    empty_entries: list[int] = field(default_factory=list)


def separate(
    sub_file: SubtitleFile,
    lang1_line_index: int,
    lang2_line_index: int,
) -> SeparationResult:
    """
    Split a bilingual subtitle file into two monolingual files.

    lang1_line_index: which line in each entry belongs to language 1 (e.g. Chinese)
    lang2_line_index: which line in each entry belongs to language 2 (e.g. English)
    """
    lang1_entries = []
    lang2_entries = []
    ambiguous = []
    empty = []

    for entry in sub_file.entries:
        line_count = len(entry.lines)
        max_idx = max(lang1_line_index, lang2_line_index)

        if line_count == 0:
            empty.append(entry.index)
            lang1_line = ""
            lang2_line = ""
        elif line_count <= max_idx:
            empty.append(entry.index)
            lang1_line = entry.lines[lang1_line_index] if lang1_line_index < line_count else ""
            lang2_line = entry.lines[lang2_line_index] if lang2_line_index < line_count else ""
        else:
            lang1_line = entry.lines[lang1_line_index]
            lang2_line = entry.lines[lang2_line_index]

        lang1_entries.append(SubtitleEntry(
            index=entry.index,
            start_time=entry.start_time,
            end_time=entry.end_time,
            lines=[lang1_line] if lang1_line else [],
            metadata=deepcopy(entry.metadata),
        ))
        lang2_entries.append(SubtitleEntry(
            index=entry.index,
            start_time=entry.start_time,
            end_time=entry.end_time,
            lines=[lang2_line] if lang2_line else [],
            metadata=deepcopy(entry.metadata),
        ))

    return SeparationResult(
        lang1_file=SubtitleFile(entries=lang1_entries, format=sub_file.format, header=sub_file.header),
        lang2_file=SubtitleFile(entries=lang2_entries, format=sub_file.format, header=sub_file.header),
        ambiguous_entries=ambiguous,
        empty_entries=empty,
    )
