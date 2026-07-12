from __future__ import annotations

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizeGrip,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from gui.convert_panel import FormatConvertPanel
from gui.i18n import i18n, tr
from gui.merge_panel import MergePanel
from gui.separate_panel import SeparatePanel
from gui.styles import STYLESHEET
from gui.ui_components import SegmentedControl, add_card_shadow, repolish


class TitleBar(QFrame):
    def __init__(self, window: "MainWindow"):
        super().__init__(window)
        self._window = window
        self._drag_position: QPoint | None = None
        self.setObjectName("title_bar")
        self.setFixedHeight(54)

        layout = QGridLayout(self)
        layout.setContentsMargins(18, 0, 18, 0)
        layout.setHorizontalSpacing(8)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(2, 1)

        traffic = QWidget()
        traffic_layout = QHBoxLayout(traffic)
        traffic_layout.setContentsMargins(0, 0, 0, 0)
        traffic_layout.setSpacing(8)
        self.close_button = QPushButton()
        self.close_button.setObjectName("traffic_red")
        self.minimize_button = QPushButton()
        self.minimize_button.setObjectName("traffic_yellow")
        self.maximize_button = QPushButton()
        self.maximize_button.setObjectName("traffic_green")
        self.close_button.clicked.connect(window.close)
        self.minimize_button.clicked.connect(window.showMinimized)
        self.maximize_button.clicked.connect(window.toggle_maximized)
        for button in (self.close_button, self.minimize_button, self.maximize_button):
            button.setCursor(Qt.PointingHandCursor)
            traffic_layout.addWidget(button)
        traffic_layout.addStretch()
        layout.addWidget(traffic, 0, 0, Qt.AlignLeft | Qt.AlignVCenter)

        self.title_label = QLabel(tr("@app.short_title"))
        self.title_label.setObjectName("window_title")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label, 0, 1, Qt.AlignCenter)

        actions = QWidget()
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(8)
        self.help_button = QPushButton("?")
        self.help_button.setObjectName("help_button")
        self.help_button.setCursor(Qt.PointingHandCursor)
        self.help_button.clicked.connect(window.show_help)
        actions_layout.addWidget(self.help_button)

        self.language_combo = QComboBox()
        self.language_combo.setObjectName("language_combo")
        self.language_combo.addItem("中文", "zh")
        self.language_combo.addItem("English", "en")
        self.language_combo.setFixedWidth(86)
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        actions_layout.addWidget(self.language_combo)
        layout.addWidget(actions, 0, 2, Qt.AlignRight | Qt.AlignVCenter)

        target_index = self.language_combo.findData(i18n.current_lang)
        self.language_combo.blockSignals(True)
        self.language_combo.setCurrentIndex(target_index if target_index >= 0 else 0)
        self.language_combo.blockSignals(False)

    def _on_language_changed(self, index: int) -> None:
        language = self.language_combo.itemData(index)
        if language:
            i18n.set_language(language)

    def refresh_language(self) -> None:
        self.title_label.setText(tr("@app.short_title"))

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and not self._window.isMaximized():
            self._drag_position = event.globalPosition().toPoint() - self._window.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._drag_position is not None and event.buttons() & Qt.LeftButton:
            self._window.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self._drag_position = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._window.toggle_maximized()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("@window.title"))
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(1220, 900)
        self.setMinimumSize(1040, 760)
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet(STYLESHEET)

        central = QWidget()
        self.outer_layout = QVBoxLayout(central)
        self.outer_layout.setContentsMargins(14, 14, 14, 14)
        self.outer_layout.setSpacing(0)

        self.shell = QFrame()
        self.shell.setObjectName("app_shell")
        self.shell.setProperty("maximized", False)
        add_card_shadow(self.shell, blur=64, y_offset=18, alpha=38)
        shell_layout = QVBoxLayout(self.shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)
        self.outer_layout.addWidget(self.shell)
        self.setCentralWidget(central)

        self.title_bar = TitleBar(self)
        shell_layout.addWidget(self.title_bar)
        shell_layout.addWidget(self._build_header())
        shell_layout.addWidget(self._build_content(), 1)
        shell_layout.addWidget(self._build_footer())

        self.segmented.index_changed.connect(self._switch_page)
        self.separate_panel.status_message.connect(self.set_status)
        self.merge_panel.status_message.connect(self.set_status)
        self.convert_panel.status_message.connect(self.set_status)
        i18n.language_changed.connect(self._on_language_changed)
        self._on_language_changed(i18n.current_lang)

    def _build_header(self) -> QFrame:
        header = QFrame()
        header.setObjectName("header")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 23, 30, 18)
        layout.setSpacing(20)

        text_col = QVBoxLayout()
        text_col.setSpacing(4)
        self.eyebrow = QLabel("SUBTITLE STUDIO")
        self.eyebrow.setObjectName("eyebrow")
        self.page_title = QLabel()
        self.page_title.setObjectName("page_title")
        self.page_description = QLabel()
        self.page_description.setObjectName("page_description")
        self.page_description.setWordWrap(True)
        text_col.addWidget(self.eyebrow)
        text_col.addWidget(self.page_title)
        text_col.addWidget(self.page_description)
        layout.addLayout(text_col, 1)

        self.segmented = SegmentedControl(["", "", ""])
        layout.addWidget(self.segmented, 0, Qt.AlignBottom)
        return header

    def _build_content(self) -> QWidget:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 0, 30, 24)
        layout.setSpacing(0)
        self.stack = QStackedWidget()
        self.separate_panel = SeparatePanel()
        self.merge_panel = MergePanel()
        self.convert_panel = FormatConvertPanel()
        self.stack.addWidget(self.separate_panel)
        self.stack.addWidget(self.merge_panel)
        self.stack.addWidget(self.convert_panel)
        layout.addWidget(self.stack)
        return content

    def _build_footer(self) -> QFrame:
        footer = QFrame()
        footer.setObjectName("footer")
        footer.setFixedHeight(30)
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(19, 0, 10, 0)
        layout.setSpacing(6)
        dot = QLabel()
        dot.setObjectName("footer_dot")
        layout.addWidget(dot)
        self.footer_text = QLabel(tr("@status.ready"))
        self.footer_text.setObjectName("footer_text")
        layout.addWidget(self.footer_text)
        layout.addStretch()
        self.footer_note = QLabel(tr("@app.footer_note"))
        self.footer_note.setObjectName("footer_note")
        layout.addWidget(self.footer_note)
        grip = QSizeGrip(footer)
        grip.setFixedSize(14, 14)
        layout.addWidget(grip, 0, Qt.AlignBottom)
        return footer

    def _switch_page(self, index: int) -> None:
        if not 0 <= index < self.stack.count():
            return
        self.stack.setCurrentIndex(index)
        self.segmented.set_index(index)
        title_keys = [
            "@page.separate.title",
            "@page.merge.title",
            "@page.convert.title",
        ]
        description_keys = [
            "@page.separate.description",
            "@page.merge.description",
            "@page.convert.description",
        ]
        self.page_title.setText(tr(title_keys[index]))
        self.page_description.setText(tr(description_keys[index]))

    def _on_language_changed(self, _lang: str) -> None:
        self.setWindowTitle(tr("@window.title"))
        self.title_bar.refresh_language()
        self.segmented.set_texts([
            tr("@tab.separate.full"),
            tr("@tab.merge.full"),
            tr("@tab.convert"),
        ])
        self.footer_note.setText(tr("@app.footer_note"))
        self._switch_page(self.stack.currentIndex())
        self.set_status(tr("@status.ready"))

    def set_status(self, message: str) -> None:
        self.footer_text.setText(message or tr("@status.ready"))

    def toggle_maximized(self) -> None:
        if self.isMaximized():
            self.showNormal()
            maximized = False
            self.outer_layout.setContentsMargins(14, 14, 14, 14)
        else:
            self.showMaximized()
            maximized = True
            self.outer_layout.setContentsMargins(0, 0, 0, 0)
        self.shell.setProperty("maximized", maximized)
        self.title_bar.setProperty("maximized", maximized)
        repolish(self.shell)
        repolish(self.title_bar)

    def show_help(self) -> None:
        QMessageBox.information(
            self,
            tr("@app.help_title"),
            tr("@app.help_text"),
        )

    def closeEvent(self, event) -> None:
        event.accept()
