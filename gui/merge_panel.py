from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from gui.drop_zone import DropZone
from gui.i18n import i18n, tr
from gui.preview_table import PreviewTable
from gui.ui_components import AppleCard, SettingBox, set_tone
from logic.merger import merge
from models.entry import SubtitleFile
from models.enums import SubtitleFormat
from parsers.base import detect_format, get_parser
from utils.text import read_subtitle_file, strip_ass_tags, write_subtitle_file


class MergePanel(QWidget):
    status_message = Signal(str)

    def __init__(self):
        super().__init__()
        self.primary_file: SubtitleFile | None = None
        self.secondary_file: SubtitleFile | None = None

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        left = QWidget()
        left.setFixedWidth(372)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(14)
        root.addWidget(left)

        import_card = AppleCard(spacing=10)
        self.import_title = QLabel(tr("@merge.import_title"))
        self.import_title.setObjectName("sectionTitle")
        self.import_desc = QLabel(tr("@merge.import_desc"))
        self.import_desc.setObjectName("sectionSubtitle")
        self.import_desc.setWordWrap(True)
        import_card.content_layout.addWidget(self.import_title)
        import_card.content_layout.addWidget(self.import_desc)

        drops = QHBoxLayout()
        drops.setSpacing(9)

        primary_col = QVBoxLayout()
        primary_col.setSpacing(6)
        self.primary_label_w = QLabel(tr("@merge.primary_label"))
        self.primary_label_w.setObjectName("fieldLabel")
        self.primary_drop = DropZone("@merge.primary_drop", compact=True)
        self.primary_drop.file_changed.connect(self._on_primary_loaded)
        self.primary_info = QLabel(tr("@merge.no_file"))
        self.primary_info.setObjectName("metaText")
        self.primary_info.setWordWrap(True)
        set_tone(self.primary_info, "muted")
        primary_col.addWidget(self.primary_label_w)
        primary_col.addWidget(self.primary_drop)
        primary_col.addWidget(self.primary_info)
        drops.addLayout(primary_col)

        secondary_col = QVBoxLayout()
        secondary_col.setSpacing(6)
        self.secondary_label_w = QLabel(tr("@merge.secondary_label"))
        self.secondary_label_w.setObjectName("fieldLabel")
        self.secondary_drop = DropZone("@merge.secondary_drop", compact=True)
        self.secondary_drop.file_changed.connect(self._on_secondary_loaded)
        self.secondary_info = QLabel(tr("@merge.no_file"))
        self.secondary_info.setObjectName("metaText")
        self.secondary_info.setWordWrap(True)
        set_tone(self.secondary_info, "muted")
        secondary_col.addWidget(self.secondary_label_w)
        secondary_col.addWidget(self.secondary_drop)
        secondary_col.addWidget(self.secondary_info)
        drops.addLayout(secondary_col)
        import_card.content_layout.addLayout(drops)
        left_layout.addWidget(import_card)

        options_card = AppleCard(spacing=10)
        self.options_title = QLabel(tr("@merge.options"))
        self.options_title.setObjectName("sectionTitle")
        options_card.content_layout.addWidget(self.options_title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(9)
        grid.setVerticalSpacing(9)

        ts_box = SettingBox()
        self.ts_label = QLabel(tr("@merge.ts_source"))
        self.ts_label.setObjectName("fieldLabel")
        ts_box.content_layout.addWidget(self.ts_label)
        ts_row = QHBoxLayout()
        ts_row.setSpacing(6)
        self.ts_btn_group = QButtonGroup(self)
        self.ts_primary_rb = QRadioButton(tr("@merge.ts_primary_short"))
        self.ts_secondary_rb = QRadioButton(tr("@merge.ts_secondary_short"))
        self.ts_primary_rb.setChecked(True)
        self.ts_btn_group.addButton(self.ts_primary_rb, 0)
        self.ts_btn_group.addButton(self.ts_secondary_rb, 1)
        ts_row.addWidget(self.ts_primary_rb)
        ts_row.addWidget(self.ts_secondary_rb)
        ts_row.addStretch()
        ts_box.content_layout.addLayout(ts_row)
        grid.addWidget(ts_box, 0, 0)

        tol_box = SettingBox()
        self.tol_label = QLabel(tr("@merge.tolerance"))
        self.tol_label.setObjectName("fieldLabel")
        tol_box.content_layout.addWidget(self.tol_label)
        self.tolerance_spin = QSpinBox()
        self.tolerance_spin.setRange(0, 9999)
        self.tolerance_spin.setValue(100)
        self.tolerance_spin.setSuffix(" ms")
        tol_box.content_layout.addWidget(self.tolerance_spin)
        grid.addWidget(tol_box, 0, 1)

        order_box = SettingBox()
        self.order_label = QLabel(tr("@merge.ordering"))
        self.order_label.setObjectName("fieldLabel")
        order_box.content_layout.addWidget(self.order_label)
        order_row = QHBoxLayout()
        order_row.setSpacing(6)
        self.order_btn_group = QButtonGroup(self)
        self.order_pfirst_rb = QRadioButton(tr("@merge.order_pfirst_short"))
        self.order_sfirst_rb = QRadioButton(tr("@merge.order_sfirst_short"))
        self.order_pfirst_rb.setChecked(True)
        self.order_btn_group.addButton(self.order_pfirst_rb, 0)
        self.order_btn_group.addButton(self.order_sfirst_rb, 1)
        order_row.addWidget(self.order_pfirst_rb)
        order_row.addWidget(self.order_sfirst_rb)
        order_row.addStretch()
        order_box.content_layout.addLayout(order_row)
        grid.addWidget(order_box, 1, 0)

        mismatch_box = SettingBox()
        self.mismatch_label = QLabel(tr("@merge.mismatch_label"))
        self.mismatch_label.setObjectName("fieldLabel")
        mismatch_box.content_layout.addWidget(self.mismatch_label)
        mismatch_row = QHBoxLayout()
        mismatch_row.setSpacing(6)
        self.mismatch_btn_group = QButtonGroup(self)
        self.mismatch_pad_rb = QRadioButton(tr("@merge.mismatch_pad_short"))
        self.mismatch_trunc_rb = QRadioButton(tr("@merge.mismatch_trunc_short"))
        self.mismatch_pad_rb.setChecked(True)
        self.mismatch_btn_group.addButton(self.mismatch_pad_rb, 0)
        self.mismatch_btn_group.addButton(self.mismatch_trunc_rb, 1)
        mismatch_row.addWidget(self.mismatch_pad_rb)
        mismatch_row.addWidget(self.mismatch_trunc_rb)
        mismatch_row.addStretch()
        mismatch_box.content_layout.addLayout(mismatch_row)
        grid.addWidget(mismatch_box, 1, 1)

        header_box = SettingBox()
        self.header_label = QLabel(tr("@merge.header_label"))
        self.header_label.setObjectName("fieldLabel")
        header_box.content_layout.addWidget(self.header_label)
        header_row = QHBoxLayout()
        header_row.setSpacing(6)
        self.header_btn_group = QButtonGroup(self)
        self.header_primary_rb = QRadioButton(tr("@merge.header_primary"))
        self.header_secondary_rb = QRadioButton(tr("@merge.header_secondary"))
        self.header_primary_rb.setChecked(True)
        self.header_btn_group.addButton(self.header_primary_rb, 0)
        self.header_btn_group.addButton(self.header_secondary_rb, 1)
        header_row.addWidget(self.header_primary_rb)
        header_row.addWidget(self.header_secondary_rb)
        header_row.addStretch()
        header_box.content_layout.addLayout(header_row)
        grid.addWidget(header_box, 2, 0)

        format_box = SettingBox()
        self.fmt_label = QLabel(tr("@merge.output_format"))
        self.fmt_label.setObjectName("fieldLabel")
        format_box.content_layout.addWidget(self.fmt_label)
        self.fmt_combo = QComboBox()
        self._populate_format_combo()
        format_box.content_layout.addWidget(self.fmt_combo)
        grid.addWidget(format_box, 2, 1)

        options_card.content_layout.addLayout(grid)
        left_layout.addWidget(options_card)
        left_layout.addStretch()

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(14)
        root.addWidget(right, 1)

        preview_card = AppleCard(margins=(0, 0, 0, 0), spacing=0)
        preview_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        preview_header = QWidget()
        preview_header_layout = QHBoxLayout(preview_header)
        preview_header_layout.setContentsMargins(17, 14, 17, 12)
        preview_header_layout.setSpacing(12)
        preview_text = QVBoxLayout()
        preview_text.setSpacing(2)
        self.preview_title = QLabel(tr("@merge.preview_title"))
        self.preview_title.setObjectName("sectionTitle")
        self.preview_meta = QLabel(tr("@merge.preview_empty"))
        self.preview_meta.setObjectName("sectionSubtitle")
        preview_text.addWidget(self.preview_title)
        preview_text.addWidget(self.preview_meta)
        preview_header_layout.addLayout(preview_text, 1)
        self.preview_status = QLabel(tr("@merge.preview_waiting"))
        self.preview_status.setObjectName("pill")
        set_tone(self.preview_status, "warning")
        preview_header_layout.addWidget(self.preview_status)
        preview_card.content_layout.addWidget(preview_header)

        self.preview_table = PreviewTable()
        preview_card.content_layout.addWidget(self.preview_table, 1)
        right_layout.addWidget(preview_card, 1)

        output_card = AppleCard(horizontal=True, margins=(15, 14, 15, 14), spacing=12)
        output_group = QVBoxLayout()
        output_group.setSpacing(5)
        self.out_label = QLabel(tr("@merge.output"))
        self.out_label.setObjectName("fieldLabel")
        output_group.addWidget(self.out_label)
        path_row = QHBoxLayout()
        path_row.setSpacing(6)
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText(tr("@merge.output_placeholder"))
        path_row.addWidget(self.output_path, 1)
        browse = QPushButton("…")
        browse.setObjectName("iconButton")
        browse.clicked.connect(self._browse_output)
        path_row.addWidget(browse)
        output_group.addLayout(path_row)
        output_card.content_layout.addLayout(output_group, 1)

        self.merge_btn = QPushButton(tr("@merge.btn_merge"))
        self.merge_btn.setObjectName("primaryButton")
        self.merge_btn.setMinimumWidth(124)
        self.merge_btn.setEnabled(False)
        self.merge_btn.clicked.connect(self._on_merge)
        output_card.content_layout.addWidget(self.merge_btn, 0, Qt.AlignBottom)
        right_layout.addWidget(output_card)

        for button in (
            self.ts_primary_rb,
            self.ts_secondary_rb,
            self.order_pfirst_rb,
            self.order_sfirst_rb,
            self.mismatch_pad_rb,
            self.mismatch_trunc_rb,
            self.header_primary_rb,
            self.header_secondary_rb,
        ):
            button.toggled.connect(self._option_changed)
        self.tolerance_spin.valueChanged.connect(self._option_changed)

        i18n.language_changed.connect(self._on_language_changed)

    def _on_language_changed(self, _lang: str):
        self.import_title.setText(tr("@merge.import_title"))
        self.import_desc.setText(tr("@merge.import_desc"))
        self.primary_label_w.setText(tr("@merge.primary_label"))
        self.secondary_label_w.setText(tr("@merge.secondary_label"))
        self.options_title.setText(tr("@merge.options"))
        self.ts_label.setText(tr("@merge.ts_source"))
        self.ts_primary_rb.setText(tr("@merge.ts_primary_short"))
        self.ts_secondary_rb.setText(tr("@merge.ts_secondary_short"))
        self.tol_label.setText(tr("@merge.tolerance"))
        self.order_label.setText(tr("@merge.ordering"))
        self.order_pfirst_rb.setText(tr("@merge.order_pfirst_short"))
        self.order_sfirst_rb.setText(tr("@merge.order_sfirst_short"))
        self.mismatch_label.setText(tr("@merge.mismatch_label"))
        self.mismatch_pad_rb.setText(tr("@merge.mismatch_pad_short"))
        self.mismatch_trunc_rb.setText(tr("@merge.mismatch_trunc_short"))
        self.header_label.setText(tr("@merge.header_label"))
        self.header_primary_rb.setText(tr("@merge.header_primary"))
        self.header_secondary_rb.setText(tr("@merge.header_secondary"))
        self.fmt_label.setText(tr("@merge.output_format"))
        self.preview_title.setText(tr("@merge.preview_title"))
        self.out_label.setText(tr("@merge.output"))
        self.output_path.setPlaceholderText(tr("@merge.output_placeholder"))
        self.merge_btn.setText(tr("@merge.btn_merge"))
        self._populate_format_combo()

        if not self.primary_file:
            self.primary_info.setText(tr("@merge.no_file"))
        if not self.secondary_file:
            self.secondary_info.setText(tr("@merge.no_file"))
        if self.primary_file and self.secondary_file:
            self._update_preview()
        else:
            self.preview_meta.setText(tr("@merge.preview_empty"))
            self.preview_status.setText(tr("@merge.preview_waiting"))

    def _populate_format_combo(self):
        current = self.fmt_combo.currentText() if self.fmt_combo.count() else ""
        self.fmt_combo.blockSignals(True)
        self.fmt_combo.clear()
        self.fmt_combo.addItems([
            tr("@merge.same_as_primary"),
            "SRT",
            "ASS",
            "VTT",
        ])
        index = self.fmt_combo.findText(current)
        if index >= 0:
            self.fmt_combo.setCurrentIndex(index)
        self.fmt_combo.blockSignals(False)

    def _on_primary_loaded(self, path: str):
        try:
            text, _enc, nl = read_subtitle_file(path)
            fmt = detect_format(text)
            parser = get_parser(fmt)
            self.primary_file = parser.parse(text)
            self.primary_file._nl = nl
            self.primary_info.setText(
                tr("@merge.format_info", fmt=fmt.name, n=len(self.primary_file.entries))
            )
            set_tone(self.primary_info, "success")
            self._check_ready()
        except Exception as exc:
            self.primary_info.setText(tr("@error.load", msg=str(exc)))
            set_tone(self.primary_info, "error")
            self.primary_file = None
            self.merge_btn.setEnabled(False)
            self._refresh_preview_state()

    def _on_secondary_loaded(self, path: str):
        try:
            text, _enc, nl = read_subtitle_file(path)
            fmt = detect_format(text)
            parser = get_parser(fmt)
            self.secondary_file = parser.parse(text)
            self.secondary_file._nl = nl
            self.secondary_info.setText(
                tr("@merge.format_info", fmt=fmt.name, n=len(self.secondary_file.entries))
            )
            set_tone(self.secondary_info, "success")
            self._check_ready()
        except Exception as exc:
            self.secondary_info.setText(tr("@error.load", msg=str(exc)))
            set_tone(self.secondary_info, "error")
            self.secondary_file = None
            self.merge_btn.setEnabled(False)
            self._refresh_preview_state()

    def _check_ready(self):
        ready = bool(self.primary_file and self.secondary_file)
        self.merge_btn.setEnabled(ready)
        if not ready:
            self._refresh_preview_state()
            return

        if not self.output_path.text().strip():
            ext_map = {
                SubtitleFormat.SRT: ".srt",
                SubtitleFormat.ASS: ".ass",
                SubtitleFormat.SSA: ".ass",
                SubtitleFormat.VTT: ".vtt",
            }
            ext = ext_map.get(self.primary_file.format, ".srt")
            source = self.primary_drop.file_path
            base = source.rsplit(".", 1)[0] if "." in source else "merged"
            self.output_path.setText(f"{base}_bilingual{ext}")
        self._update_preview()

    def _current_options(self) -> dict[str, object]:
        return {
            "timestamp_source": "primary" if self.ts_primary_rb.isChecked() else "secondary",
            "ordering": "primary_first" if self.order_pfirst_rb.isChecked() else "secondary_first",
            "on_entry_count_mismatch": "warn_pad" if self.mismatch_pad_rb.isChecked() else "truncate",
            "timestamp_tolerance_ms": self.tolerance_spin.value(),
            "header_source": "primary" if self.header_primary_rb.isChecked() else "secondary",
        }

    def _option_changed(self, *_args):
        if self.primary_file and self.secondary_file:
            self._update_preview()

    def _update_preview(self):
        if not self.primary_file or not self.secondary_file:
            self._refresh_preview_state()
            return

        result = merge(self.primary_file, self.secondary_file, **self._current_options())
        self.preview_table.show_merge_preview(
            self.primary_file.entries,
            self.secondary_file.entries,
            result.conflicts,
        )
        total = max(len(self.primary_file.entries), len(self.secondary_file.entries))
        conflicts = len(result.conflicts)
        self.preview_meta.setText(tr("@merge.preview_meta", count=total, conflicts=conflicts))
        if conflicts:
            match_rate = max(0.0, (total - conflicts) / max(total, 1) * 100)
            self.preview_status.setText(tr("@merge.preview_match_rate", rate=f"{match_rate:.1f}"))
            set_tone(self.preview_status, "warning")
        else:
            self.preview_status.setText(tr("@merge.preview_all_ok"))
            set_tone(self.preview_status, "success")

    def _refresh_preview_state(self):
        self.preview_table.clear_preview()
        self.preview_meta.setText(tr("@merge.preview_empty"))
        self.preview_status.setText(tr("@merge.preview_waiting"))
        set_tone(self.preview_status, "warning")

    def _browse_output(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            tr("@merge.save_as"),
            self.output_path.text(),
            tr("@drop.file_filter"),
        )
        if path:
            self.output_path.setText(path)

    def _on_merge(self):
        if not self.primary_file or not self.secondary_file:
            return

        out_path = self.output_path.text().strip()
        if not out_path:
            QMessageBox.warning(
                self,
                tr("@merge.missing_path_title"),
                tr("@merge.missing_path_msg"),
            )
            return

        result = merge(self.primary_file, self.secondary_file, **self._current_options())

        fmt_choice = self.fmt_combo.currentText()
        if fmt_choice in (tr("@merge.same_as_primary"), "Same as primary"):
            out_fmt = self.primary_file.format
        else:
            try:
                out_fmt = SubtitleFormat[fmt_choice]
            except KeyError:
                out_fmt = self.primary_file.format
        result.merged_file.format = out_fmt

        if out_fmt not in (SubtitleFormat.ASS, SubtitleFormat.SSA):
            for entry in result.merged_file.entries:
                entry.lines = [strip_ass_tags(line) for line in entry.lines]

        parser_cls = get_parser(out_fmt)
        text = parser_cls.write(result.merged_file)
        newline = getattr(self.primary_file, "_nl", "\r\n")
        write_subtitle_file(out_path, text, newline=newline)

        message = tr("@merge.complete_msg", path=out_path)
        if result.conflicts:
            message += "\n\n" + tr("@merge.warnings", n=len(result.conflicts))
            for idx, conflict_type, detail in result.conflicts[:5]:
                message += tr(
                    "@merge.conflict_entry",
                    idx=idx,
                    ctype=conflict_type.name,
                    detail=detail,
                )
            if len(result.conflicts) > 5:
                message += tr("@merge.conflict_more", n=len(result.conflicts) - 5)

        QMessageBox.information(self, tr("@merge.complete_title"), message)
        self.status_message.emit(
            tr("@merge.status_done", path=out_path, n=len(result.conflicts))
        )
