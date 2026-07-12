from PySide6.QtWidgets import QMainWindow, QTabWidget, QStatusBar, QLabel, QComboBox, QHBoxLayout, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from gui.separate_panel import SeparatePanel
from gui.merge_panel import MergePanel
from gui.convert_panel import FormatConvertPanel
from gui.styles import STYLESHEET
from gui.i18n import i18n, tr


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("@window.title"))
        self.resize(1060, 920)
        self.setMinimumSize(960, 780)
        self.setStyleSheet(STYLESHEET)

        font = QFont("Microsoft YaHei", 10)
        self.setFont(font)

        central = QWidget()
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        # Language switcher bar
        lang_bar = QWidget()
        lang_bar.setFixedHeight(36)
        lang_bar.setStyleSheet(
            "background-color: #181825;"
            "border-bottom: 1px solid #313244;"
        )
        lang_layout = QHBoxLayout(lang_bar)
        lang_layout.setContentsMargins(16, 0, 16, 0)
        lang_layout.addStretch()

        lang_sep = QLabel("|")
        lang_sep.setStyleSheet("color: #45475a; font-size: 14px; border: none; background: transparent;")
        lang_layout.addWidget(lang_sep)

        lang_label = QLabel("  " + tr("@lang.label"))
        lang_label.setStyleSheet("color: #a6adc8; font-size: 12px; border: none; background: transparent;")
        lang_label.setObjectName("lang_label")
        lang_layout.addWidget(lang_label)

        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("中文", "zh")
        self.lang_combo.setFixedWidth(100)
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        lang_layout.addWidget(self.lang_combo)
        central_layout.addWidget(lang_bar)

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setContentsMargins(4, 4, 4, 4)
        self.separate_panel = SeparatePanel()
        self.merge_panel = MergePanel()
        self.convert_panel = FormatConvertPanel()
        self.tabs.addTab(self.separate_panel, "  " + tr("@tab.separate") + "  ")
        self.tabs.addTab(self.merge_panel, "  " + tr("@tab.merge") + "  ")
        self.tabs.addTab(self.convert_panel, "  " + tr("@tab.convert") + "  ")
        central_layout.addWidget(self.tabs)

        self.setCentralWidget(central)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(tr("@status.ready"))

        # Connect signals
        self.separate_panel.status_message.connect(self.status_bar.showMessage)
        self.merge_panel.status_message.connect(self.status_bar.showMessage)
        self.convert_panel.status_message.connect(self.status_bar.showMessage)
        i18n.language_changed.connect(self._on_language_changed)

    def _on_lang_changed(self, idx: int):
        lang = self.lang_combo.itemData(idx)
        i18n.set_language(lang)

    def _on_language_changed(self, lang: str):
        self.setWindowTitle(tr("@window.title"))
        self.tabs.setTabText(0, "  " + tr("@tab.separate") + "  ")
        self.tabs.setTabText(1, "  " + tr("@tab.merge") + "  ")
        self.tabs.setTabText(2, "  " + tr("@tab.convert") + "  ")
        self.status_bar.showMessage(tr("@status.ready"))

    def closeEvent(self, event):
        event.accept()
