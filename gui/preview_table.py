from PySide6.QtGui import QColor, QBrush
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
)

from gui.i18n import i18n, tr
from models.entry import SubtitleEntry
from utils.time_utils import format_srt_timestamp


TEXT_COLOR = QBrush(QColor("#3a3a3f"))
MUTED_COLOR = QBrush(QColor("#77777d"))
SUCCESS_COLOR = QBrush(QColor("#18843a"))
WARN_COLOR = QBrush(QColor("#b56b00"))


class PreviewTable(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setShowGrid(False)
        self.setWordWrap(True)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(46)
        self._last_sep_args = None
        self._last_merge_args = None
        i18n.language_changed.connect(self._on_language_changed)

    def _on_language_changed(self, _lang: str):
        if self._last_sep_args:
            self.show_separation_preview(*self._last_sep_args)
        elif self._last_merge_args:
            self.show_merge_preview(*self._last_merge_args)

    def show_separation_preview(
        self,
        entries: list[SubtitleEntry],
        lang1_idx: int,
        lang2_idx: int,
        empty_entries: list[int],
    ):
        self._last_sep_args = (entries, lang1_idx, lang2_idx, empty_entries)
        self._last_merge_args = None
        self.clear()
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels([
            tr("@table.index"),
            tr("@table.time"),
            tr("@table.line1"),
            tr("@table.line2"),
            tr("@table.status"),
        ])

        self.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            ts = f"{format_srt_timestamp(entry.start_time)}  →  {format_srt_timestamp(entry.end_time)}"
            self.setItem(row, 0, _item(str(entry.index), MUTED_COLOR))
            self.setItem(row, 1, _item(ts, MUTED_COLOR))

            line_count = len(entry.lines)
            line1 = entry.lines[lang1_idx] if lang1_idx < line_count else ""
            line2 = entry.lines[lang2_idx] if lang2_idx < line_count else ""
            self.setItem(row, 2, _item(line1))
            self.setItem(row, 3, _item(line2))

            if entry.index in empty_entries:
                self.setItem(row, 4, _item(tr("@table.missing_lines"), WARN_COLOR))
            else:
                self.setItem(row, 4, _item(tr("@table.ok"), SUCCESS_COLOR))

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

    def show_merge_preview(
        self,
        primary: list[SubtitleEntry],
        secondary: list[SubtitleEntry],
        conflicts: list[tuple[int, object, str]],
    ):
        self._last_merge_args = (primary, secondary, conflicts)
        self._last_sep_args = None
        self.clear()
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels([
            tr("@table.index"),
            tr("@table.time"),
            tr("@table.primary"),
            tr("@table.secondary"),
            tr("@table.status"),
        ])

        pmap = {entry.index: entry for entry in primary}
        smap = {entry.index: entry for entry in secondary}
        conflict_map = {item[0]: f"{item[1].name}: {item[2]}" for item in conflicts}
        all_indices = sorted(set(pmap) | set(smap))
        self.setRowCount(len(all_indices))

        for row, idx in enumerate(all_indices):
            p_entry = pmap.get(idx)
            s_entry = smap.get(idx)
            ts = format_srt_timestamp((p_entry or s_entry).start_time)
            self.setItem(row, 0, _item(str(idx), MUTED_COLOR))
            self.setItem(row, 1, _item(ts, MUTED_COLOR))
            self.setItem(row, 2, _item(
                p_entry.lines[0] if p_entry and p_entry.lines else tr("@table.missing")
            ))
            self.setItem(row, 3, _item(
                s_entry.lines[0] if s_entry and s_entry.lines else tr("@table.missing")
            ))

            if idx in conflict_map:
                self.setItem(row, 4, _item(conflict_map[idx], WARN_COLOR))
            else:
                self.setItem(row, 4, _item(tr("@table.ok"), SUCCESS_COLOR))

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

    def clear_preview(self):
        self._last_sep_args = None
        self._last_merge_args = None
        self.clear()
        self.setRowCount(0)
        self.setColumnCount(0)


def _item(text: str, brush: QBrush = TEXT_COLOR) -> QTableWidgetItem:
    item = QTableWidgetItem(text)
    item.setForeground(brush)
    return item
