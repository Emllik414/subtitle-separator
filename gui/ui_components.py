from __future__ import annotations

from typing import Any, Iterable

from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QAbstractButton,
    QButtonGroup,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


def repolish(widget: QWidget) -> None:
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()


def add_card_shadow(widget: QWidget, blur: int = 24, y_offset: int = 8, alpha: int = 10) -> None:
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur)
    effect.setOffset(0, y_offset)
    effect.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(effect)


class Card(QFrame):
    def __init__(self, parent: QWidget | None = None, shadow: bool = True):
        super().__init__(parent)
        self.setObjectName("card")
        if shadow:
            add_card_shadow(self)


class ToggleSwitch(QAbstractButton):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(38, 22)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        track = QColor("#007aff") if self.isChecked() else QColor("#d1d1d6")
        painter.setPen(Qt.NoPen)
        painter.setBrush(track)
        painter.drawRoundedRect(QRectF(0, 0, 38, 22), 11, 11)
        knob_x = 18 if self.isChecked() else 2
        painter.setBrush(QColor("#ffffff"))
        painter.setPen(QPen(QColor(0, 0, 0, 28), 1))
        painter.drawEllipse(QRectF(knob_x, 2, 18, 18))

    def sizeHint(self):
        return self.minimumSizeHint()


class SegmentedControl(QFrame):
    index_changed = Signal(int)

    def __init__(self, items: Iterable[str], parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("segmented_control")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(3)
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons: list[QPushButton] = []
        for index, text in enumerate(items):
            button = QPushButton(text)
            button.setProperty("segment", True)
            button.setCheckable(True)
            button.setCursor(Qt.PointingHandCursor)
            button.setMinimumWidth(108)
            button.setFixedHeight(34)
            self._group.addButton(button, index)
            self._buttons.append(button)
            layout.addWidget(button)
        self._group.idClicked.connect(self.index_changed.emit)
        if self._buttons:
            self._buttons[0].setChecked(True)

    def set_index(self, index: int) -> None:
        if 0 <= index < len(self._buttons):
            self._buttons[index].setChecked(True)

    def set_texts(self, texts: Iterable[str]) -> None:
        for button, text in zip(self._buttons, texts):
            button.setText(text)


class PillGroup(QWidget):
    value_changed = Signal(object)

    def __init__(self, items: Iterable[tuple[str, Any]], parent: QWidget | None = None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(7)
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons: list[QPushButton] = []
        self._values: list[Any] = []
        for index, (text, value) in enumerate(items):
            button = QPushButton(text)
            button.setProperty("pill", True)
            button.setCheckable(True)
            button.setCursor(Qt.PointingHandCursor)
            self._group.addButton(button, index)
            self._buttons.append(button)
            self._values.append(value)
            layout.addWidget(button)
        layout.addStretch()
        self._group.idClicked.connect(self._on_clicked)
        if self._buttons:
            self._buttons[0].setChecked(True)

    def _on_clicked(self, index: int) -> None:
        if 0 <= index < len(self._values):
            self.value_changed.emit(self._values[index])

    def value(self) -> Any:
        checked = self._group.checkedId()
        return self._values[checked] if 0 <= checked < len(self._values) else None

    def set_value(self, value: Any) -> None:
        if value in self._values:
            self._buttons[self._values.index(value)].setChecked(True)

    def set_texts(self, texts: Iterable[str]) -> None:
        for button, text in zip(self._buttons, texts):
            button.setText(text)


class StatusPill(QLabel):
    def __init__(self, text: str = "", tone: str = "success", parent: QWidget | None = None):
        super().__init__(text, parent)
        self.setObjectName("status_pill")
        self.setAlignment(Qt.AlignCenter)
        self.set_tone(tone)

    def set_tone(self, tone: str) -> None:
        self.setProperty("tone", tone)
        repolish(self)


class SettingBox(QFrame):
    def __init__(self, title: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("setting_box")
        self.layout_box = QVBoxLayout(self)
        self.layout_box.setContentsMargins(11, 10, 11, 10)
        self.layout_box.setSpacing(7)
        self.title_label = QLabel(title)
        self.title_label.setObjectName("setting_label")
        self.layout_box.addWidget(self.title_label)

    def set_title(self, text: str) -> None:
        self.title_label.setText(text)


class FileSummary(QFrame):
    replace_requested = Signal()
    clear_requested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("file_summary")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 9, 10, 9)
        layout.setSpacing(10)

        check = QLabel("✓")
        check.setObjectName("file_check")
        check.setAlignment(Qt.AlignCenter)
        check.setFixedSize(26, 26)
        layout.addWidget(check)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(2)
        self.name_label = QLabel("")
        self.name_label.setObjectName("file_name")
        self.name_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.meta_label = QLabel("")
        self.meta_label.setObjectName("file_meta")
        text_col.addWidget(self.name_label)
        text_col.addWidget(self.meta_label)
        layout.addLayout(text_col, 1)

        self.menu_button = QPushButton("•••")
        self.menu_button.setObjectName("more_button")
        self.menu_button.setCursor(Qt.PointingHandCursor)
        self.menu_button.setFixedSize(30, 28)
        self.menu_button.clicked.connect(self.replace_requested.emit)
        self.menu_button.setToolTip("Choose another file")
        layout.addWidget(self.menu_button)

    def set_file(self, name: str, meta: str) -> None:
        self.name_label.setText(name)
        self.meta_label.setText(meta)
