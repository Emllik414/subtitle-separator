from __future__ import annotations

import os

from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from gui.drop_zone import DropZone
from gui.i18n import i18n, tr
from gui.preview_table import PreviewTable
from gui.ui_components import Card, FileSummary, PillGroup, SettingBox, StatusPill
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
        self._last_result = None

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        left = QWidget()
        left.setFixedWidth(360)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(14)
        left_layout.addWidget(self._build_import_card())
        left_layout.addWidget(self._build_options_card(), 1)
        root.addWidget(left)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(14)
        right_layout.addWidget(self._build_preview_card(), 1)
        right_layout.addWidget(self._build_output_card())
        root.addWidget(right, 1)

        self.output_path.installEventFilter(self)
        i18n.language_changed.connect(self._on_language_changed)
        self._on_language_changed(i18n.current_lang)

    def _build_import_card(self) -> Card:
        card = Card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(17, 16, 17, 16)
        layout.setSpacing(11)

        self.import_title = QLabel()
        self.import_title.setObjectName("card_title")
        self.import_desc = QLabel()
        self.import_desc.setObjectName("card_subtitle")
        self.import_desc.setWordWrap(True)
        layout.addWidget(self.import_title)
        layout.addWidget(self.import_desc)

        drops = QHBoxLayout()
        drops.setSpacing(10)
        self.primary_drop = DropZone(
            "@merge.preview_primary_drop",
            compact=True,
            badge_text="ZH",
            replace_content_on_load=True,
        )
        self.secondary_drop = DropZone(
            "@merge.preview_secondary_drop",
            compact=True,
            badge_text="EN",
            replace_content_on_load=True,
        )
        self.primary_drop.file_changed.connect(self._on_primary_loaded)
        self.secondary_drop.file_changed.connect(self._on_secondary_loaded)
        drops.addWidget(self.primary_drop)
        drops.addWidget(self.secondary_drop)
        layout.addLayout(drops)

        self.ready_summary = FileSummary()
        self.ready_summary.menu_button.hide()
        self.ready_summary.hide()
        layout.addWidget(self.ready_summary)
        return card

    def _build_options_card(self) -> Card:
        card = Card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(17, 16, 17, 16)
        layout.setSpacing(11)
        self.options_title = QLabel()
        self.options_title.setObjectName("card_title")
        layout.addWidget(self.options_title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)

        self.ts_box = SettingBox("")
        self.ts_group = PillGroup([("", "primary"), ("", "secondary")])
        self.ts_group.value_changed.connect(self._update_preview)
        self.ts_box.layout_box.addWidget(self.ts_group)
        grid.addWidget(self.ts_box, 0, 0)

        self.tolerance_box = SettingBox("")
        self.tolerance_group = PillGroup([("", "default"), ("", "custom")])
        self.tolerance_group.value_changed.connect(self._on_tolerance_mode_changed)
        self.tolerance_box.layout_box.addWidget(self.tolerance_group)
        self.tolerance_spin = QSpinBox()
        self.tolerance_spin.setObjectName("compact_spin")
        self.tolerance_spin.setRange(0, 9999)
        self.tolerance_spin.setValue(100)
        self.tolerance_spin.setSuffix(" ms")
        self.tolerance_spin.hide()
        self.tolerance_spin.valueChanged.connect(self._update_preview)
        self.tolerance_box.layout_box.addWidget(self.tolerance_spin)
        grid.addWidget(self.tolerance_box, 0, 1)

        self.order_box = SettingBox("")
        self.order_group = PillGroup([("", "primary_first"), ("", "secondary_first")])
        self.order_group.value_changed.connect(self._update_preview)
        self.order_box.layout_box.addWidget(self.order_group)
        grid.addWidget(self.order_box, 1, 0)

        self.mismatch_box = SettingBox("")
        self.mismatch_group = PillGroup([("", "warn_pad"), ("", "truncate")])
        self.mismatch_group.value_changed.connect(self._update_preview)
        self.mismatch_box.layout_box.addWidget(self.mismatch_group)
        grid.addWidget(self.mismatch_box, 1, 1)

        self.header_box = SettingBox("")
        self.header_group = PillGroup([("", "primary"), ("", "secondary")])
        self.header_group.value_changed.connect(self._update_preview)
        self.header_box.layout_box.addWidget(self.header_group)
        grid.addWidget(self.header_box, 2, 0)

        self.format_box = SettingBox("")
        self.fmt_combo = QComboBox()
        self.fmt_combo.setObjectName("format_combo")
        self.fmt_combo.currentIndexChanged.connect(self._on_format_changed)
        self.format_box.layout_box.addWidget(self.fmt_combo)
        grid.addWidget(self.format_box, 2, 1)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        layout.addLayout(grid)
        layout.addStretch()
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

        path_group = QVBoxLayout()
        path_group.setSpacing(5)
        self.output_label = QLabel()
        self.output_label.setObjectName("small_label")
        self.output_path = QLineEdit()
        self.output_path.setObjectName("path_field")
        path_group.addWidget(self.output_label)
        path_group.addWidget(self.output_path)
        layout.addLayout(path_group, 1)

        self.merge_btn = QPushButton()
        self.merge_btn.setObjectName("primary_button")
        self.merge_btn.setCursor(Qt.PointingHandCursor)
        self.merge_btn.setEnabled(False)
        self.merge_btn.clicked.connect(self._on_merge)
        layout.addWidget(self.merge_btn, 0, Qt.AlignBottom)
        return card

    def _on_language_changed(self, _lang: str) -> None:
        self.import_title.setText(tr("@merge.preview_import_title"))
        self.import_desc.setText(tr("@merge.preview_import_desc"))
        self.options_title.setText(tr("@merge.preview_options_title"))
        self.ts_box.set_title(tr("@merge.preview_ts_title"))
        self.ts_group.set_texts([tr("@merge.preview_primary"), tr("@merge.preview_secondary")])
        self.tolerance_box.set_title(tr("@merge.preview_tolerance_title"))
        self.tolerance_group.set_texts([tr("@merge.preview_100ms"), tr("@merge.preview_custom")])
        self.order_box.set_title(tr("@merge.preview_order_title"))
        self.order_group.set_texts([tr("@merge.preview_primary_top"), tr("@merge.preview_secondary_top")])
        self.mismatch_box.set_title(tr("@merge.preview_mismatch_title"))
        self.mismatch_group.set_texts([tr("@merge.preview_pad"), tr("@merge.preview_truncate")])
        self.header_box.set_title(tr("@merge.preview_style_title"))
        self.header_group.set_texts([tr("@merge.preview_primary"), tr("@merge.preview_secondary")])
        self.format_box.set_title(tr("@merge.preview_format_title"))
        self.preview_title.setText(tr("@merge.preview_title"))
        self.output_label.setText(tr("@merge.preview_output"))
        self.merge_btn.setText(tr("@merge.preview_start"))
        self._populate_format_combo()
        self._refresh_preview_header()

    def _populate_format_combo(self) -> None:
        previous = self.fmt_combo.currentText() if self.fmt_combo.count() else ""
        self.fmt_combo.blockSignals(True)
        self.fmt_combo.clear()
        self.fmt_combo.addItems([tr("@merge.same_as_primary"), "SRT", "ASS", "VTT"])
        index = self.fmt_combo.findText(previous)
        self.fmt_combo.setCurrentIndex(index if index >= 0 else 0)
        self.fmt_combo.blockSignals(False)

    def _load_subtitle(self, path: str) -> tuple[SubtitleFile, str, str]:
        text, encoding, newline = read_subtitle_file(path)
        fmt = detect_format(text)
        parser = get_parser(fmt)
        subtitle = parser.parse(text)
        subtitle._nl = newline
        return subtitle, fmt.name, encoding

    def _on_primary_loaded(self, path: str) -> None:
        try:
            self.primary_file, fmt, encoding = self._load_subtitle(path)
            self.primary_drop.set_loaded_metadata(
                path,
                fmt,
                tr("@merge.preview_compact_meta", fmt=fmt, count=len(self.primary_file.entries)),
            )
            self._check_ready()
        except Exception as exc:
            self.primary_file = None
            self.merge_btn.setEnabled(False)
            QMessageBox.warning(self, tr("@merge.preview_load_failed"), tr("@error.load", msg=str(exc)))

    def _on_secondary_loaded(self, path: str) -> None:
        try:
            self.secondary_file, fmt, encoding = self._load_subtitle(path)
            self.secondary_drop.set_loaded_metadata(
                path,
                fmt,
                tr("@merge.preview_compact_meta", fmt=fmt, count=len(self.secondary_file.entries)),
            )
            self._check_ready()
        except Exception as exc:
            self.secondary_file = None
            self.merge_btn.setEnabled(False)
            QMessageBox.warning(self, tr("@merge.preview_load_failed"), tr("@error.load", msg=str(exc)))

    def _check_ready(self) -> None:
        ready = bool(self.primary_file and self.secondary_file)
        self.merge_btn.setEnabled(ready)
        self.ready_summary.setVisible(ready)
        if not ready:
            self.preview_table.clear_preview()
            self._refresh_preview_header()
            return
        if not self.output_path.text().strip():
            self._update_default_output_path()
        self._update_preview()
        self.status_message.emit(tr("@merge.preview_ready_status"))

    def _on_tolerance_mode_changed(self, mode) -> None:
        self.tolerance_spin.setVisible(mode == "custom")
        self._update_preview()

    def _selected_tolerance(self) -> int:
        return self.tolerance_spin.value() if self.tolerance_group.value() == "custom" else 100

    def _update_preview(self, *_args) -> None:
        if not self.primary_file or not self.secondary_file:
            self.preview_table.clear_preview()
            self._refresh_preview_header()
            return
        result = merge(
            self.primary_file,
            self.secondary_file,
            timestamp_source=self.ts_group.value() or "primary",
            ordering=self.order_group.value() or "primary_first",
            on_entry_count_mismatch=self.mismatch_group.value() or "warn_pad",
            timestamp_tolerance_ms=self._selected_tolerance(),
            header_source=self.header_group.value() or "primary",
        )
        self._last_result = result
        self.preview_table.show_merge_preview(
            self.primary_file.entries,
            self.secondary_file.entries,
            result.conflicts,
        )
        total = max(len(self.primary_file.entries), len(self.secondary_file.entries), 1)
        match_rate = max(0.0, (total - len(result.conflicts)) / total * 100)
        self.ready_summary.set_file(
            tr("@merge.preview_ready_title"),
            tr(
                "@merge.preview_ready_meta",
                primary=len(self.primary_file.entries),
                secondary=len(self.secondary_file.entries),
                rate=f"{match_rate:.1f}",
            ),
        )
        self._refresh_preview_header(len(result.conflicts), match_rate)

    def _refresh_preview_header(self, conflicts: int = 0, rate: float = 0.0) -> None:
        if not self.primary_file or not self.secondary_file:
            self.preview_meta.setText(tr("@merge.preview_empty_meta"))
            self.preview_status.setText(tr("@merge.preview_waiting"))
            self.preview_status.set_tone("neutral")
            return
        total = max(len(self.primary_file.entries), len(self.secondary_file.entries))
        self.preview_meta.setText(tr("@merge.preview_meta", count=total, conflicts=conflicts))
        self.preview_status.setText(tr("@merge.preview_rate", rate=f"{rate:.1f}"))
        self.preview_status.set_tone("warning" if conflicts else "success")

    def _resolve_output_format(self) -> SubtitleFormat:
        if not self.primary_file:
            return SubtitleFormat.SRT
        choice = self.fmt_combo.currentText()
        if choice == tr("@merge.same_as_primary") or choice == "Same as primary":
            return self.primary_file.format
        try:
            return SubtitleFormat[choice]
        except KeyError:
            return self.primary_file.format

    def _on_format_changed(self, _index: int) -> None:
        self._update_default_output_path()

    def _update_default_output_path(self) -> None:
        if not self.primary_file or not self.primary_drop.file_path:
            return
        ext_map = {
            SubtitleFormat.SRT: ".srt",
            SubtitleFormat.ASS: ".ass",
            SubtitleFormat.SSA: ".ssa",
            SubtitleFormat.VTT: ".vtt",
        }
        base, _ = os.path.splitext(self.primary_drop.file_path)
        suffix = tr("@merge.preview_output_suffix")
        self.output_path.setText(f"{base}_{suffix}{ext_map.get(self._resolve_output_format(), '.srt')}")

    def eventFilter(self, watched, event) -> bool:
        if watched is self.output_path and event.type() == QEvent.MouseButtonDblClick:
            self._browse_output()
            return True
        return super().eventFilter(watched, event)

    def _browse_output(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            tr("@merge.preview_choose_output"),
            self.output_path.text(),
            tr("@drop.file_filter"),
        )
        if path:
            self.output_path.setText(path)

    def _on_merge(self) -> None:
        if not self.primary_file or not self.secondary_file:
            return
        output_path = self.output_path.text().strip()
        if not output_path:
            QMessageBox.warning(self, tr("@merge.missing_path_title"), tr("@merge.missing_path_msg"))
            return
        result = merge(
            self.primary_file,
            self.secondary_file,
            timestamp_source=self.ts_group.value() or "primary",
            ordering=self.order_group.value() or "primary_first",
            on_entry_count_mismatch=self.mismatch_group.value() or "warn_pad",
            timestamp_tolerance_ms=self._selected_tolerance(),
            header_source=self.header_group.value() or "primary",
        )
        out_fmt = self._resolve_output_format()
        result.merged_file.format = out_fmt
        if out_fmt not in (SubtitleFormat.ASS, SubtitleFormat.SSA):
            for entry in result.merged_file.entries:
                entry.lines = [strip_ass_tags(line) for line in entry.lines]
        parser = get_parser(out_fmt)
        newline = getattr(self.primary_file, "_nl", "\r\n")
        write_subtitle_file(output_path, parser.write(result.merged_file), newline=newline)
        message = tr("@merge.complete_msg", path=output_path)
        if result.conflicts:
            message += "\n\n" + tr("@merge.warnings", n=len(result.conflicts))
            for idx, conflict_type, detail in result.conflicts[:5]:
                message += tr("@merge.conflict_entry", idx=idx, ctype=conflict_type.name, detail=detail)
            if len(result.conflicts) > 5:
                message += tr("@merge.conflict_more", n=len(result.conflicts) - 5)
        QMessageBox.information(self, tr("@merge.complete_title"), message)
        self.status_message.emit(tr("@merge.status_done", path=output_path, n=len(result.conflicts)))
