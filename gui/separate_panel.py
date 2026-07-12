from __future__ import annotations

import os
import re

from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QComboBox,
    QVBoxLayout,
    QWidget,
)

from gui.drop_zone import DropZone
from gui.i18n import i18n, tr
import gui.i18n_extra  # noqa: F401
from gui.preview_table import PreviewTable
from gui.ui_components import Card, FileSummary, StatusPill, ToggleSwitch
from language.detector import (
    LANGUAGE_GROUP_NAMES,
    LANGUAGE_GROUP_NAMES_ZH,
    LanguageGroup,
    detect_language_assignment,
)
from logic.separator import separate
from models.entry import SubtitleFile
from models.enums import SubtitleFormat
from parsers.base import detect_format, get_parser
from utils.text import (
    PendingWrite,
    paths_equal,
    read_subtitle_file,
    strip_ass_tags,
    write_subtitle_files_atomically,
)


class SeparatePanel(QWidget):
    status_message = Signal(str)

    def __init__(self):
        super().__init__()
        self.sub_file: SubtitleFile | None = None
        self.lang1_line = 0
        self.lang2_line = 1
        self.original_nl = "\r\n"
        self.original_encoding = "utf-8"
        self.detected_assignment: dict[int, LanguageGroup] = {}
        self._input_path = ""
        self._lang1_path_custom = False
        self._lang2_path_custom = False

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        left = QWidget()
        left.setFixedWidth(330)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(14)
        left_layout.addWidget(self._build_import_card())
        left_layout.addWidget(self._build_language_card())
        left_layout.addStretch()
        root.addWidget(left)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(14)
        right_layout.addWidget(self._build_preview_card(), 1)
        right_layout.addWidget(self._build_output_card())
        root.addWidget(right, 1)

        self.lang1_path.installEventFilter(self)
        self.lang2_path.installEventFilter(self)
        self.lang1_path.textEdited.connect(lambda _text: self._set_path_custom(1))
        self.lang2_path.textEdited.connect(lambda _text: self._set_path_custom(2))
        i18n.language_changed.connect(self._on_language_changed)
        self._on_language_changed(i18n.current_lang)

    def _build_import_card(self) -> Card:
        card = Card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(17, 16, 17, 16)
        layout.setSpacing(12)

        title_row = QHBoxLayout()
        self.import_title = QLabel()
        self.import_title.setObjectName("card_title")
        self.format_hint = QLabel("SRT · ASS · SSA · VTT")
        self.format_hint.setObjectName("format_hint")
        title_row.addWidget(self.import_title)
        title_row.addStretch()
        title_row.addWidget(self.format_hint)
        layout.addLayout(title_row)

        self.drop_zone = DropZone("@sep.preview_drop_main", badge_text="SRT")
        self.drop_zone.file_changed.connect(self._on_file_loaded)
        layout.addWidget(self.drop_zone)

        self.file_summary = FileSummary()
        self.file_summary.hide()
        self.file_summary.replace_requested.connect(self.drop_zone._browse)
        layout.addWidget(self.file_summary)
        return card

    def _build_language_card(self) -> Card:
        card = Card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(17, 16, 17, 16)
        layout.setSpacing(12)

        head = QHBoxLayout()
        text_col = QVBoxLayout()
        text_col.setSpacing(3)
        self.auto_title = QLabel()
        self.auto_title.setObjectName("card_title")
        self.auto_desc = QLabel()
        self.auto_desc.setObjectName("card_subtitle")
        self.auto_desc.setWordWrap(True)
        text_col.addWidget(self.auto_title)
        text_col.addWidget(self.auto_desc)
        head.addLayout(text_col, 1)
        self.auto_toggle = ToggleSwitch()
        self.auto_toggle.setChecked(True)
        self.auto_toggle.toggled.connect(self._on_detection_mode_changed)
        head.addWidget(self.auto_toggle, 0, Qt.AlignTop)
        layout.addLayout(head)

        divider = QFrame()
        divider.setObjectName("divider")
        layout.addWidget(divider)

        self.detect_label = QLabel()
        self.detect_label.setObjectName("small_label")
        layout.addWidget(self.detect_label)
        chip_row = QHBoxLayout()
        chip_row.setSpacing(7)
        self.lang1_chip = QPushButton("--")
        self.lang2_chip = QPushButton("--")
        for chip in (self.lang1_chip, self.lang2_chip):
            chip.setObjectName("language_chip")
            chip.setCursor(Qt.PointingHandCursor)
            chip.setEnabled(False)
            chip.clicked.connect(self._swap_manual_assignment)
            chip_row.addWidget(chip)
        chip_row.addStretch()
        layout.addLayout(chip_row)

        divider2 = QFrame()
        divider2.setObjectName("divider")
        layout.addWidget(divider2)

        fmt_row = QHBoxLayout()
        fmt_text = QVBoxLayout()
        fmt_text.setSpacing(3)
        self.fmt_label = QLabel()
        self.fmt_label.setObjectName("small_label")
        self.fmt_hint_label = QLabel()
        self.fmt_hint_label.setObjectName("card_subtitle")
        self.fmt_hint_label.setWordWrap(True)
        fmt_text.addWidget(self.fmt_label)
        fmt_text.addWidget(self.fmt_hint_label)
        fmt_row.addLayout(fmt_text, 1)
        self.fmt_combo = QComboBox()
        self.fmt_combo.setObjectName("compact_combo")
        self.fmt_combo.setFixedWidth(122)
        self.fmt_combo.currentIndexChanged.connect(self._on_output_format_changed)
        fmt_row.addWidget(self.fmt_combo)
        layout.addLayout(fmt_row)
        return card

    def _build_preview_card(self) -> Card:
        card = Card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("preview_header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(18, 14, 18, 13)
        text_col = QVBoxLayout()
        text_col.setSpacing(3)
        self.preview_title = QLabel()
        self.preview_title.setObjectName("preview_title")
        self.preview_meta = QLabel()
        self.preview_meta.setObjectName("preview_meta")
        text_col.addWidget(self.preview_title)
        text_col.addWidget(self.preview_meta)
        header_layout.addLayout(text_col)
        header_layout.addStretch()
        self.preview_status = StatusPill(tone="neutral")
        header_layout.addWidget(self.preview_status)
        layout.addWidget(header)

        self.preview_table = PreviewTable()
        layout.addWidget(self.preview_table, 1)
        return card

    def _build_output_card(self) -> Card:
        card = Card()
        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 13, 16, 13)
        layout.setSpacing(12)

        lang1_group = QVBoxLayout()
        lang1_group.setSpacing(5)
        self.lang1_out_label = QLabel()
        self.lang1_out_label.setObjectName("small_label")
        self.lang1_path = QLineEdit()
        self.lang1_path.setObjectName("path_field")
        lang1_group.addWidget(self.lang1_out_label)
        lang1_group.addWidget(self.lang1_path)
        layout.addLayout(lang1_group, 1)

        lang2_group = QVBoxLayout()
        lang2_group.setSpacing(5)
        self.lang2_out_label = QLabel()
        self.lang2_out_label.setObjectName("small_label")
        self.lang2_path = QLineEdit()
        self.lang2_path.setObjectName("path_field")
        lang2_group.addWidget(self.lang2_out_label)
        lang2_group.addWidget(self.lang2_path)
        layout.addLayout(lang2_group, 1)

        self.separate_btn = QPushButton()
        self.separate_btn.setObjectName("primary_button")
        self.separate_btn.setCursor(Qt.PointingHandCursor)
        self.separate_btn.setEnabled(False)
        self.separate_btn.clicked.connect(self._on_separate)
        layout.addWidget(self.separate_btn, 0, Qt.AlignBottom)
        return card

    def _on_language_changed(self, _lang: str) -> None:
        self.import_title.setText(tr("@sep.preview_import_title"))
        self.auto_title.setText(tr("@sep.preview_auto_title"))
        self.auto_desc.setText(tr("@sep.preview_auto_desc"))
        self.detect_label.setText(tr("@sep.preview_detect_result"))
        self.fmt_label.setText(tr("@sep.preview_output_format"))
        self.fmt_hint_label.setText(tr("@sep.preview_output_hint"))
        self.preview_title.setText(tr("@sep.preview_title"))
        self.separate_btn.setText(tr("@sep.preview_start"))
        self._populate_format_combo()
        self._refresh_language_ui()
        if self.sub_file:
            self._update_default_paths()
            self._update_preview()
        else:
            self._refresh_preview_header()

    def _populate_format_combo(self) -> None:
        previous_data = self.fmt_combo.currentData() if self.fmt_combo.count() else None
        self.fmt_combo.blockSignals(True)
        self.fmt_combo.clear()
        self.fmt_combo.addItem(tr("@sep.same_as_input"), None)
        for name in ("SRT", "ASS", "SSA", "VTT"):
            self.fmt_combo.addItem(name, name)
        index = self.fmt_combo.findData(previous_data)
        self.fmt_combo.setCurrentIndex(index if index >= 0 else 0)
        self.fmt_combo.blockSignals(False)

    def _language_name(self, group: LanguageGroup | None, fallback: str) -> str:
        if group is None:
            return fallback
        names = LANGUAGE_GROUP_NAMES_ZH if i18n.current_lang == "zh" else LANGUAGE_GROUP_NAMES
        return names.get(group, fallback)

    def _refresh_language_ui(self) -> None:
        group1 = self.detected_assignment.get(self.lang1_line)
        group2 = self.detected_assignment.get(self.lang2_line)
        name1 = self._language_name(group1, tr("@sep.language_one"))
        name2 = self._language_name(group2, tr("@sep.language_two"))
        self.lang1_chip.setText(tr("@sep.preview_line_language", line=self.lang1_line + 1, language=name1))
        self.lang2_chip.setText(tr("@sep.preview_line_language", line=self.lang2_line + 1, language=name2))
        self.lang1_out_label.setText(tr("@sep.preview_output_name", language=name1))
        self.lang2_out_label.setText(tr("@sep.preview_output_name", language=name2))

    def _on_file_loaded(self, path: str) -> None:
        try:
            text, encoding, newline = read_subtitle_file(path)
            fmt = detect_format(text)
            parser = get_parser(fmt)
            subtitle = parser.parse(text)
            if not subtitle.entries:
                raise ValueError(tr("@error.no_entries"))
        except Exception as exc:
            self.drop_zone.restore_state()
            QMessageBox.warning(self, tr("@sep.preview_load_failed"), tr("@error.load", msg=str(exc)))
            return

        self.sub_file = subtitle
        self._input_path = path
        self.original_encoding = encoding
        self.original_nl = newline
        self._lang1_path_custom = False
        self._lang2_path_custom = False
        self.drop_zone.set_loaded_metadata(path, fmt.name)
        self.file_summary.set_file(
            os.path.basename(path),
            tr("@sep.preview_file_meta", fmt=fmt.name, count=len(subtitle.entries), encoding=encoding.upper()),
        )
        self.file_summary.show()
        self.separate_btn.setEnabled(True)

        if self.auto_toggle.isChecked():
            self._run_auto_detect()
        else:
            self.detected_assignment = {}
            self.lang1_line, self.lang2_line = 0, 1

        self._update_default_paths(force=True)
        self._update_preview()
        self.status_message.emit(tr("@sep.preview_loaded_status", count=len(subtitle.entries)))

    def _run_auto_detect(self) -> None:
        if not self.sub_file:
            return
        assignment = detect_language_assignment(self.sub_file.entries)
        self.detected_assignment = assignment
        sorted_items = sorted(assignment.items(), key=lambda item: item[0])
        if len(sorted_items) >= 2:
            self.lang1_line = sorted_items[0][0]
            self.lang2_line = sorted_items[1][0]
        else:
            self.lang1_line, self.lang2_line = 0, 1
        self._refresh_language_ui()

    def _on_detection_mode_changed(self, checked: bool) -> None:
        self.lang1_chip.setEnabled(not checked)
        self.lang2_chip.setEnabled(not checked)
        if checked and self.sub_file:
            self._run_auto_detect()
        elif not checked:
            self.detected_assignment = {}
            self.lang1_line, self.lang2_line = 0, 1
            self._refresh_language_ui()
        self._update_default_paths()
        self._update_preview()

    def _swap_manual_assignment(self) -> None:
        if self.auto_toggle.isChecked():
            return
        self.lang1_line, self.lang2_line = self.lang2_line, self.lang1_line
        self._refresh_language_ui()
        self._update_default_paths()
        self._update_preview()

    def _refresh_preview_header(self, missing_count: int = 0) -> None:
        if not self.sub_file:
            self.preview_meta.setText(tr("@sep.preview_empty_meta"))
            self.preview_status.setText(tr("@sep.preview_waiting"))
            self.preview_status.set_tone("neutral")
            return

        mode = tr("@sep.preview_auto_success") if self.auto_toggle.isChecked() else tr("@sep.preview_manual_mode")
        if self.preview_table.is_truncated:
            mode += " · " + tr("@table.preview_limited_short", limit=self.preview_table.visible_entry_count)
        self.preview_meta.setText(tr("@sep.preview_meta", count=len(self.sub_file.entries), mode=mode))
        if missing_count:
            self.preview_status.setText(tr("@sep.preview_missing_status", count=missing_count))
            self.preview_status.set_tone("warning")
        else:
            self.preview_status.setText(tr("@sep.preview_all_normal"))
            self.preview_status.set_tone("success")

    def _update_preview(self) -> None:
        if not self.sub_file:
            self.preview_table.clear_preview()
            self._refresh_preview_header()
            return

        max_line = max(self.lang1_line, self.lang2_line)
        empty = [entry.index for entry in self.sub_file.entries if len(entry.lines) <= max_line]
        name1 = self._language_name(self.detected_assignment.get(self.lang1_line), tr("@sep.language_one"))
        name2 = self._language_name(self.detected_assignment.get(self.lang2_line), tr("@sep.language_two"))
        self.preview_table.show_separation_preview(
            self.sub_file.entries,
            self.lang1_line,
            self.lang2_line,
            empty,
            tr("@sep.preview_line_language", line=self.lang1_line + 1, language=name1),
            tr("@sep.preview_line_language", line=self.lang2_line + 1, language=name2),
        )
        self._refresh_preview_header(len(empty))

    def _resolve_output_format(self) -> SubtitleFormat:
        if not self.sub_file:
            return SubtitleFormat.SRT
        choice = self.fmt_combo.currentData()
        if not choice:
            return self.sub_file.format
        try:
            return SubtitleFormat[choice]
        except KeyError:
            return self.sub_file.format

    def _safe_suffix(self, value: str, fallback: str) -> str:
        cleaned = re.sub(r'[<>:"/\\|?*]+', "_", value).strip(" ._")
        return cleaned or fallback

    def _update_default_paths(self, force: bool = False) -> None:
        if not self._input_path or not self.sub_file:
            return
        extension = {
            SubtitleFormat.SRT: ".srt",
            SubtitleFormat.ASS: ".ass",
            SubtitleFormat.SSA: ".ssa",
            SubtitleFormat.VTT: ".vtt",
        }.get(self._resolve_output_format(), ".srt")
        base, _ = os.path.splitext(self._input_path)
        name1 = self._safe_suffix(
            self._language_name(self.detected_assignment.get(self.lang1_line), tr("@sep.language_one")),
            "lang1",
        )
        name2 = self._safe_suffix(
            self._language_name(self.detected_assignment.get(self.lang2_line), tr("@sep.language_two")),
            "lang2",
        )

        if force or not self._lang1_path_custom:
            self.lang1_path.setText(f"{base}_{name1}{extension}")
        if force or not self._lang2_path_custom:
            self.lang2_path.setText(f"{base}_{name2}{extension}")
        self._refresh_language_ui()

    def _set_path_custom(self, slot: int) -> None:
        if slot == 1:
            self._lang1_path_custom = True
        else:
            self._lang2_path_custom = True

    def _on_output_format_changed(self, _index: int) -> None:
        self._update_default_paths()

    def eventFilter(self, watched, event) -> bool:
        if event.type() == QEvent.MouseButtonDblClick and watched in (self.lang1_path, self.lang2_path):
            slot = 1 if watched is self.lang1_path else 2
            self._browse_output(watched, slot)
            return True
        return super().eventFilter(watched, event)

    def _browse_output(self, line_edit: QLineEdit, slot: int) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            tr("@sep.preview_choose_output", language=str(slot)),
            line_edit.text(),
            tr("@drop.file_filter"),
        )
        if path:
            line_edit.setText(path)
            self._set_path_custom(slot)

    def _validate_output_paths(self, path1: str, path2: str) -> bool:
        if not path1 or not path2:
            QMessageBox.warning(self, tr("@sep.missing_path_title"), tr("@sep.missing_path_msg"))
            return False
        if paths_equal(path1, path2):
            QMessageBox.warning(self, tr("@error.output_path_title"), tr("@error.outputs_must_differ"))
            return False
        if paths_equal(path1, self._input_path) or paths_equal(path2, self._input_path):
            QMessageBox.warning(self, tr("@error.output_path_title"), tr("@error.output_overwrites_source"))
            return False
        return True

    def _on_separate(self) -> None:
        if not self.sub_file:
            return

        path1 = self.lang1_path.text().strip()
        path2 = self.lang2_path.text().strip()
        if not self._validate_output_paths(path1, path2):
            return

        try:
            result = separate(self.sub_file, self.lang1_line, self.lang2_line)
            out_fmt = self._resolve_output_format()
            if out_fmt not in (SubtitleFormat.ASS, SubtitleFormat.SSA):
                for subtitle_file in (result.lang1_file, result.lang2_file):
                    for entry in subtitle_file.entries:
                        entry.lines = [strip_ass_tags(line) for line in entry.lines]

            parser = get_parser(out_fmt)
            for subtitle_file in (result.lang1_file, result.lang2_file):
                subtitle_file.format = out_fmt

            text1 = parser.write(result.lang1_file)
            text2 = parser.write(result.lang2_file)
            write_subtitle_files_atomically([
                PendingWrite(path=path1, text=text1, encoding=self.original_encoding, newline=self.original_nl),
                PendingWrite(path=path2, text=text2, encoding=self.original_encoding, newline=self.original_nl),
            ])
        except Exception as exc:
            QMessageBox.critical(self, tr("@error.write_title"), tr("@error.write_failed", msg=str(exc)))
            self.status_message.emit(tr("@error.write_failed", msg=str(exc)))
            return

        message = tr("@sep.complete_msg", path1=path1, path2=path2)
        if result.empty_entries:
            message += "\n\n" + tr("@sep.warn_missing", n=len(result.empty_entries))
        QMessageBox.information(self, tr("@sep.complete_title"), message)
        self.status_message.emit(tr("@sep.status_done", path1=path1, path2=path2))
