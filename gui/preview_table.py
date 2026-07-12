from PySide6.QtWidgets import QTableWidget, QHeaderView, QAbstractItemView, QTableWidgetItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush

from models.entry import SubtitleEntry
from utils.time_utils import format_srt_timestamp
from gui.i18n import i18n, tr


WARN_COLOR = QBrush(QColor("#f9e2af"))
ERROR_COLOR = QBrush(QColor("#f38ba8"))


class PreviewTable(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self._last_sep_args = None
        self._last_merge_args = None
        i18n.language_changed.connect(self._on_language_changed)

    def _on_language_changed(self, lang: str):
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
            tr("@table.index"), tr("@table.time"),
            tr("@table.line1"), tr("@table.line2"),
            tr("@table.status"),
        ])

        self.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            ts = f"{format_srt_timestamp(entry.start_time)} --> {format_srt_timestamp(entry.end_time)}"
            self.setItem(row, 0, _item(str(entry.index)))
            self.setItem(row, 1, _item(ts))

            line_count = len(entry.lines)
            line1 = entry.lines[lang1_idx] if lang1_idx < line_count else ""
            line2 = entry.lines[lang2_idx] if lang2_idx < line_count else ""
            self.setItem(row, 2, _item(line1))
            self.setItem(row, 3, _item(line2))

            if entry.index in empty_entries:
                item = _item(tr("@table.missing_lines"))
                item.setForeground(WARN_COLOR)
                self.setItem(row, 4, item)
            else:
                self.setItem(row, 4, _item(tr("@table.ok")))

        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)

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
            tr("@table.index"), tr("@table.time"),
            tr("@table.primary"), tr("@table.secondary"),
            tr("@table.status"),
        ])

        pmap = {e.index: e for e in primary}
        smap = {e.index: e for e in secondary}
        conflict_map = {c[0]: f"{c[1].name}: {c[2]}" for c in conflicts}

        all_indices = sorted(set(pmap.keys()) | set(smap.keys()))
        self.setRowCount(len(all_indices))

        for row, idx in enumerate(all_indices):
            p = pmap.get(idx)
            s = smap.get(idx)
            ts = format_srt_timestamp((p or s).start_time)
            self.setItem(row, 0, _item(str(idx)))
            self.setItem(row, 1, _item(ts))
            self.setItem(row, 2, _item(p.lines[0] if p and p.lines else tr("@table.missing")))
            self.setItem(row, 3, _item(s.lines[0] if s and s.lines else tr("@table.missing")))

            status = conflict_map.get(idx, tr("@table.ok"))
            item = _item(status)
            if idx in conflict_map:
                item.setForeground(WARN_COLOR)
            self.setItem(row, 4, item)

        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)

    def clear_preview(self):
        self._last_sep_args = None
        self._last_merge_args = None
        self.clear()
        self.setRowCount(0)
        self.setColumnCount(0)


def _item(text: str) -> QTableWidgetItem:
    item = QTableWidgetItem(text)
    item.setForeground(QBrush(QColor("#cdd6f4")))
    return item
