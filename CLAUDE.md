# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Bilingual subtitle separation and merging GUI tool (PySide6). Supports SRT, ASS/SSA, and VTT formats with Chinese/English i18n.

**Entry point:** `python main.py`
**Tests:** `python tests/test_all.py`
**Dependencies:** `pip install -r requirements.txt` (only PySide6>=6.5.0)

## Architecture

```
main.py                 # QApplication, high-DPI setup, launches MainWindow
├── gui/
│   ├── main_window.py  # QMainWindow: lang switcher bar + QTabWidget
│   ├── separate_panel.py  # Tab 1 — bilingual → two monolingual
│   ├── merge_panel.py     # Tab 2 — two monolingual → bilingual
│   ├── drop_zone.py       # Reusable drag-and-drop + browse widget
│   ├── preview_table.py   # QTableWidget, 5-column preview with status
│   ├── i18n.py            # Signal-based EN/ZH translation (tr(key, **kw))
│   └── styles.py          # Catppuccin Mocha QSS
├── models/
│   ├── entry.py           # SubtitleEntry, SubtitleFile dataclasses
│   └── enums.py           # SubtitleFormat, LanguageGroup
├── parsers/
│   ├── base.py            # AbstractParser ABC + detect_format() / get_parser() factory
│   ├── srt.py             # SrtParser: parse by \n\n blocks, write sequential indices
│   ├── ass.py             # AssParser: preserves header, parses [Events] Dialogue/Comment
│   └── vtt.py             # VttParser: WEBVTT header, optional cue identifiers
├── language/
│   └── detector.py        # Unicode-range classification (CJK/Latin/...), consensus voting
├── logic/
│   ├── separator.py       # separate(sub_file, line_idx1, line_idx2) → SeparationResult
│   └── merger.py          # merge(primary, secondary, **opts) → MergeResult
└── utils/
    ├── time_utils.py      # Timedelta ↔ string for all 3 formats
    └── text.py            # BOM handling, newline normalisation, strip_ass_tags()
```

## Data model

- **`SubtitleEntry`**: `index` (1-based), `start_time`/`end_time` (`timedelta`), `lines` (`list[str]` — one element per display line), `metadata` (`dict` — ASS fields like style/actor/layer)
- **`SubtitleFile`**: `entries`, `format` (enum), `header` (raw string for ASS/VTT preamble)
- **`MergeConflictType`**: `MISSING_PRIMARY`, `MISSING_SECONDARY`, `TIMESTAMP_MISMATCH` — returned in `MergeResult.conflicts`

Time is always `timedelta` internally. Each format's parser/writer converts to/from its native string representation.

## Parser details

### ASS parser (ass.py)

- Stores raw header (everything before `[Events]` plus Format lines) in `SubtitleFile.header`
- `text_lines = text.split("\\N")` — `\N` is the ASS line break within a Dialogue text field
- `_split_ass_fields(content, len(format_fields))` splits dialogue field values. The `num_fields` parameter **must** be passed to prevent commas inside the Text field from being treated as field separators
- `\,` (escaped comma) → literal `,` during parsing
- Entry index is **sequential** (1, 2, 3...), NOT derived from the Layer field. The original Layer value is stored in `metadata["layer"]` for write round-trip
- The writer reads `metadata["layer"]` for the Layer output field, falling back to sequential

### SRT parser (srt.py)

- Splits on `\n\n` blocks; handles optional cue identifiers before the index number
- **Writer always outputs sequential indices** (`i+1`), not `entry.index`. This ensures valid SRT regardless of input format

### VTT parser (vtt.py)

- Preserves WEBVTT header; optional cue identifiers stored in `metadata["identifier"]`
- Writer includes identifiers only when present

## i18n pattern

All GUI strings use `tr("@category.key", **kwargs)` from `gui/i18n.py`. The `I18n` singleton emits `language_changed` on switch; every widget connects to this signal to refresh text. Adding a new string requires:
1. `add_translations("@key", "English", "中文")` in `i18n.py`
2. `tr("@key")` in the widget code; store the key in `__init__` and re-call `tr()` in the `_on_language_changed` handler

## Known sharp edges

- When converting ASS → SRT, call `strip_ass_tags()` (from `utils/text.py`) on each line to remove ASS override blocks (`{\an8}`, `{\rStyle}`, `{\fs10}`, etc.)
- ASS Layer field uses `metadata["layer"]`, not `entry.index - 1` (the index is sequential and unrelated to layer)
- SRT index numbers in the file are preserved during parsing but **not** during writing — the writer renumbers sequentially
- `read_subtitle_file()` normalises all newlines to `\n` and detects the original convention; `write_subtitle_file()` restores it. Encoding is auto-detected (UTF-8 with BOM, UTF-16 LE/BE, GBK fallback)
- Language detection classifies by Unicode codepoint ranges with a 50% majority threshold per line, then consensus voting across all entries to determine which line index holds which language
- `tests/test_all.py` hardcodes `sys.path.insert(0, 'D:/CODE')` — change this if the repo is cloned to a different path
