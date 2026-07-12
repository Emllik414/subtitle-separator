"""Reusable light-theme UI components for the subtitle desktop app."""

from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QAbstractButton,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLayout,
    QVBoxLayout,
)


class AppleCard(QFrame):
    """Rounded white surface with a soft, restrained shadow."""

    def __init__(
        self,
        parent=None,
        *,
        horizontal: bool = False,
        margins: tuple[int, int, int, int] = (17, 17, 17, 17),
        spacing: int = 12,
        shadow: bool = True,
    ):
        super().__init__(parent)
        self.setObjectName("card")
        layout_cls: type[QLayout] = QHBoxLayout if horizontal else QVBoxLayout
        self.content_layout = layout_cls(self)
        self.content_layout.setContentsMargins(*margins)
        self.content_layout.setSpacing(spacing)

        if shadow:
            effect = QGraphicsDropShadowEffect(self)
            effect.setBlurRadius(24)
            effect.setOffset(0, 4)
            effect.setColor(QColor(0, 0, 0, 18))
            self.setGraphicsEffect(effect)


class ToggleSwitch(QAbstractButton):
    """Compact iOS-style toggle without external image assets."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFixedSize(42, 24)

    def sizeHint(self) -> QSize:
        return QSize(42, 24)

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        enabled = self.isEnabled()
        checked = self.isChecked()
        if not enabled:
            track = QColor("#d8d8dc")
        elif checked:
            track = QColor("#007aff")
        else:
            track = QColor("#c7c7cc")

        painter.setPen(Qt.NoPen)
        painter.setBrush(track)
        painter.drawRoundedRect(QRectF(0, 1, 42, 22), 11, 11)

        knob_x = 21 if checked else 3
        painter.setBrush(QColor("#ffffff"))
        painter.drawEllipse(QRectF(knob_x, 3, 18, 18))

        if self.hasFocus():
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QColor(0, 122, 255, 90))
            painter.drawRoundedRect(QRectF(0.5, 0.5, 41, 23), 11.5, 11.5)


class SettingBox(QFrame):
    """Small nested setting surface used in the merge panel."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settingBox")
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(11, 11, 11, 11)
        self.content_layout.setSpacing(8)


def repolish(widget) -> None:
    """Refresh Qt stylesheet selectors after a dynamic property changes."""

    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()


def set_tone(widget, tone: str) -> None:
    widget.setProperty("tone", tone)
    repolish(widget)
