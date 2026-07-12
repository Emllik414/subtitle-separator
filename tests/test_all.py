"""Portable regression suite for the bilingual subtitle tool."""

from __future__ import annotations

import codecs
import os
import sys
import tempfile
from datetime import timedelta
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import gui.i18n_extra  # noqa: F401
from gui.preview_table import PREVIEW_ROW_LIMIT, PreviewTable
from language.detector import LanguageGroup, classify_line
from logic.converter import convert_subtitle, resolved_conversion_output_path
from logic.merger import MergeConflictType, merge
from logic.separator import separate
from models.entry import SubtitleEntry
from models.enums import SubtitleFormat
from parsers.ass import AssParser
from parsers.base import detect_format
from parsers.srt import SrtParser
from parsers.vtt import VttParser
from PySide6.QtWidgets import QApplication
from utils.text import (
    PendingWrite,
    ensure_extension,
    paths_equal,
    read_subtitle_file,
    strip_html_tags,
    write_subtitle_file,
    write_subtitle_files_atomically,
)
from utils.time_utils import (
    format_ass_timestamp,
    format_srt_timestamp,
    format_vtt_timestamp,
    parse_ass_timestamp,
    parse_srt_timestamp,
    parse_vtt_timestamp,
)


def _sample_bilingual_srt() -> str:
    return (
        "1\n"
        "00:00:01,000 --> 00:00:04,000\n"
        "Hello world\n"
        "你好世界\n\n"
        "2\n"
        "00:00:05,000 --> 00:00:08,500\n"
        "Goodbye\n"
        "再见\n"
    )


def test_srt_roundtrip():
    subtitle = SrtParser.parse(_sample_bilingual_srt())
    assert len(subtitle.entries) == 2
    assert subtitle.entries[0].lines == ["Hello world", "你好世界"]
    reparsed = SrtParser.parse(SrtParser.write(subtitle))
    assert reparsed.entries[0].lines == subtitle.entries[0].lines


def test_vtt_roundtrip():
    text = (
        "WEBVTT\n\n"
        "cue-1\n"
        "00:00:01.000 --> 00:00:04.000 align:start\n"
        "Hello world\n"
        "你好世界\n"
    )
    subtitle = VttParser.parse(text)
    assert subtitle.header.startswith("WEBVTT")
    reparsed = VttParser.parse(VttParser.write(subtitle))
    assert reparsed.entries[0].metadata["identifier"] == "cue-1"
    assert reparsed.entries[0].metadata["cue_settings"] == "align:start"


def test_ass_roundtrip_and_metadata():
    text = (
        "[Script Info]\n"
        "ScriptType: v4.00+\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize\n"
        "Style: Sign,Arial,20\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        "Dialogue: 2,0:00:01.00,0:00:04.00,Sign,Actor,1,2,3,fx,Hello\\N你好\n"
    )
    subtitle = AssParser.parse(text)
    assert subtitle.entries[0].metadata["style"] == "Sign"
    assert subtitle.entries[0].metadata["name"] == "Actor"
    reparsed = AssParser.parse(AssParser.write(subtitle))
    assert reparsed.entries[0].metadata["style"] == "Sign"
    assert reparsed.entries[0].metadata["layer"] == "2"


def test_ass_writer_builds_complete_header_once():
    subtitle = SrtParser.parse(_sample_bilingual_srt())
    subtitle.format = SubtitleFormat.ASS
    subtitle.header = ""
    output = AssParser.write(subtitle)
    assert output.count("[Script Info]") == 1
    assert output.count("[Events]") == 1
    assert output.count(
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    ) == 1


def test_ssa_detection_and_output_header():
    text = (
        "[Script Info]\nScriptType: v4.00\n\n"
        "[V4 Styles]\nFormat: Name, Fontname, Fontsize\n"
        "Style: Default,Arial,20\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        "Dialogue: 0,0:00:01.00,0:00:02.00,Default,,0,0,0,,Hello\n"
    )
    assert detect_format(text) == SubtitleFormat.SSA
    subtitle = AssParser.parse(text)
    assert subtitle.format == SubtitleFormat.SSA
    assert "[V4 Styles]" in AssParser.write(subtitle)


def test_bom_and_utf16_preservation():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        utf8_path = root / "utf8.srt"
        utf8_path.write_bytes(codecs.BOM_UTF8 + _sample_bilingual_srt().encode("utf-8"))
        text, encoding, newline = read_subtitle_file(str(utf8_path))
        assert encoding == "utf-8-bom"
        output = root / "utf8-out.srt"
        write_subtitle_file(str(output), text, encoding=encoding, newline=newline)
        assert output.read_bytes().startswith(codecs.BOM_UTF8)

        utf16_path = root / "utf16.srt"
        utf16_path.write_bytes(codecs.BOM_UTF16_LE + _sample_bilingual_srt().encode("utf-16-le"))
        text, encoding, newline = read_subtitle_file(str(utf16_path))
        assert encoding == "utf-16-le-bom"
        output16 = root / "utf16-out.srt"
        write_subtitle_file(str(output16), text, encoding=encoding, newline=newline)
        assert output16.read_bytes().startswith(codecs.BOM_UTF16_LE)


