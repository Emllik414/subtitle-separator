from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QGroupBox, QFileDialog, QMessageBox, QCheckBox, QLineEdit, QFrame,
)
from PySide6.QtCore import Qt, Signal

from gui.drop_zone import DropZone
from gui.preview_table import PreviewTable
from gui.i18n import i18n, tr
from models.entry import SubtitleFile
from models.enums import SubtitleFormat
from parsers.base import detect_format, get_parser
from language.detector import detect_language_assignment, LANGUAGE_GROUP_NAMES, LANGUAGE_GROUP_NAMES_ZH, LanguageGroup
from logic.separator import separate
from utils.text import read_subtitle_file, write_subtitle_file, strip_ass_tags


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

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # --- Input Drop Zone ---
        self.drop_zone = DropZone("@sep.drop_label")
        self.drop_zone.file_changed.connect(self._on_file_loaded)
        layout.addWidget(self.drop_zone)

        # File info bar
        self.info_label = QLabel(tr("@sep.no_file"))
        self.info_label.setStyleSheet("color: #6c7086; padding: 2px;")
        layout.addWidget(self.info_label)

        # --- Language Detection ---
        self.lang_group = QGroupBox(tr("@sep.auto_detect"))
        lang_layout = QVBoxLayout(self.lang_group)

        self.auto_detect_cb = QCheckBox(tr("@sep.auto_detect"))
        self.auto_detect_cb.setChecked(True)
        self.auto_detect_cb.toggled.connect(self._on_detection_mode_changed)
        lang_layout.addWidget(self.auto_detect_cb)

        manual_frame = QFrame()
        manual_layout = QHBoxLayout(manual_frame)
        manual_layout.setContentsMargins(0, 0, 0, 0)

        line1_layout = QVBoxLayout()
        self.line1_label_w = QLabel(tr("@sep.line1_label"))
        line1_layout.addWidget(self.line1_label_w)
        self.lang1_combo = QComboBox()
        self.lang1_combo.addItem(tr("@sep.line1"), 0)
        self.lang1_combo.addItem(tr("@sep.line2"), 1)
        self.lang1_combo.setEnabled(False)
        line1_layout.addWidget(self.lang1_combo)
        manual_layout.addLayout(line1_layout)

        line2_layout = QVBoxLayout()
        self.line2_label_w = QLabel(tr("@sep.line2_label"))
        line2_layout.addWidget(self.line2_label_w)
        self.lang2_combo = QComboBox()
        self.lang2_combo.addItem(tr("@sep.line1"), 0)
        self.lang2_combo.addItem(tr("@sep.line2"), 1)
        self.lang2_combo.setCurrentIndex(1)
        self.lang2_combo.setEnabled(False)
        line2_layout.addWidget(self.lang2_combo)
        manual_layout.addLayout(line2_layout)

        lang_layout.addWidget(manual_frame)

        self.detected_label = QLabel(tr("@sep.detected"))
        self.lang1_label = QLabel("--")
        self.lang2_label = QLabel("--")
        labels_layout = QHBoxLayout()
        labels_layout.addWidget(self.detected_label)
        labels_layout.addWidget(self.lang1_label)
        labels_layout.addWidget(QLabel(" | "))
        labels_layout.addWidget(self.lang2_label)
        labels_layout.addStretch()
        lang_layout.addLayout(labels_layout)

        layout.addWidget(self.lang_group)

        # --- Output format ---
        fmt_layout = QHBoxLayout()
        self.fmt_label = QLabel(tr("@sep.output_format"))
        fmt_layout.addWidget(self.fmt_label)
        self.fmt_combo = QComboBox()
        self.fmt_combo.setMinimumWidth(170)
        self._populate_format_combo()
        fmt_layout.addWidget(self.fmt_combo)
        fmt_layout.addStretch()
        layout.addLayout(fmt_layout)

        # --- Preview ---
        self.preview_table = PreviewTable()
        layout.addWidget(self.preview_table, 1)

        # --- Output paths + Execute ---
        out_layout = QVBoxLayout()
        out_layout.setSpacing(6)

        l1_out = QHBoxLayout()
        self.lang1_out_label = QLabel(tr("@sep.lang1_out"))
        l1_out.addWidget(self.lang1_out_label)
        self.lang1_path = QLineEdit()
        self.lang1_path.setPlaceholderText(tr("@sep.lang1_placeholder"))
        l1_out.addWidget(self.lang1_path)
        l1_browse = QPushButton("...")
        l1_browse.setFixedWidth(36)
        l1_browse.setStyleSheet("background-color: #45475a; color: #cdd6f4; border-radius: 4px; padding: 4px; font-weight: bold;")
        l1_browse.setCursor(Qt.PointingHandCursor)
        l1_browse.clicked.connect(lambda: self._browse_output(self.lang1_path, "lang1"))
        l1_out.addWidget(l1_browse)
        out_layout.addLayout(l1_out)

        l2_out = QHBoxLayout()
        self.lang2_out_label = QLabel(tr("@sep.lang2_out"))
        l2_out.addWidget(self.lang2_out_label)
        self.lang2_path = QLineEdit()
        self.lang2_path.setPlaceholderText(tr("@sep.lang2_placeholder"))
        l2_out.addWidget(self.lang2_path)
        l2_browse = QPushButton("...")
        l2_browse.setFixedWidth(40)
        l2_browse.clicked.connect(lambda: self._browse_output(self.lang2_path, "lang2"))
        l2_out.addWidget(l2_browse)
        out_layout.addLayout(l2_out)

        layout.addLayout(out_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.separate_btn = QPushButton(tr("@sep.btn_separate"))
        self.separate_btn.setFixedWidth(140)
        self.separate_btn.setEnabled(False)
        self.separate_btn.clicked.connect(self._on_separate)
        btn_layout.addWidget(self.separate_btn)
        layout.addLayout(btn_layout)

        i18n.language_changed.connect(self._on_language_changed)

    def _on_language_changed(self, lang: str):
        self.lang_group.setTitle("")
        self.auto_detect_cb.setText(tr("@sep.auto_detect"))
        self.line1_label_w.setText(tr("@sep.line1_label"))
        self.line2_label_w.setText(tr("@sep.line2_label"))
        self.detected_label.setText(tr("@sep.detected"))
        self.fmt_label.setText(tr("@sep.output_format"))
        self.lang1_out_label.setText(tr("@sep.lang1_out"))
        self.lang2_out_label.setText(tr("@sep.lang2_out"))
        self.lang1_path.setPlaceholderText(tr("@sep.lang1_placeholder"))
        self.lang2_path.setPlaceholderText(tr("@sep.lang2_placeholder"))
        self.separate_btn.setText(tr("@sep.btn_separate"))

        # Rebuild combo items
        self.lang1_combo.clear()
        self.lang1_combo.addItem(tr("@sep.line1"), 0)
        self.lang1_combo.addItem(tr("@sep.line2"), 1)
        self.lang2_combo.clear()
        self.lang2_combo.addItem(tr("@sep.line1"), 0)
        self.lang2_combo.addItem(tr("@sep.line2"), 1)
        self.lang2_combo.setCurrentIndex(1)

        self._populate_format_combo()

        # Re-apply detection result labels
        if self.sub_file:
            self._refresh_lang_labels()
        else:
            self.info_label.setText(tr("@sep.no_file"))

    def _populate_format_combo(self):
        self.fmt_combo.clear()
        self.fmt_combo.addItems([
            tr("@sep.same_as_input"), "SRT", "ASS", "VTT"
        ])

    def _refresh_lang_labels(self):
        if not self.detected_assignment:
            self.lang1_label.setText(tr("@sep.no_lang"))
            self.lang2_label.setText("--")
            return
        names = LANGUAGE_GROUP_NAMES_ZH if i18n.current_lang == "zh" else LANGUAGE_GROUP_NAMES
        sorted_items = sorted(self.detected_assignment.items(), key=lambda x: x[0])
        if len(sorted_items) >= 1:
            _, g0 = sorted_items[0]
            self.lang1_label.setText(names.get(g0, "?"))
        if len(sorted_items) >= 2:
            _, g1 = sorted_items[1]
            self.lang2_label.setText(names.get(g1, "?"))

    def _on_file_loaded(self, path: str):
        try:
            text, enc, nl = read_subtitle_file(path)
            self.original_encoding = enc
            self.original_nl = nl
            fmt = detect_format(text)
            parser = get_parser(fmt)
            self.sub_file = parser.parse(text)

            count = len(self.sub_file.entries)
            lines_sample = ", ".join(str(len(e.lines)) for e in self.sub_file.entries[:3])
            more = "..." if count > 3 else ""
            self.info_label.setText(tr("@sep.format_info", fmt=fmt.name, count=count, lines=f"{lines_sample}{more}"))
            self.info_label.setStyleSheet("color: #a6e3a1; padding: 2px;")
            self.separate_btn.setEnabled(True)

            if self.auto_detect_cb.isChecked():
                self._run_auto_detect()

            ext_map = {SubtitleFormat.SRT: ".srt", SubtitleFormat.ASS: ".ass", SubtitleFormat.SSA: ".ass", SubtitleFormat.VTT: ".vtt"}
            ext = ext_map.get(fmt, ".srt")
            base = path.rsplit(".", 1)[0] if "." in path else path
            self.lang1_path.setText(f"{base}_lang1{ext}")
            self.lang2_path.setText(f"{base}_lang2{ext}")

            self._update_preview()

        except Exception as e:
            self.info_label.setText(tr("@error.load", msg=str(e)))
            self.info_label.setStyleSheet("color: #f38ba8; padding: 2px;")
            self.sub_file = None
            self.separate_btn.setEnabled(False)

    def _run_auto_detect(self):
        if not self.sub_file:
            return
        assignment = detect_language_assignment(self.sub_file.entries)
        self.detected_assignment = assignment
        self._refresh_lang_labels()

        if not assignment:
            return

        sorted_items = sorted(assignment.items(), key=lambda x: x[0])
        if len(sorted_items) >= 1:
            idx0, _ = sorted_items[0]
            self.lang1_combo.setCurrentIndex(idx0)
            self.lang1_line = idx0
        if len(sorted_items) >= 2:
            idx1, _ = sorted_items[1]
            self.lang2_combo.setCurrentIndex(idx1)
            self.lang2_line = idx1

    def _on_detection_mode_changed(self, checked: bool):
        manual = not checked
        self.lang1_combo.setEnabled(manual)
        self.lang2_combo.setEnabled(manual)
        if checked and self.sub_file:
            self._run_auto_detect()
            self._update_preview()

    def _update_preview(self):
        if not self.sub_file:
            self.preview_table.clear_preview()
            return

        self.lang1_line = self.lang1_combo.currentData() if self.lang1_combo.currentData() is not None else 0
        self.lang2_line = self.lang2_combo.currentData() if self.lang2_combo.currentData() is not None else 1

        empty = [e.index for e in self.sub_file.entries if len(e.lines) <= max(self.lang1_line, self.lang2_line)]

        self.preview_table.show_separation_preview(
            self.sub_file.entries, self.lang1_line, self.lang2_line, empty,
        )

    def _browse_output(self, line_edit: QLineEdit, suffix: str):
        path, _ = QFileDialog.getSaveFileName(
            self, f"Save {suffix} as", "",
            tr("@drop.file_filter")
        )
        if path:
            line_edit.setText(path)

    def _on_separate(self):
        if not self.sub_file:
            return

        lang1_path = self.lang1_path.text().strip()
        lang2_path = self.lang2_path.text().strip()
        if not lang1_path or not lang2_path:
            QMessageBox.warning(self, tr("@sep.missing_path_title"), tr("@sep.missing_path_msg"))
            return

        self.lang1_line = self.lang1_combo.currentData() if self.lang1_combo.currentData() is not None else 0
        self.lang2_line = self.lang2_combo.currentData() if self.lang2_combo.currentData() is not None else 1

        result = separate(self.sub_file, self.lang1_line, self.lang2_line)

        fmt_choice = self.fmt_combo.currentText()
        if fmt_choice == tr("@sep.same_as_input") or fmt_choice == "Same as input":
            out_fmt = self.sub_file.format
        else:
            try:
                out_fmt = SubtitleFormat[fmt_choice]
            except KeyError:
                out_fmt = self.sub_file.format

        # Strip ASS style override tags when outputting to non-ASS formats
        if out_fmt not in (SubtitleFormat.ASS, SubtitleFormat.SSA):
            for subf in (result.lang1_file, result.lang2_file):
                for entry in subf.entries:
                    entry.lines = [strip_ass_tags(line) for line in entry.lines]

        parser_cls = get_parser(out_fmt)

        for path, subf in [(lang1_path, result.lang1_file), (lang2_path, result.lang2_file)]:
            subf.format = out_fmt
            text = parser_cls.write(subf)
            write_subtitle_file(path, text, newline=self.original_nl)

        msg = tr("@sep.complete_msg", path1=lang1_path, path2=lang2_path)
        if result.empty_entries:
            msg += "\n\n" + tr("@sep.warn_missing", n=len(result.empty_entries))
        QMessageBox.information(self, tr("@sep.complete_title"), msg)
        self.status_message.emit(tr("@sep.status_done", path1=lang1_path, path2=lang2_path))
