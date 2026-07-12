from __future__ import annotations

import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import QFileDialog, QFrame, QLabel, QPushButton, QVBoxLayout

from gui.i18n import i18n, tr
from gui.ui_components import repolish


class DropZone(QFrame):
    file_changed = Signal(str)

    def __init__(
        self,
        label_key: str = "@sep.drop_label",
        *,
        compact: bool = False,
        badge_text: str = "SRT",
        replace_content_on_load: bool = False,
    ):
        super().__init__()
        self.setObjectName("drop_zone")
        self.setAcceptDrops(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setProperty("state", "idle")
        self.setProperty("compact", compact)
        self._label_key = label_key
        self._compact = compact
        self._file_path = ""
        self._badge_text = badge_text
        self._default_badge_text = badge_text
        self._replace_content_on_load = replace_content_on_load

        self.setMinimumHeight(112 if compact else 158)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 11, 12, 11)
        layout.setSpacing(4 if compact else 5)
        layout.setAlignment(Qt.AlignCenter)

        self.icon_label = QLabel(badge_text)
        self.icon_label.setObjectName("file_icon")
        self.icon_label.setProperty("compact", compact)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setFixedSize(35, 42) if compact else self.icon_label.setFixedSize(48, 56)
        layout.addWidget(self.icon_label, 0, Qt.AlignCenter)

        self.main_label = QLabel(tr(label_key))
        self.main_label.setObjectName("drop_main")
        self.main_label.setAlignment(Qt.AlignCenter)
        self.main_label.setWordWrap(True)
        layout.addWidget(self.main_label)

        self.hint_label = QLabel(tr("@drop.hint"))
        self.hint_label.setObjectName("drop_hint")
        self.hint_label.setAlignment(Qt.AlignCenter)
        self.hint_label.setWordWrap(True)
        layout.addWidget(self.hint_label)

        self.browse_btn = QPushButton(tr("@convert.choose_file"))
        self.browse_btn.setObjectName("mini_button")
        self.browse_btn.setCursor(Qt.PointingHandCursor)
        self.browse_btn.clicked.connect(self._browse)
        self.browse_btn.setVisible(not compact)
        layout.addWidget(self.browse_btn, 0, Qt.AlignCenter)

        i18n.language_changed.connect(self._on_language_changed)

    def _on_language_changed(self, _lang: str) -> None:
        if not (self._replace_content_on_load and self._file_path):
            self.main_label.setText(tr(self._label_key))
            self.hint_label.setText(tr("@drop.hint"))
        self.browse_btn.setText(tr("@convert.choose_file"))

    def set_badge(self, text: str) -> None:
        self._badge_text = text
        self.icon_label.setText(text)

    def set_loaded_metadata(self, path: str, badge: str | None = None, meta: str = "") -> None:
        self._file_path = path
        if badge:
            self.set_badge(badge)
        self.setProperty("state", "loaded")
        repolish(self)
        if self._replace_content_on_load:
            self.main_label.setText(os.path.basename(path))
            self.hint_label.setText(meta or path)

    def _set_state(self, state: str) -> None:
        self.setProperty("state", state)
        repolish(self)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._set_state("hover")

    def dragLeaveEvent(self, event) -> None:
        self._set_state("loaded" if self._file_path else "idle")
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            self._file_path = path
            self._set_state("loaded")
            self.file_changed.emit(path)
            event.acceptProposedAction()
        else:
            self._set_state("idle")

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._browse()
            event.accept()
            return
        super().mousePressEvent(event)

    def _browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            tr("@drop.select_title"),
            "",
            tr("@drop.file_filter"),
        )
        if path:
            self._file_path = path
            self._set_state("loaded")
            self.file_changed.emit(path)

    @property
    def file_path(self) -> str:
        return self._file_path

    def clear(self) -> None:
        self._file_path = ""
        self.set_badge(self._default_badge_text)
        self.main_label.setText(tr(self._label_key))
        self.hint_label.setText(tr("@drop.hint"))
        self._set_state("idle")