def test_atomic_multi_output_prepares_before_replace():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        first = root / "first.srt"
        second = root / "second.srt"
        first.write_text("old-first", encoding="utf-8")
        second.write_text("old-second", encoding="utf-8")
        try:
            write_subtitle_files_atomically([
                PendingWrite(str(first), "new-first"),
                PendingWrite(str(second), "cannot encode 你好", encoding="ascii"),
            ])
        except UnicodeEncodeError:
            pass
        else:
            raise AssertionError("Expected encoding failure")
        assert first.read_text(encoding="utf-8") == "old-first"
        assert second.read_text(encoding="utf-8") == "old-second"


def test_path_helpers():
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "sample.srt"
        source.write_text("x", encoding="utf-8")
        assert paths_equal(str(source), str(source.parent / "." / source.name))
        assert ensure_extension("movie.ass", ".srt").endswith("movie.srt")
        assert ensure_extension("movie", "vtt").endswith("movie.vtt")


def test_conversion_uses_actual_extension_and_preserves_bom():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        source = root / "source.srt"
        source.write_bytes(codecs.BOM_UTF8 + _sample_bilingual_srt().encode("utf-8"))
        requested = root / "converted.wrong"
        actual = Path(resolved_conversion_output_path(str(requested), SubtitleFormat.VTT))
        convert_subtitle(str(source), str(requested), SubtitleFormat.VTT)
        assert actual.exists()
        assert actual.read_bytes().startswith(codecs.BOM_UTF8)
        text, _, _ = read_subtitle_file(str(actual))
        assert text.startswith("WEBVTT")


def test_conversion_rejects_source_overwrite():
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "source.srt"
        source.write_text(_sample_bilingual_srt(), encoding="utf-8")
        try:
            convert_subtitle(str(source), str(source), SubtitleFormat.SRT)
        except ValueError:
            pass
        else:
            raise AssertionError("Source overwrite must be rejected")


def test_merge_preserves_selected_entry_metadata():
    primary = SrtParser.parse("1\n00:00:01,000 --> 00:00:02,000\nHello\n")
    secondary = SrtParser.parse("1\n00:00:01,000 --> 00:00:02,000\n你好\n")
    primary.entries[0].metadata = {"style": "PrimaryStyle", "layer": "1"}
    secondary.entries[0].metadata = {"style": "SecondaryStyle", "layer": "2"}
    result = merge(primary, secondary, header_source="secondary")
    assert result.merged_file.entries[0].metadata["style"] == "SecondaryStyle"
    assert result.merged_file.entries[0].metadata["layer"] == "2"


def test_merge_entry_count_mismatch():
    primary = SrtParser.parse(
        "1\n00:00:01,000 --> 00:00:04,000\nHello\n\n"
        "2\n00:00:05,000 --> 00:00:08,000\nWorld\n"
    )
    secondary = SrtParser.parse("1\n00:00:01,000 --> 00:00:04,000\n你好\n")
    result = merge(primary, secondary, on_entry_count_mismatch="warn_pad")
    assert result.conflicts[0][1] == MergeConflictType.MISSING_SECONDARY
    assert len(result.merged_file.entries) == 2


def test_language_and_format_detection():
    assert classify_line("Hello world! 123") == LanguageGroup.LATIN
    assert classify_line("你好世界") == LanguageGroup.CJK
    assert classify_line("Привет") == LanguageGroup.CYRILLIC
    assert strip_html_tags("<i>Hello</i>") == "Hello"
    assert detect_format(_sample_bilingual_srt()) == SubtitleFormat.SRT
    assert detect_format("cue-name\n00:00:01,000 --> 00:00:02,000\nHello") == SubtitleFormat.SRT


def test_time_roundtrips():
    assert format_srt_timestamp(parse_srt_timestamp("00:00:01,250")) == "00:00:01,250"
    assert format_vtt_timestamp(parse_vtt_timestamp("00:00:01.250")) == "00:00:01.250"
    assert format_ass_timestamp(parse_ass_timestamp("0:00:01.25")) == "0:00:01.25"


def test_end_to_end_separate_merge():
    subtitle = SrtParser.parse(_sample_bilingual_srt())
    separated = separate(subtitle, 0, 1)
    merged = merge(separated.lang1_file, separated.lang2_file)
    assert [entry.lines for entry in merged.merged_file.entries] == [
        ["Hello world", "你好世界"],
        ["Goodbye", "再见"],
    ]


def test_preview_row_limit():
    app = QApplication.instance() or QApplication([])
    entries = [
        SubtitleEntry(
            index=index + 1,
            start_time=timedelta(seconds=index),
            end_time=timedelta(seconds=index + 1),
            lines=["A", "B"],
        )
        for index in range(PREVIEW_ROW_LIMIT + 20)
    ]
    table = PreviewTable()
    table.show_separation_preview(entries, 0, 1, [])
    assert table.rowCount() == PREVIEW_ROW_LIMIT
    assert table.is_truncated
    table.deleteLater()
    app.processEvents()


def run_all():
    tests = [
        value
        for name, value in sorted(globals().items())
        if name.startswith("test_") and callable(value)
    ]
    for test in tests:
        test()
        print(f"{test.__name__}: OK")
    print(f"\n=== {len(tests)} TESTS PASSED ===")


if __name__ == "__main__":
    run_all()
