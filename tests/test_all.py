"""Comprehensive test suite for bilingual subtitle tool."""
import sys
sys.path.insert(0, 'D:/CODE')

from utils.text import read_subtitle_file, write_subtitle_file, strip_html_tags
from utils.time_utils import (
    parse_srt_timestamp, format_srt_timestamp,
    parse_vtt_timestamp, format_vtt_timestamp,
    parse_ass_timestamp, format_ass_timestamp,
)
from parsers.base import detect_format, get_parser
from parsers.srt import SrtParser
from parsers.vtt import VttParser
from parsers.ass import AssParser
from language.detector import classify_line, LanguageGroup
from logic.separator import separate
from logic.merger import merge, MergeConflictType


def test_srt_roundtrip():
    text = (
        "1\n"
        "00:00:01,000 --> 00:00:04,000\n"
        "Hello world\n"
        "你好世界\n\n"
        "2\n"
        "00:00:05,000 --> 00:00:08,500\n"
        "Goodbye\n"
        "再见\n"
    )
    sub = SrtParser.parse(text)
    assert len(sub.entries) == 2
    assert sub.entries[0].lines == ["Hello world", "你好世界"]
    out = SrtParser.write(sub)
    sub2 = SrtParser.parse(out)
    assert len(sub2.entries) == 2
    assert sub2.entries[0].lines == ["Hello world", "你好世界"]
    print("SRT round-trip: OK")


def test_vtt_roundtrip():
    text = (
        "WEBVTT\n\n"
        "1\n"
        "00:00:01.000 --> 00:00:04.000\n"
        "Hello world\n"
        "你好世界\n\n"
        "2\n"
        "00:00:05.000 --> 00:00:08.500\n"
        "Goodbye\n"
        "再见\n"
    )
    sub = VttParser.parse(text)
    assert len(sub.entries) == 2
    assert sub.header.startswith("WEBVTT")
    out = VttParser.write(sub)
    sub2 = VttParser.parse(out)
    assert len(sub2.entries) == 2
    print("VTT round-trip: OK")


def test_ass_roundtrip():
    text = (
        "[Script Info]\n"
        "Title: Test\n"
        "ScriptType: v4.00+\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize\n"
        "Style: Default,Arial,20\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        "Dialogue: 0,0:00:01.00,0:00:04.00,Default,,0,0,0,,Hello world\\N你好世界\n"
        "Dialogue: 0,0:00:05.00,0:00:08.50,Default,,0,0,0,,Goodbye\\N再见\n"
    )
    sub = AssParser.parse(text)
    assert len(sub.entries) == 2
    assert sub.header.startswith("[Script Info]")
    out = AssParser.write(sub)
    sub2 = AssParser.parse(out)
    assert len(sub2.entries) == 2
    print("ASS round-trip: OK")


def test_bom_handling():
    text = "1\n00:00:01,000 --> 00:00:04,000\nHello\n你好\n"
    write_subtitle_file("D:/CODE/tests/bom_test.srt", text, add_bom=True)
    text_out, enc, nl = read_subtitle_file("D:/CODE/tests/bom_test.srt")
    assert enc == "utf-8-bom"
    sub = SrtParser.parse(text_out)
    assert sub.entries[0].lines == ["Hello", "你好"]
    print("BOM handling: OK")


def test_empty_entries():
    text = (
        "1\n00:00:01,000 --> 00:00:04,000\nHello\n你好\n\n"
        "2\n00:00:05,000 --> 00:00:08,000\n\n"
    )
    sub = SrtParser.parse(text)
    assert len(sub.entries) == 2
    assert sub.entries[1].lines == []
    result = separate(sub, 0, 1)
    assert 2 in result.empty_entries
    print("Empty entries: OK")


def test_merge_entry_count_mismatch():
    a = SrtParser.parse(
        "1\n00:00:01,000 --> 00:00:04,000\nHello\n\n"
        "2\n00:00:05,000 --> 00:00:08,000\nWorld\n"
    )
    b = SrtParser.parse("1\n00:00:01,000 --> 00:00:04,000\n你好\n")
    result = merge(a, b, on_entry_count_mismatch="warn_pad")
    assert len(result.conflicts) > 0
    assert result.conflicts[0][1] == MergeConflictType.MISSING_SECONDARY
    assert len(result.merged_file.entries) == 2
    print("Merge mismatch pad: OK")


