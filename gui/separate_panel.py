from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from gui.drop_zone import DropZone
from gui.i18n import i18n, tr
from gui.preview_table import PreviewTable
from gui.ui_components import AppleCard, ToggleSwitch, set_tone
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
from utils.text import read_subtitle_file, strip_ass_tags, write_subtitle_file


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

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        left = QWidget()
        left.setFixedWidth(340)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(14)
        root.addWidget(left)

        import_card = AppleCard(spacing=10)
        self.import_title = QLabel(tr("@sep.import_title"))
        self.import_title.setObjectName("sectionTitle")
        self.import_formats = QLabel("SRT · ASS · SSA · VTT")
        self.import_formats.setObjectName("sectionSubtitle")
        title_row = QHBoxLayout()
        title_row.addWidget(self.import_title)
        title_row.addStretch()
        title_row.addWidget(self.import_formats)
        import_card.content_layout.addLayout(title_row)

        self.drop_zone = DropZone("@sep.drop_label")
        self.drop_zone.file_changed.connect(self._on_file_loaded)
        import_card.content_layout.addWidget(self.drop_zone)

        self.info_label = QLabel(tr("@sep.no_file"))
        self.info_label.setObjectName("metaText")
        self.info_label.setWordWrap(True)
        set_tone(self.info_label, "muted")
        import_card.content_layout.addWidget(self.info_label)
        left_layout.addWidget(import_card)

        lang_card = AppleCard(spacing=10)
        header_row = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        self.language_title = QLabel(tr("@sep.language_title"))
        self.language_title.setObjectName("sectionTitle")
        self.language_desc = QLabel(tr("@sep.language_desc"))
        self.language_desc.setObjectName("sectionSubtitle")
        self.language_desc.setWordWrap(True)
        title_col.addWidget(self.language_title)
        title_col.addWidget(self.language_desc)
        header_row.addLayout(title_col, 1)

        self.auto_detect_cb = ToggleSwitch()
        self.auto_detect_cb.setChecked(True)
        self.auto_detect_cb.setToolTip(tr("@sep.auto_detect"))
        self.auto_detect_cb.toggled.connect(self._on_detection_mode_changed)
        header_row.addWidget(self.auto_detect_cb, 0, Qt.AlignTop)
        lang_card.content_layout.addLayout(header_row)

        self.manual_frame = QFrame()
        manual_layout = QHBoxLayout(self.manual_frame)
        manual_layout.setContentsMargins(0, 4, 0, 0)
        manual_layout.setSpacing(8)

        line1_col = QVBoxLayout()
        line1_col.setSpacing(5)
        self.line1_label_w = QLabel(tr("@sep.line1_label"))
        self.line1_label_w.setObjectName("fieldLabel")
        self.lang1_combo = QComboBox()
        self.lang1_combo.addItem(tr("@sep.line1"), 0)
        self.lang1_combo.addItem(tr("@sep.line2"), 1)
        self.lang1_combo.currentIndexChanged.connect(self._on_manual_selection_changed)
        line1_col.addWidget(self.line1_label_w)
        line1_col.addWidget(self.lang1_combo)
        manual_layout.addLayout(line1_col)

        line2_col = QVBoxLayout()
        line2_col.setSpacing(5)
        self.line2_label_w = QLabel(tr("@sep.line2_label"))
        self.line2_label_w.setObjectName("fieldLabel")
        self.lang2_combo = QComboBox()
        self.lang2_combo.addItem(tr("@sep.line1"), 0)
        self.lang2_combo.addItem(tr("@sep.line2"), 1)
        self.lang2_combo.setCurrentIndex(1)
        self.lang2_combo.currentIndexChanged.connect(self._on_manual_selection_changed)
        line2_col.addWidget(self.line2_label_w)
        line2_col.addWidget(self.lang2_combo)
        manual_layout.addLayout(line2_col)
        self.manual_frame.setVisible(False)
        lang_card.content_layout.addWidget(self.manual_frame)

        self.detected_title = QLabel(tr("@sep.detected_title"))
        self.detected_title.setObjectName("fieldLabel")
        lang_card.content_layout.addWidget(self.detected_title)

        chips_row = QHBoxLayout()
        chips_row.setSpacing(7)
        self.lang1_label = QLabel("—")
        self.lang1_label.setObjectName("chip")
        self.lang2_label = QLabel("—")
        self.lang2_label.setObjectName("chip")
        chips_row.addWidget(self.lang1_label)
        chips_row.addWidget(self.lang2_label)
        chips_row.addStretch()
        lang_card.content_layout.addLayout(chips_row)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("color: #eeeef1; background: #eeeef1; max-height: 1px;")
        lang_card.content_layout.addWidget(divider)

        fmt_row = QHBoxLayout()
        fmt_text = QVBoxLayout()
        fmt_text.setSpacing(2)
        self.fmt_label = QLabel(tr("@sep.output_format"))
        self.fmt_label.setObjectName("fieldLabel")
        self.fmt_hint = QLabel(tr("@sep.output_format_hint"))
        self.fmt_hint.setObjectName("sectionSubtitle")
        fmt_text.addWidget(self.fmt_label)
        fmt_text.addWidget(self.fmt_hint)
        fmt_row.addLayout(fmt_text, 1)
        self.fmt_combo = QComboBox()
        self.fmt_combo.setMinimumWidth(142)
        self._populate_format_combo()
        fmt_row.addWidget(self.fmt_combo)
        lang_card.content_layout.addLayout(fmt_row)
        left_layout.addWidget(lang_card)
        left_layout.addStretch()

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(14)
        root.addWidget(right, 1)

        preview_card = AppleCard(margins=(0, 0, 0, 0), spacing=0)
        preview_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        preview_header = QFrame()
        preview_header_layout = QHBoxLayout(preview_header)
        preview_header_layout.setContentsMargins(17, 14, 17, 12)
        preview_header_layout.setSpacing(12)
        preview_text = QVBoxLayout()
        preview_text.setSpacing(2)
        self.preview_title = QLabel(tr("@sep.preview_title"))
        self.preview_title.setObjectName("sectionTitle")
        self.preview_meta = QLabel(tr("@sep.preview_empty"))
        self.preview_meta.setObjectName("sectionSubtitle")
        preview_text.addWidget(self.preview_title)
        preview_text.addWidget(self.preview_meta)
        preview_header_layout.addLayout(preview_text, 1)
        self.preview_status = QLabel(tr("@sep.preview_waiting"))
        self.preview_status.setObjectName("pill")
        set_tone(self.preview_status, "warning")
        preview_header_layout.addWidget(self.preview_status)
        preview_card.content_layout.addWidget(preview_header)

        self.preview_table = PreviewTable()
        preview_card.content_layout.addWidget(self.preview_table, 1)
        right_layout.addWidget(preview_card, 1)

        output_card = AppleCard(horizontal=True, margins=(15, 14, 15, 14), spacing=12)
        output_card.content_layout.setAlignment(Qt.AlignVCenter)

        lang1_group = QVBoxLayout()
        lang1_group.setSpacing(5)
        self.lang1_out_label = QLabel(tr("@sep.lang1_out"))
        self.lang1_out_label.setObjectName("fieldLabel")
        lang1_group.addWidget(self.lang1_out_label)
        lang1_row = QHBoxLayout()
        lang1_row.setSpacing(6)
        self.lang1_path = QLineEdit()
        self.lang1_path.setPlaceholderText(tr("@sep.lang1_placeholder"))
        lang1_row.addWidget(self.lang1_path, 1)
        lang1_browse = QPushButton("…")
        lang1_browse.setObjectName("iconButton")
        lang1_browse.clicked.connect(lambda: self._browse_output(self.lang1_path, "lang1"))
        lang1_row.addWidget(lang1_browse)
        lang1_group.addLayout(lang1_row)
        output_card.content_layout.addLayout(lang1_group, 1)

        lang2_group = QVBoxLayout()
        lang2_group.setSpacing(5)
        self.lang2_out_label = QLabel(tr("@sep.lang2_out"))
        self.lang2_out_label.setObjectName("fieldLabel")
        lang2_group.addWidget(self.lang2_out_label)
        lang2_row = QHBoxLayout()
        lang2_row.setSpacing(6)
        self.lang2_path = QLineEdit()
        self.lang2_path.setPlaceholderText(tr("@sep.lang2_placeholder"))
        lang2_row.addWidget(self.lang2_path, 1)
        lang2_browse = QPushButton("…")
        lang2_browse.setObjectName("iconButton")
        lang2_browse.clicked.connect(lambda: self._browse_output(self.lang2_path, "lang2"))
        lang2_row.addWidget(lang2_browse)
        lang2_group.addLayout(lang2_row)
        output_card.content_layout.addLayout(lang2_group, 1)

        self.separate_btn = QPushButton(tr("@sep.btn_separate"))
        self.separate_btn.setObjectName("primaryButton")
        self.separate_btn.setMinimumWidth(124)
        self.separate_btn.setEnabled(False)
        self.separate_btn.clicked.connect(self._on_separate)
        output_card.content_layout.addWidget(self.separate_btn, 0, Qt.AlignBottom)
        right_layout.addWidget(output_card)

        i18n.language_changed.connect(self._on_language_changed)

    def _on_language_changed(self, _lang: str):
        self.import_title.setText(tr("@sep.import_title"))
        self.language_title.setText(tr("@sep.language_title"))
        self.language_desc.setText(tr("@sep.language_desc"))
        self.auto_detect_cb.setToolTip(tr("@sep.auto_detect"))
        self.line1_label_w.setText(tr("@sep.line1_label"))
        self.line2_label_w.setText(tr("@sep.line2_label"))
        self.detected_title.setText(tr("@sep.detected_title"))
        self.fmt_label.setText(tr("@sep.output_format"))
        self.fmt_hint.setText(tr("@sep.output_format_hint"))
        self.preview_title.setText(tr("@sep.preview_title"))
        self.lang1_out_label.setText(tr("@sep.lang1_out"))
        self.lang2_out_label.setText(tr("@sep.lang2_out"))
        self.lang1_path.setPlaceholderText(tr("@sep.lang1_placeholder"))
        self.lang2_path.setPlaceholderText(tr("@sep.lang2_placeholder"))
        self.separate_btn.setText(tr("@sep.btn_separate"))

        current1 = self.lang1_combo.currentData()
        current2 = self.lang2_combo.currentData()
        self.lang1_combo.blockSignals(True)
        self.lang2_combo.blockSignals(True)
        self.lang1_combo.clear()
        self.lang1_combo.addItem(tr("@sep.line1"), 0)
        self.lang1_combo.addItem(tr("@sep.line2"), 1)
        self.lang2_combo.clear()
        self.lang2_combo.addItem(tr("@sep.line1"), 0)
        self.lang2_combo.addItem(tr("@sep.line2"), 1)
        self.lang1_combo.setCurrentIndex(0 if current1 == 0 else 1)
        self.lang2_combo.setCurrentIndex(0 if current2 == 0 else 1)
        self.lang1_combo.blockSignals(False)
        self.lang2_combo.blockSignals(False)
        self._populate_format_combo()

        if self.sub_file:
            self._refresh_lang_labels()
            self._update_preview()
        else:
            self.info_label.setText(tr("@sep.no_file"))
            self.preview_meta.setText(tr("@sep.preview_empty"))
            self.preview_status.setText(tr("@sep.preview_waiting"))

    def _populate_format_combo(self):
        current = self.fmt_combo.currentText() if self.fmt_combo.count() else ""
        self.fmt_combo.blockSignals(True)
        self.fmt_combo.clear()
        self.fmt_combo.addItems([tr("@sep.same_as_input"), "SRT", "ASS", "VTT"])
        index = self.fmt_combo.findText(current)
        if index >= 0:
            self.fmt_combo.setCurrentIndex(index)
        self.fmt_combo.blockSignals(False)

    def _refresh_lang_labels(self):
        if not self.detected_assignment:
            self.lang1_label.setText(tr("@sep.no_lang"))
            self.lang2_label.setText("—")
            return

        names = LANGUAGE_GROUP_NAMES_ZH if i18n.current_lang == "zh" else LANGUAGE_GROUP_NAMES
        sorted_items = sorted(self.detected_assignment.items(), key=lambda item: item[0])
        if sorted_items:
            idx, group = sorted_items[0]
            self.lang1_label.setText(tr("@sep.detected_chip", line=idx + 1, lang=names.get(group, "?")))
        if len(sorted_items) >= 2:
            idx, group = sorted_items[1]
            self.lang2_label.setText(tr("@sep.detected_chip", line=idx + 1, lang=names.get(group, "?")))
        else:
            self.lang2_label.setText("—")

    def _on_file_loaded(self, path: str):
        try:
            text, enc, nl = read_subtitle_file(path)
            self.original_encoding = enc
            self.original_nl = nl
            fmt = detect_format(text)
            parser = get_parser(fmt)
            self.sub_file = parser.parse(text)

            count = len(self.sub_file.entries)
            lines_sample = ", ".join(str(len(entry.lines)) for entry in self.sub_file.entries[:3])
            more = "…" if count > 3 else ""
            self.info_label.setText(
                tr("@sep.format_info", fmt=fmt.name, count=count, lines=f"{lines_sample}{more}")
            )
            set_tone(self.info_label, "success")
            self.separate_btn.setEnabled(True)

            if self.auto_detect_cb.isChecked():
                self._run_auto_detect()

            ext_map = {
                SubtitleFormat.SRT: ".srt",
                SubtitleFormat.ASS: ".ass",
                SubtitleFormat.SSA: ".ass",
                SubtitleFormat.VTT: ".vtt",
            }
            ext = ext_map.get(fmt, ".srt")
            base = path.rsplit(".", 1)[0] if "." in path else path
            self.lang1_path.setText(f"{base}_lang1{ext}")
            self.lang2_path.setText(f"{base}_lang2{ext}")
            self._update_preview()
        except Exception as exc:
            self.info_label.setText(tr("@error.load", msg=str(exc)))
            set_tone(self.info_label, "error")
            self.sub_file = None
            self.separate_btn.setEnabled(False)
            self.preview_table.clear_preview()
            self.preview_meta.setText(tr("@sep.preview_empty"))
            self.preview_status.setText(tr("@sep.preview_error"))
            set_tone(self.preview_status, "error")

    def _run_auto_detect(self):
        if not self.sub_file:
            return
        assignment = detect_language_assignment(self.sub_file.entries)
        self.detected_assignment = assignment
        self._refresh_lang_labels()
        if not assignment:
            return

        sorted_items = sorted(assignment.items(), key=lambda item: item[0])
        self.lang1_combo.blockSignals(True)
        self.lang2_combo.blockSignals(True)
        if sorted_items:
            self.lang1_line = sorted_items[0][0]
            self.lang1_combo.setCurrentIndex(self.lang1_line)
        if len(sorted_items) >= 2:
            self.lang2_line = sorted_items[1][0]
            self.lang2_combo.setCurrentIndex(self.lang2_line)
        self.lang1_combo.blockSignals(False)
        self.lang2_combo.blockSignals(False)

    def _on_detection_mode_changed(self, checked: bool):
        self.manual_frame.setVisible(not checked)
        if checked and self.sub_file:
            self._run_auto_detect()
        self._update_preview()

    def _on_manual_selection_changed(self, _index: int):
        if not self.auto_detect_cb.isChecked():
            self._update_preview()

    def _update_preview(self):
        if not self.sub_file:
            self.preview_table.clear_preview()
            return

        self.lang1_line = self.lang1_combo.currentData() if self.lang1_combo.currentData() is not None else 0
        self.lang2_line = self.lang2_combo.currentData() if self.lang2_combo.currentData() is not None else 1
        empty = [
            entry.index
            for entry in self.sub_file.entries
            if len(entry.lines) <= max(self.lang1_line, self.lang2_line)
        ]
        self.preview_table.show_separation_preview(
            self.sub_file.entries,
            self.lang1_line,
            self.lang2_line,
            empty,
        )

        self.preview_meta.setText(
            tr("@sep.preview_meta", count=len(self.sub_file.entries), missing=len(empty))
        )
        if empty:
            self.preview_status.setText(tr("@sep.preview_has_warnings", count=len(empty)))
            set_tone(self.preview_status, "warning")
        else:
            self.preview_status.setText(tr("@sep.preview_all_ok"))
            set_tone(self.preview_status, "success")

    def _browse_output(self, line_edit: QLineEdit, suffix: str):
        path, _ = QFileDialog.getSaveFileName(
            self,
            tr("@sep.save_as", suffix=suffix),
            line_edit.text(),
            tr("@drop.file_filter"),
        )
        if path:
            line_edit.setText(path)

    def _on_separate(self):
        if not self.sub_file:
            return

        lang1_path = self.lang1_path.text().strip()
        lang2_path = self.lang2_path.text().strip()
        if not lang1_path or not lang2_path:
            QMessageBox.warning(
                self,
                tr("@sep.missing_path_title"),
                tr("@sep.missing_path_msg"),
            )
            return

        self.lang1_line = self.lang1_combo.currentData() if self.lang1_combo.currentData() is not None else 0
        self.lang2_line = self.lang2_combo.currentData() if self.lang2_combo.currentData() is not None else 1
        result = separate(self.sub_file, self.lang1_line, self.lang2_line)

        fmt_choice = self.fmt_combo.currentText()
        if fmt_choice in (tr("@sep.same_as_input"), "Same as input"):
            out_fmt = self.sub_file.format
        else:
            try:
                out_fmt = SubtitleFormat[fmt_choice]
            except KeyError:
                out_fmt = self.sub_file.format

        if out_fmt not in (SubtitleFormat.ASS, SubtitleFormat.SSA):
            for sub_file in (result.lang1_file, result.lang2_file):
                for entry in sub_file.entries:
                    entry.lines = [strip_ass_tags(line) for line in entry.lines]

        parser_cls = get_parser(out_fmt)
        for path, sub_file in (
            (lang1_path, result.lang1_file),
            (lang2_path, result.lang2_file),
        ):
            sub_file.format = out_fmt
            text = parser_cls.write(sub_file)
            write_subtitle_file(path, text, newline=self.original_nl)

        message = tr("@sep.complete_msg", path1=lang1_path, path2=lang2_path)
        if result.empty_entries:
            message += "\n\n" + tr("@sep.warn_missing", n=len(result.empty_entries))
        QMessageBox.information(self, tr("@sep.complete_title"), message)
        self.status_message.emit(tr("@sep.status_done", path1=lang1_path, path2=lang2_path))
