from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QFileDialog, QFrame,
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent

from gui.i18n import i18n, tr


class DropZone(QWidget):
    file_changed = Signal(str)

    def __init__(self, label_key: str = "@sep.drop_label"):
        super().__init__()
        self.setAcceptDrops(True)
        self.setMinimumHeight(132)
        self._label_key = label_key
        self._has_file = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(9)

        self.drop_card = QFrame()
        self.drop_card.setObjectName("drop_card")
        self.drop_card.setProperty("dropState", "idle")
        self.drop_card.setAcceptDrops(True)
        self.drop_card.setMinimumHeight(88)

        card_layout = QVBoxLayout(self.drop_card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(3)

        self.drop_icon = QLabel("+")
        self.drop_icon.setObjectName("drop_icon")
        self.drop_icon.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.drop_icon)

        self.drop_label = QLabel(tr(label_key))
        self.drop_label.setObjectName("drop_label")
        self.drop_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.drop_label)

        self.drop_hint = QLabel(tr("@drop.hint"))
        self.drop_hint.setObjectName("drop_hint")
        self.drop_hint.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.drop_hint)
        layout.addWidget(self.drop_card)

        path_row = QHBoxLayout()
        path_row.setSpacing(8)

        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self._update_placeholder()
        path_row.addWidget(self.path_edit)

        self.browse_btn = QPushButton(tr("@drop.browse"))
        self.browse_btn.setProperty("role", "secondary")
        self.browse_btn.clicked.connect(self._browse)
        self.browse_btn.setFixedWidth(92)
        path_row.addWidget(self.browse_btn)
        layout.addLayout(path_row)

        i18n.language_changed.connect(self._on_language_changed)

    def _on_language_changed(self, lang: str):
        self.drop_label.setText(tr(self._label_key))
        self.drop_hint.setText(tr("@drop.hint"))
        self._update_placeholder()
        self.browse_btn.setText(tr("@drop.browse"))

    def _update_placeholder(self):
        self.path_edit.setPlaceholderText(tr("@drop.no_file"))

    def _set_state(self, state: str):
        self.drop_card.setProperty("dropState", state)
        self.drop_card.style().unpolish(self.drop_card)
        self.drop_card.style().polish(self.drop_card)
        self.drop_card.update()

    def _set_file_loaded_state(self):
        self._has_file = True
        self.drop_icon.setText("✓")
        self._set_state("loaded")

    def _set_empty_state(self):
        self._has_file = False
        self.drop_icon.setText("+")
        self._set_state("idle")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._set_state("hover")

    def dragLeaveEvent(self, event):
        self._set_state("loaded" if self._has_file else "idle")

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            self.path_edit.setText(path)
            self._set_file_loaded_state()
            self.file_changed.emit(path)
        else:
            self._set_empty_state()

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, tr("@drop.select_title"), "", tr("@drop.file_filter")
        )
        if path:
            self.path_edit.setText(path)
            self._set_file_loaded_state()
            self.file_changed.emit(path)

    @property
    def file_path(self) -> str:
        return self.path_edit.text()

    def clear(self):
        self.path_edit.clear()
        self._set_empty_state()
