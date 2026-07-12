from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QFileDialog, QMessageBox, QRadioButton,
    QButtonGroup, QLineEdit, QComboBox, QSpinBox,
)
from PySide6.QtCore import Qt, Signal

from gui.drop_zone import DropZone
from gui.preview_table import PreviewTable
from gui.i18n import i18n, tr
from models.entry import SubtitleFile
from models.enums import SubtitleFormat
from parsers.base import detect_format, get_parser
from logic.merger import merge
from utils.text import read_subtitle_file, write_subtitle_file, strip_ass_tags


class MergePanel(QWidget):
    status_message = Signal(str)

    def __init__(self):
        super().__init__()
        self.primary_file: SubtitleFile | None = None
        self.secondary_file: SubtitleFile | None = None

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # --- Dual Drop Zones ---
        drop_layout = QHBoxLayout()
        drop_layout.setSpacing(8)

        left_col = QVBoxLayout()
        self.primary_label_w = QLabel(tr("@merge.primary_label"))
        left_col.addWidget(self.primary_label_w)
        self.primary_drop = DropZone("@merge.primary_drop")
        self.primary_drop.file_changed.connect(self._on_primary_loaded)
        left_col.addWidget(self.primary_drop)
        self.primary_info = QLabel(tr("@merge.no_file"))
        self.primary_info.setStyleSheet("color: #6c7086;")
        left_col.addWidget(self.primary_info)
        drop_layout.addLayout(left_col)

        right_col = QVBoxLayout()
        self.secondary_label_w = QLabel(tr("@merge.secondary_label"))
        right_col.addWidget(self.secondary_label_w)
        self.secondary_drop = DropZone("@merge.secondary_drop")
        self.secondary_drop.file_changed.connect(self._on_secondary_loaded)
        right_col.addWidget(self.secondary_drop)
        self.secondary_info = QLabel(tr("@merge.no_file"))
        self.secondary_info.setStyleSheet("color: #6c7086;")
        right_col.addWidget(self.secondary_info)
        drop_layout.addLayout(right_col)

        layout.addLayout(drop_layout)

        # --- Options ---
        self.options_group = QGroupBox(tr("@merge.options"))
        options_layout = QVBoxLayout(self.options_group)
        options_layout.setSpacing(4)

        # Timestamp source
        self.ts_label = QLabel(tr("@merge.ts_source"))
        options_layout.addWidget(self.ts_label)
        self.ts_btn_group = QButtonGroup(self)
        ts_row = QHBoxLayout()
        self.ts_primary_rb = QRadioButton(tr("@merge.ts_primary"))
        self.ts_primary_rb.setChecked(True)
        self.ts_secondary_rb = QRadioButton(tr("@merge.ts_secondary"))
        self.ts_btn_group.addButton(self.ts_primary_rb, 0)
        self.ts_btn_group.addButton(self.ts_secondary_rb, 1)
        ts_row.addWidget(self.ts_primary_rb)
        ts_row.addWidget(self.ts_secondary_rb)
        ts_row.addStretch()
        options_layout.addLayout(ts_row)

        # Tolerance
        tol_row = QHBoxLayout()
        self.tol_label = QLabel(tr("@merge.tolerance"))
        tol_row.addWidget(self.tol_label)
        self.tolerance_spin = QSpinBox()
        self.tolerance_spin.setRange(0, 9999)
        self.tolerance_spin.setValue(100)
        self.tolerance_spin.setSuffix(" ms")
        self.tolerance_spin.setMinimumWidth(110)
        tol_row.addWidget(self.tolerance_spin)
        tol_row.addStretch()
        options_layout.addLayout(tol_row)

        # Ordering
        self.order_label = QLabel(tr("@merge.ordering"))
        options_layout.addWidget(self.order_label)
        self.order_btn_group = QButtonGroup(self)
        order_row = QHBoxLayout()
        self.order_pfirst_rb = QRadioButton(tr("@merge.order_pfirst"))
        self.order_pfirst_rb.setChecked(True)
        self.order_sfirst_rb = QRadioButton(tr("@merge.order_sfirst"))
        self.order_btn_group.addButton(self.order_pfirst_rb, 0)
        self.order_btn_group.addButton(self.order_sfirst_rb, 1)
        order_row.addWidget(self.order_pfirst_rb)
        order_row.addWidget(self.order_sfirst_rb)
        order_row.addStretch()
        options_layout.addLayout(order_row)

        # Entry count mismatch
        self.mismatch_label = QLabel(tr("@merge.mismatch_label"))
        options_layout.addWidget(self.mismatch_label)
        self.mismatch_btn_group = QButtonGroup(self)
        mismatch_row = QHBoxLayout()
        self.mismatch_pad_rb = QRadioButton(tr("@merge.mismatch_pad"))
        self.mismatch_pad_rb.setChecked(True)
        self.mismatch_trunc_rb = QRadioButton(tr("@merge.mismatch_trunc"))
        self.mismatch_btn_group.addButton(self.mismatch_pad_rb, 0)
        self.mismatch_btn_group.addButton(self.mismatch_trunc_rb, 1)
        mismatch_row.addWidget(self.mismatch_pad_rb)
        mismatch_row.addWidget(self.mismatch_trunc_rb)
        mismatch_row.addStretch()
        options_layout.addLayout(mismatch_row)

        # Header source
        self.header_label = QLabel(tr("@merge.header_label"))
        options_layout.addWidget(self.header_label)
        self.header_btn_group = QButtonGroup(self)
        header_row = QHBoxLayout()
        self.header_primary_rb = QRadioButton(tr("@merge.header_primary"))
        self.header_primary_rb.setChecked(True)
        self.header_secondary_rb = QRadioButton(tr("@merge.header_secondary"))
        self.header_btn_group.addButton(self.header_primary_rb, 0)
        self.header_btn_group.addButton(self.header_secondary_rb, 1)
        header_row.addWidget(self.header_primary_rb)
        header_row.addWidget(self.header_secondary_rb)
        header_row.addStretch()
        options_layout.addLayout(header_row)

        layout.addWidget(self.options_group)

        # Output format
        fmt_layout = QHBoxLayout()
        self.fmt_label = QLabel(tr("@merge.output_format"))
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

        # --- Output path + Execute ---
        out_layout = QHBoxLayout()
        self.out_label = QLabel(tr("@merge.output"))
        out_layout.addWidget(self.out_label)
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText(tr("@merge.output_placeholder"))
        out_layout.addWidget(self.output_path)
        out_browse = QPushButton("...")
        out_browse.setFixedWidth(36)
        out_browse.setStyleSheet("background-color: #45475a; color: #cdd6f4; border-radius: 4px; padding: 4px; font-weight: bold;")
        out_browse.setCursor(Qt.PointingHandCursor)
        out_browse.clicked.connect(self._browse_output)
        out_layout.addWidget(out_browse)
        layout.addLayout(out_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.merge_btn = QPushButton(tr("@merge.btn_merge"))
        self.merge_btn.setFixedWidth(140)
        self.merge_btn.setEnabled(False)
        self.merge_btn.clicked.connect(self._on_merge)
        btn_layout.addWidget(self.merge_btn)
        layout.addLayout(btn_layout)

        i18n.language_changed.connect(self._on_language_changed)

    def _on_language_changed(self, lang: str):
        self.primary_label_w.setText(tr("@merge.primary_label"))
        self.secondary_label_w.setText(tr("@merge.secondary_label"))
        self.options_group.setTitle(tr("@merge.options"))
        self.ts_label.setText(tr("@merge.ts_source"))
        self.ts_primary_rb.setText(tr("@merge.ts_primary"))
        self.ts_secondary_rb.setText(tr("@merge.ts_secondary"))
        self.tol_label.setText(tr("@merge.tolerance"))
        self.order_label.setText(tr("@merge.ordering"))
        self.order_pfirst_rb.setText(tr("@merge.order_pfirst"))
        self.order_sfirst_rb.setText(tr("@merge.order_sfirst"))
        self.mismatch_label.setText(tr("@merge.mismatch_label"))
        self.mismatch_pad_rb.setText(tr("@merge.mismatch_pad"))
        self.mismatch_trunc_rb.setText(tr("@merge.mismatch_trunc"))
        self.header_label.setText(tr("@merge.header_label"))
        self.header_primary_rb.setText(tr("@merge.header_primary"))
        self.header_secondary_rb.setText(tr("@merge.header_secondary"))
        self.fmt_label.setText(tr("@merge.output_format"))
        self.out_label.setText(tr("@merge.output"))
        self.output_path.setPlaceholderText(tr("@merge.output_placeholder"))
        self.merge_btn.setText(tr("@merge.btn_merge"))
        self._populate_format_combo()

        if not self.primary_file:
            self.primary_info.setText(tr("@merge.no_file"))
        if not self.secondary_file:
            self.secondary_info.setText(tr("@merge.no_file"))

    def _populate_format_combo(self):
        self.fmt_combo.clear()
        self.fmt_combo.addItems([
            tr("@merge.same_as_primary"), "SRT", "ASS", "VTT"
        ])

    def _on_primary_loaded(self, path: str):
        try:
            text, enc, nl = read_subtitle_file(path)
            fmt = detect_format(text)
            parser = get_parser(fmt)
            self.primary_file = parser.parse(text)
            self.primary_file._nl = nl
            self.primary_info.setText(tr("@merge.format_info", fmt=fmt.name, n=len(self.primary_file.entries)))
            self.primary_info.setStyleSheet("color: #a6e3a1;")
            self._check_ready()
        except Exception as e:
            self.primary_info.setText(tr("@error.load", msg=str(e)))
            self.primary_info.setStyleSheet("color: #f38ba8;")
            self.primary_file = None
            self.merge_btn.setEnabled(False)

    def _on_secondary_loaded(self, path: str):
        try:
            text, enc, nl = read_subtitle_file(path)
            fmt = detect_format(text)
            parser = get_parser(fmt)
            self.secondary_file = parser.parse(text)
            self.secondary_file._nl = nl
            self.secondary_info.setText(tr("@merge.format_info", fmt=fmt.name, n=len(self.secondary_file.entries)))
            self.secondary_info.setStyleSheet("color: #a6e3a1;")
            self._check_ready()
        except Exception as e:
            self.secondary_info.setText(tr("@error.load", msg=str(e)))
            self.secondary_info.setStyleSheet("color: #f38ba8;")
            self.secondary_file = None
            self.merge_btn.setEnabled(False)

    def _check_ready(self):
        if self.primary_file and self.secondary_file:
            self.merge_btn.setEnabled(True)
            if not self.output_path.text().strip():
                ext_map = {SubtitleFormat.SRT: ".srt", SubtitleFormat.ASS: ".ass", SubtitleFormat.SSA: ".ass", SubtitleFormat.VTT: ".vtt"}
                ext = ext_map.get(self.primary_file.format, ".srt")
                base = self.primary_drop.file_path.rsplit(".", 1)[0] if "." in self.primary_drop.file_path else "merged"
                self.output_path.setText(f"{base}_bilingual{ext}")
            self._update_preview()

    def _update_preview(self):
        if not self.primary_file or not self.secondary_file:
            self.preview_table.clear_preview()
            return

        result = merge(
            self.primary_file, self.secondary_file,
            timestamp_source="primary",
            ordering="primary_first",
            on_entry_count_mismatch="warn_pad",
            timestamp_tolerance_ms=self.tolerance_spin.value(),
            header_source="primary",
        )

        self.preview_table.show_merge_preview(
            self.primary_file.entries, self.secondary_file.entries, result.conflicts,
        )

    def _browse_output(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save merged file as", "",
            tr("@drop.file_filter")
        )
        if path:
            self.output_path.setText(path)

    def _on_merge(self):
        if not self.primary_file or not self.secondary_file:
            return

        out_path = self.output_path.text().strip()
        if not out_path:
            QMessageBox.warning(self, tr("@merge.missing_path_title"), tr("@merge.missing_path_msg"))
            return

        ts_src = "primary" if self.ts_primary_rb.isChecked() else "secondary"
        ordering = "primary_first" if self.order_pfirst_rb.isChecked() else "secondary_first"
        mm = "warn_pad" if self.mismatch_pad_rb.isChecked() else "truncate"
        tol = self.tolerance_spin.value()
        header_src = "primary" if self.header_primary_rb.isChecked() else "secondary"

        result = merge(
            self.primary_file, self.secondary_file,
            timestamp_source=ts_src, ordering=ordering,
            on_entry_count_mismatch=mm, timestamp_tolerance_ms=tol,
            header_source=header_src,
        )

        fmt_choice = self.fmt_combo.currentText()
        if fmt_choice == tr("@merge.same_as_primary") or fmt_choice == "Same as primary":
            out_fmt = self.primary_file.format
        else:
            try:
                out_fmt = SubtitleFormat[fmt_choice]
            except KeyError:
                out_fmt = self.primary_file.format

        result.merged_file.format = out_fmt

        # Strip ASS style override tags when outputting to non-ASS formats
        if out_fmt not in (SubtitleFormat.ASS, SubtitleFormat.SSA):
            for entry in result.merged_file.entries:
                entry.lines = [strip_ass_tags(line) for line in entry.lines]

        parser_cls = get_parser(out_fmt)
        text = parser_cls.write(result.merged_file)
        nl = getattr(self.primary_file, "_nl", "\r\n")
        write_subtitle_file(out_path, text, newline=nl)

        msg = tr("@merge.complete_msg", path=out_path)
        if result.conflicts:
            msg += "\n\n" + tr("@merge.warnings", n=len(result.conflicts))
            for idx, ctype, detail in result.conflicts[:5]:
                msg += tr("@merge.conflict_entry", idx=idx, ctype=ctype.name, detail=detail)
            if len(result.conflicts) > 5:
                msg += tr("@merge.conflict_more", n=len(result.conflicts) - 5)
        QMessageBox.information(self, tr("@merge.complete_title"), msg)
        self.status_message.emit(tr("@merge.status_done", path=out_path, n=len(result.conflicts)))
