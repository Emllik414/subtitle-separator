from __future__ import annotations

import os

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QMouseEvent
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gui.i18n import i18n, tr
from gui.ui_components import repolish


class ClickableFrame(QFrame):
    clicked = Signal()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.rect().contains(event.position().toPoint()):
            self.clicked.emit()
        super().mouseReleaseEvent(event)


class DropZone(QWidget):
    """Rounded file picker supporting click, browse and native drag-and-drop."""

    file_changed = Signal(str)

    def __init__(self, label_key: str = "@sep.drop_label", compact: bool = False):
        super().__init__()
        self.setAcceptDrops(True)
        self._label_key = label_key
        self._has_file = False
        self._compact = compact

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(9)

        self.drop_card = ClickableFrame()
        self.drop_card.setObjectName("dropCard")
        self.drop_card.setAcceptDrops(True)
        self.drop_card.setCursor(Qt.PointingHandCursor)
        self.drop_card.setMinimumHeight(112 if compact else 152)
        self.drop_card.clicked.connect(self._browse)
        self._set_card_state("idle")

        card_layout = QVBoxLayout(self.drop_card)
        card_layout.setContentsMargins(14, 13, 14, 13)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(5 if compact else 7)

        self.drop_icon = QLabel("SUB")
        self.drop_icon.setObjectName("fileIcon")
        self.drop_icon.setAlignment(Qt.AlignCenter)
        if compact:
            self.drop_icon.setFixedSize(38, 42)
        card_layout.addWidget(self.drop_icon, 0, Qt.AlignCenter)

        self.drop_label = QLabel(tr(label_key))
        self.drop_label.setObjectName("dropMain")
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setWordWrap(True)
        card_layout.addWidget(self.drop_label)

        self.drop_hint = QLabel(tr("@drop.hint"))
        self.drop_hint.setObjectName("dropHint")
        self.drop_hint.setAlignment(Qt.AlignCenter)
        self.drop_hint.setWordWrap(True)
        if not compact:
            card_layout.addWidget(self.drop_hint)

        self.browse_btn = QPushButton(tr("@drop.browse"))
        self.browse_btn.setObjectName("miniButton")
        self.browse_btn.setCursor(Qt.PointingHandCursor)
        self.browse_btn.clicked.connect(self._browse)
        self.browse_btn.setFixedWidth(76 if compact else 88)
        card_layout.addWidget(self.browse_btn, 0, Qt.AlignCenter)

        layout.addWidget(self.drop_card)

        self.summary = QFrame()
        self.summary.setObjectName("fileSummary")
        summary_layout = QHBoxLayout(self.summary)
        summary_layout.setContentsMargins(10, 8, 10, 8)
        summary_layout.setSpacing(9)

        check = QLabel("✓")
        check.setObjectName("fileCheck")
        check.setAlignment(Qt.AlignCenter)
        summary_layout.addWidget(check)

        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.path_edit.setFrame(False)
        self.path_edit.setObjectName("filePath")
        self._update_placeholder()
        summary_layout.addWidget(self.path_edit, 1)

        self.change_btn = QPushButton("…")
        self.change_btn.setObjectName("iconButton")
        self.change_btn.setToolTip(tr("@drop.browse"))
        self.change_btn.clicked.connect(self._browse)
        summary_layout.addWidget(self.change_btn)

        self.summary.setVisible(False)
        layout.addWidget(self.summary)

        i18n.language_changed.connect(self._on_language_changed)

    def _on_language_changed(self, _lang: str):
        self.drop_label.setText(tr(self._label_key))
        self.drop_hint.setText(tr("@drop.hint"))
        self._update_placeholder()
        self.browse_btn.setText(tr("@drop.browse"))
        self.change_btn.setToolTip(tr("@drop.browse"))

    def _update_placeholder(self):
        self.path_edit.setPlaceholderText(tr("@drop.no_file"))

    def _set_card_state(self, state: str):
        self.drop_card.setProperty("state", state)
        repolish(self.drop_card)

    def _set_file_loaded_state(self):
        self._has_file = True
        self._set_card_state("loaded")
        self.drop_icon.setText("✓")
        self.summary.setVisible(True)

    def _set_empty_state(self):
        self._has_file = False
        self._set_card_state("idle")
        self.drop_icon.setText("SUB")
        self.summary.setVisible(False)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._set_card_state("hover")

    def dragLeaveEvent(self, event):
        self._set_card_state("loaded" if self._has_file else "idle")
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if not urls:
            self._set_empty_state()
            return

        path = urls[0].toLocalFile()
        if path:
            self._set_path(path)
            event.acceptProposedAction()

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            tr("@drop.select_title"),
            "",
            tr("@drop.file_filter"),
        )
        if path:
            self._set_path(path)

    def _set_path(self, path: str):
        self.path_edit.setText(path)
        suffix = os.path.splitext(path)[1].lstrip(".").upper()
        self.drop_icon.setText(suffix[:3] or "SUB")
        self._set_file_loaded_state()
        self.drop_icon.setText(suffix[:3] or "✓")
        self.file_changed.emit(path)

    @property
    def file_path(self) -> str:
        return self.path_edit.text()

    def clear(self):
        self.path_edit.clear()
        self._set_empty_state()
