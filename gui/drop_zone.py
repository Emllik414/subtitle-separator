from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFileDialog, QFrame
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent

from gui.i18n import i18n, tr


class DropZone(QWidget):
    file_changed = Signal(str)

    def __init__(self, label_key: str = "@sep.drop_label"):
        super().__init__()
        self.setAcceptDrops(True)
        self.setMinimumHeight(96)
        self._label_key = label_key
        self._has_file = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Drop target card
        self.drop_card = QFrame()
        self.drop_card.setAcceptDrops(True)
        self.drop_card.setMinimumHeight(60)
        self._idle_style = (
            "QFrame {"
            "  background-color: #252836;"
            "  border: 2px dashed #45475a;"
            "  border-radius: 10px;"
            "}"
        )
        self._hover_style = (
            "QFrame {"
            "  background-color: #2a3040;"
            "  border: 2px dashed #89b4fa;"
            "  border-radius: 10px;"
            "}"
        )
        self._file_loaded_style = (
            "QFrame {"
            "  background-color: #252836;"
            "  border: 2px solid #3d4057;"
            "  border-radius: 10px;"
            "}"
        )
        self.drop_card.setStyleSheet(self._idle_style)

        card_layout = QVBoxLayout(self.drop_card)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(4)

        self.drop_icon = QLabel("+")
        self.drop_icon.setAlignment(Qt.AlignCenter)
        self.drop_icon.setStyleSheet(
            "color: #585b70; font-size: 22px; font-weight: 300;"
            "background: transparent; border: none;"
        )
        card_layout.addWidget(self.drop_icon)

        self.drop_label = QLabel(tr(label_key))
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet(
            "color: #6c7086; font-size: 13px;"
            "background: transparent; border: none;"
        )
        card_layout.addWidget(self.drop_label)

        self.drop_hint = QLabel(tr("@drop.hint"))
        self.drop_hint.setAlignment(Qt.AlignCenter)
        self.drop_hint.setStyleSheet(
            "color: #585b70; font-size: 11px;"
            "background: transparent; border: none;"
        )
        card_layout.addWidget(self.drop_hint)

        layout.addWidget(self.drop_card)

        # Path + Browse row
        path_row = QHBoxLayout()
        path_row.setSpacing(8)

        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self._update_placeholder()
        path_row.addWidget(self.path_edit)

        self.browse_btn = QPushButton(tr("@drop.browse"))
        self.browse_btn.clicked.connect(self._browse)
        self.browse_btn.setFixedWidth(80)
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

    def _set_file_loaded_state(self):
        self._has_file = True
        self.drop_card.setStyleSheet(self._file_loaded_style)
        self.drop_icon.setStyleSheet(
            "color: #a6e3a1; font-size: 22px; font-weight: 300;"
            "background: transparent; border: none;"
        )
        self.drop_icon.setText("✓")

    def _set_empty_state(self):
        self._has_file = False
        self.drop_card.setStyleSheet(self._idle_style)
        self.drop_icon.setStyleSheet(
            "color: #585b70; font-size: 22px; font-weight: 300;"
            "background: transparent; border: none;"
        )
        self.drop_icon.setText("+")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.drop_card.setStyleSheet(self._hover_style)
            self.drop_icon.setStyleSheet(
                "color: #89b4fa; font-size: 22px; font-weight: 300;"
                "background: transparent; border: none;"
            )

    def dragLeaveEvent(self, event):
        if self._has_file:
            self._set_file_loaded_state()
        else:
            self._set_empty_state()

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
            self, tr("@drop.select_title"), "",
            tr("@drop.file_filter")
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
