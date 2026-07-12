from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QStatusBar, QLabel, QComboBox,
    QHBoxLayout, QVBoxLayout, QWidget, QPushButton,
)
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
        self.resize(1120, 860)
        self.setMinimumSize(980, 760)

        font = QFont("Segoe UI", 10)
        self.setFont(font)

        central = QWidget()
        central.setObjectName("app_root")
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        top_bar = QWidget()
        top_bar.setObjectName("top_bar")
        top_bar.setFixedHeight(64)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(24, 0, 24, 0)
        top_layout.setSpacing(12)

        title_col = QVBoxLayout()
        title_col.setSpacing(1)
        self.app_title = QLabel(tr("@window.title"))
        self.app_title.setObjectName("app_title")
        self.app_subtitle = QLabel("Subtitle Studio")
        self.app_subtitle.setObjectName("app_subtitle")
        title_col.addWidget(self.app_title)
        title_col.addWidget(self.app_subtitle)
        top_layout.addLayout(title_col)
        top_layout.addStretch()

        self.lang_label = QLabel(tr("@lang.label"))
        self.lang_label.setObjectName("lang_label")
        top_layout.addWidget(self.lang_label)

        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("中文", "zh")
        self.lang_combo.setFixedWidth(104)
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        top_layout.addWidget(self.lang_combo)
        root_layout.addWidget(top_bar)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 18, 24, 18)
        content_layout.setSpacing(14)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBar().setExpanding(False)
        self.tabs.tabBar().setDrawBase(False)

        self.separate_panel = SeparatePanel()
        self.merge_panel = MergePanel()
        self.convert_panel = FormatConvertPanel()
        self.tabs.addTab(self.separate_panel, tr("@tab.separate"))
        self.tabs.addTab(self.merge_panel, tr("@tab.merge"))
        self.tabs.addTab(self.convert_panel, tr("@tab.convert"))
        content_layout.addWidget(self.tabs)
        root_layout.addWidget(content)

        self.setCentralWidget(central)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(tr("@status.ready"))

        self.separate_panel.status_message.connect(self.status_bar.showMessage)
        self.merge_panel.status_message.connect(self.status_bar.showMessage)
        self.convert_panel.status_message.connect(self.status_bar.showMessage)
        i18n.language_changed.connect(self._on_language_changed)

        # Existing panels contain legacy local dark styles. Clearing them once lets
        # the shared light theme control the visual system without changing logic.
        for widget in central.findChildren(QWidget):
            if widget.styleSheet():
                widget.setStyleSheet("")

        self.setStyleSheet(STYLESHEET)

    def _on_lang_changed(self, idx: int):
        lang = self.lang_combo.itemData(idx)
        i18n.set_language(lang)

    def _on_language_changed(self, lang: str):
        self.setWindowTitle(tr("@window.title"))
        self.app_title.setText(tr("@window.title"))
        self.lang_label.setText(tr("@lang.label"))
        self.tabs.setTabText(0, tr("@tab.separate"))
        self.tabs.setTabText(1, tr("@tab.merge"))
        self.tabs.setTabText(2, tr("@tab.convert"))
        self.status_bar.showMessage(tr("@status.ready"))

    def closeEvent(self, event):
        event.accept()