def test_merge_timestamp_mismatch():
    a = SrtParser.parse("1\n00:00:01,000 --> 00:00:04,000\nHello\n")
    b = SrtParser.parse("1\n00:00:01,500 --> 00:00:04,500\n你好\n")
    result = merge(a, b, timestamp_tolerance_ms=100)
    assert len(result.conflicts) == 1
    assert result.conflicts[0][1] == MergeConflictType.TIMESTAMP_MISMATCH
    print("Timestamp mismatch: OK")


def test_language_detection():
    assert classify_line("Hello world! 123") == LanguageGroup.LATIN
    assert classify_line("你好世界") == LanguageGroup.CJK
    assert classify_line("") == LanguageGroup.UNKNOWN
    assert classify_line("!@#$%^&*()") == LanguageGroup.UNKNOWN
    assert classify_line("Привет") == LanguageGroup.CYRILLIC
    print("Language detection: OK")


def test_format_detection():
    assert detect_format("1\n00:00:01,000 --> 00:00:04,000\ntest").name == "SRT"
    assert detect_format("WEBVTT\n\ntest").name == "VTT"
    assert detect_format("[Script Info]\ntest").name == "ASS"
    print("Format detection: OK")


def test_html_tag_stripping():
    assert strip_html_tags("<i>Hello</i> <b>world</b>") == "Hello world"
    print("HTML tag stripping: OK")


def test_end_to_end():
    # Full cycle: bilingual SRT -> separate -> merge -> verify
    text = (
        "1\n00:00:01,000 --> 00:00:04,000\n"
        "你好，今天天气真好。\n"
        "Hello, the weather is really nice today.\n\n"
        "2\n00:00:05,000 --> 00:00:08,500\n"
        "我们去公园散步吧。\n"
        "Let's go for a walk in the park.\n\n"
        "3\n00:00:09,000 --> 00:00:12,000\n"
        "我完全同意你的看法。\n"
        "I completely agree with you.\n"
    )
    sub = SrtParser.parse(text)
    assert len(sub.entries) == 3

    # Separate: line 0 = Chinese, line 1 = English
    result = separate(sub, 0, 1)
    assert len(result.lang1_file.entries) == 3
    assert len(result.lang2_file.entries) == 3
    assert result.empty_entries == []

    # Write and read back
    out1 = SrtParser.write(result.lang1_file)
    out2 = SrtParser.write(result.lang2_file)
    sub1 = SrtParser.parse(out1)
    sub2 = SrtParser.parse(out2)

    # Merge
    merge_result = merge(sub1, sub2)
    assert len(merge_result.merged_file.entries) == 3
    assert len(merge_result.conflicts) == 0

    # Verify round-trip
    for orig, merged in zip(sub.entries, merge_result.merged_file.entries):
        assert orig.lines[0] == merged.lines[0]
        assert orig.lines[1] == merged.lines[1]

    print("End-to-end: OK")


def test_ass_comma_escape():
    # Test that ASS parser correctly handles backslash-comma in text
    from parsers.ass import _split_ass_fields, _escape_ass_text
    fields = _split_ass_fields("0,0:00:01.00,0:00:04.00,Default,,0,0,0,,Hello\\, world\\N你好")
    assert len(fields) >= 10
    assert "Hello, world\\N你好" in fields[-1] or "Hello, world" in fields[-1].replace("\\N", "\n")
    print("ASS comma escape: OK")


if __name__ == "__main__":
    test_srt_roundtrip()
    test_vtt_roundtrip()
    test_ass_roundtrip()
    test_bom_handling()
    test_empty_entries()
    test_merge_entry_count_mismatch()
    test_merge_timestamp_mismatch()
    test_language_detection()
    test_format_detection()
    test_html_tag_stripping()
    test_ass_comma_escape()
    test_end_to_end()
    print("\n=== ALL TESTS PASSED ===")
