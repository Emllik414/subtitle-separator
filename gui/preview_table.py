from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem

from gui.i18n import tr
from models.entry import SubtitleEntry
from utils.time_utils import format_srt_timestamp

WARN_COLOR = QBrush(QColor("#b86b00"))
OK_COLOR = QBrush(QColor("#18843a"))
MUTED_COLOR = QBrush(QColor("#6f6f75"))
TEXT_COLOR = QBrush(QColor("#3a3a3f"))


class PreviewTable(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("preview_table")
        self.setAlternatingRowColors(False)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setShowGrid(False)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setHighlightSections(False)
        self.horizontalHeader().setStretchLastSection(False)
        self.setWordWrap(True)
        self.setFocusPolicy(Qt.NoFocus)
        self._last_sep_args = None
        self._last_merge_args = None

    def show_separation_preview(
        self,
        entries: list[SubtitleEntry],
        lang1_idx: int,
        lang2_idx: int,
        empty_entries: list[int],
        line1_title: str | None = None,
        line2_title: str | None = None,
    ) -> None:
        self._last_sep_args = (entries, lang1_idx, lang2_idx, empty_entries, line1_title, line2_title)
        self._last_merge_args = None
        self.clear()
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels([
            tr("@table.index"),
            tr("@table.timeline"),
            line1_title or tr("@table.line1"),
            line2_title or tr("@table.line2"),
            tr("@table.status"),
        ])
        self.setRowCount(len(entries))
        empty_set = set(empty_entries)
        for row, entry in enumerate(entries):
            ts = f"{format_srt_timestamp(entry.start_time)}  →  {format_srt_timestamp(entry.end_time)}"
            self.setItem(row, 0, _item(str(entry.index), MUTED_COLOR))
            self.setItem(row, 1, _item(ts, MUTED_COLOR))
            line1 = entry.lines[lang1_idx] if lang1_idx < len(entry.lines) else ""
            line2 = entry.lines[lang2_idx] if lang2_idx < len(entry.lines) else ""
            self.setItem(row, 2, _item(line1))
            self.setItem(row, 3, _item(line2))
            missing = entry.index in empty_set
            self.setItem(row, 4, _item(tr("@table.missing_lines") if missing else tr("@table.ok"), WARN_COLOR if missing else OK_COLOR))
            self.setRowHeight(row, 48)
        self._configure_columns()

    def show_merge_preview(
        self,
        primary: list[SubtitleEntry],
        secondary: list[SubtitleEntry],
        conflicts: list[tuple[int, object, str]],
    ) -> None:
        self._last_merge_args = (primary, secondary, conflicts)
        self._last_sep_args = None
        self.clear()
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels([
            tr("@table.index"),
            tr("@table.start_time"),
            tr("@table.primary"),
            tr("@table.secondary"),
            tr("@table.status"),
        ])
        pmap = {entry.index: entry for entry in primary}
        smap = {entry.index: entry for entry in secondary}
        conflict_map = {item[0]: item[2] for item in conflicts}
        all_indices = sorted(set(pmap) | set(smap))
        self.setRowCount(len(all_indices))
        for row, idx in enumerate(all_indices):
            p = pmap.get(idx)
            s = smap.get(idx)
            source = p or s
            ts = format_srt_timestamp(source.start_time) if source else ""
            self.setItem(row, 0, _item(str(idx), MUTED_COLOR))
            self.setItem(row, 1, _item(ts, MUTED_COLOR))
            self.setItem(row, 2, _item(p.lines[0] if p and p.lines else tr("@table.missing")))
            self.setItem(row, 3, _item(s.lines[0] if s and s.lines else tr("@table.missing")))
            if idx in conflict_map:
                self.setItem(row, 4, _item(conflict_map[idx], WARN_COLOR))
            else:
                self.setItem(row, 4, _item(tr("@table.matched"), OK_COLOR))
            self.setRowHeight(row, 48)
        self._configure_columns()

    def _configure_columns(self) -> None:
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        self.setColumnWidth(0, 54)
        self.setColumnWidth(1, 165)
        self.setColumnWidth(4, 92)

    def clear_preview(self) -> None:
        self._last_sep_args = None
        self._last_merge_args = None
        self.clear()
        self.setRowCount(0)
        self.setColumnCount(0)


def _item(text: str, brush: QBrush = TEXT_COLOR) -> QTableWidgetItem:
    item = QTableWidgetItem(text)
    item.setForeground(brush)
    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    return item
