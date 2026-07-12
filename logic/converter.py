import os
from models.entry import SubtitleFile
from models.enums import SubtitleFormat
from parsers.base import detect_format, get_parser
from utils.text import read_subtitle_file, write_subtitle_file, strip_ass_tags


DEFAULT_ASS_HEADER = """[Script Info]
; Converted by Bilingual Subtitle Tool
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def _get_default_header(target_format: SubtitleFormat) -> str:
    if target_format == SubtitleFormat.SSA:
        return DEFAULT_ASS_HEADER.replace("[V4+ Styles]", "[V4 Styles]")
    return DEFAULT_ASS_HEADER


def _needs_ass_tag_stripping(source_format: SubtitleFormat, target_format: SubtitleFormat) -> bool:
    is_ass_source = source_format in (SubtitleFormat.ASS, SubtitleFormat.SSA)
    is_ass_target = target_format in (SubtitleFormat.ASS, SubtitleFormat.SSA)
    return is_ass_source and not is_ass_target


def _unescape_ass_text(text: str) -> str:
    """Unescape ASS escape sequences back to literal characters.
    ASS uses:
      \\, -> ,   (comma)
      \\N -> line break (already split into lines by parser)
      \\n -> line break (same as \\N in newer spec)
      \\h -> hard space
      \\\\ -> \\
    """
    text = text.replace("\\,", ",")
    text = text.replace("\\\\", "\\")
    text = text.replace("\\h", " ")
    text = text.replace("\\n", "\n")
    return text


def convert_subtitle(input_path: str, output_path: str, target_format: SubtitleFormat) -> str:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    raw_text, encoding, nl = read_subtitle_file(input_path)
    source_format = detect_format(raw_text)

    parser_cls = get_parser(source_format)
    sub_file: SubtitleFile = parser_cls.parse(raw_text)

    if _needs_ass_tag_stripping(source_format, target_format):
        for entry in sub_file.entries:
            entry.lines = [strip_ass_tags(line) for line in entry.lines]
            entry.lines = [_unescape_ass_text(line) for line in entry.lines]

    if target_format in (SubtitleFormat.ASS, SubtitleFormat.SSA):
        if source_format not in (SubtitleFormat.ASS, SubtitleFormat.SSA):
            sub_file.header = _get_default_header(target_format)
        else:
            if target_format == SubtitleFormat.SSA:
                sub_file.header = sub_file.header.replace("[V4+ Styles]", "[V4 Styles]")
            elif target_format == SubtitleFormat.ASS:
                sub_file.header = sub_file.header.replace("[V4 Styles]", "[V4+ Styles]")
    else:
        if target_format == SubtitleFormat.VTT and not sub_file.header:
            sub_file.header = "WEBVTT"
        else:
            sub_file.header = ""

    sub_file.format = target_format
    writer_cls = get_parser(target_format)
    output_text = writer_cls.write(sub_file)

    ext_map = {
        SubtitleFormat.SRT: ".srt",
        SubtitleFormat.ASS: ".ass",
        SubtitleFormat.SSA: ".ssa",
        SubtitleFormat.VTT: ".vtt",
    }
    expected_ext = ext_map[target_format]
    if not output_path.lower().endswith(expected_ext):
        output_path += expected_ext

    write_subtitle_file(output_path, output_text, encoding=encoding, newline=nl)

    source_name = source_format.name
    target_name = target_format.name
    count = len(sub_file.entries)

    return f"Converted {source_name} ({count} entries) to {target_name} -> {os.path.basename(output_path)}"
