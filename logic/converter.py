import os

from models.entry import SubtitleFile
from models.enums import SubtitleFormat
from parsers.base import detect_format, get_parser
from utils.text import (
    ensure_extension,
    paths_equal,
    read_subtitle_file,
    strip_ass_tags,
    write_subtitle_file,
)


FORMAT_EXTENSIONS = {
    SubtitleFormat.SRT: ".srt",
    SubtitleFormat.ASS: ".ass",
    SubtitleFormat.SSA: ".ssa",
    SubtitleFormat.VTT: ".vtt",
}


def resolved_conversion_output_path(output_path: str, target_format: SubtitleFormat) -> str:
    return ensure_extension(output_path, FORMAT_EXTENSIONS[target_format])


def _needs_ass_tag_stripping(source_format: SubtitleFormat, target_format: SubtitleFormat) -> bool:
    return (
        source_format in (SubtitleFormat.ASS, SubtitleFormat.SSA)
        and target_format not in (SubtitleFormat.ASS, SubtitleFormat.SSA)
    )


def _unescape_ass_text(text: str) -> str:
    text = text.replace("\\,", ",")
    text = text.replace("\\h", " ")
    text = text.replace("\\n", "\n")
    text = text.replace("\\\\", "\\")
    return text


def convert_subtitle(input_path: str, output_path: str, target_format: SubtitleFormat) -> str:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    resolved_output = resolved_conversion_output_path(output_path, target_format)
    if paths_equal(input_path, resolved_output):
        raise ValueError("Output file must be different from the source file")

    raw_text, encoding, newline = read_subtitle_file(input_path)
    source_format = detect_format(raw_text)
    parser_cls = get_parser(source_format)
    sub_file: SubtitleFile = parser_cls.parse(raw_text)

    if _needs_ass_tag_stripping(source_format, target_format):
        for entry in sub_file.entries:
            entry.lines = [_unescape_ass_text(strip_ass_tags(line)) for line in entry.lines]

    if target_format == SubtitleFormat.VTT:
        sub_file.header = sub_file.header if source_format == SubtitleFormat.VTT else "WEBVTT"
    elif target_format not in (SubtitleFormat.ASS, SubtitleFormat.SSA):
        sub_file.header = ""

    sub_file.format = target_format
    writer_cls = get_parser(target_format)
    output_text = writer_cls.write(sub_file)
    write_subtitle_file(
        resolved_output,
        output_text,
        encoding=encoding,
        newline=newline,
    )

    return (
        f"Converted {source_format.name} ({len(sub_file.entries)} entries) "
        f"to {target_format.name} -> {os.path.basename(resolved_output)}"
    )
