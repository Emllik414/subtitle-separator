from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from gui.convert_panel import FormatConvertPanel
from gui.i18n import i18n, tr
from gui.merge_panel import MergePanel
from gui.separate_panel import SeparatePanel
from gui.styles import STYLESHEET


class MainWindow(QMainWindow):
    PAGE_KEYS = (
        ("@page.separate.title", "@page.separate.desc"),
        ("@page.merge.title", "@page.merge.desc"),
        ("@page.convert.title", "@page.convert.desc"),
    )

    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("@window.title"))
        self.resize(1180, 860)
        self.setMinimumSize(1000, 740)
        self.setStyleSheet(STYLESHEET)

        central = QWidget()
        central.setObjectName("appRoot")
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        # Compact app toolbar
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_bar.setFixedHeight(54)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(18, 0, 18, 0)
        top_layout.setSpacing(10)

        app_mark = QFrame()
        app_mark.setObjectName("appMark")
        app_mark.setFixedSize(16, 16)
        top_layout.addWidget(app_mark)

        self.top_title = QLabel(tr("@app.name"))
        self.top_title.setObjectName("topTitle")
        top_layout.addWidget(self.top_title)
        top_layout.addStretch()

        self.help_btn = QPushButton("?")
        self.help_btn.setObjectName("topButton")
        self.help_btn.setToolTip(tr("@app.help"))
        self.help_btn.clicked.connect(self._show_help)
        top_layout.addWidget(self.help_btn)

        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("中文", "zh")
        self.lang_combo.setFixedWidth(104)
        self.lang_combo.setCurrentIndex(1 if i18n.current_lang == "zh" else 0)
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        top_layout.addWidget(self.lang_combo)
        central_layout.addWidget(top_bar)

        # Page header and segmented navigation
        header = QFrame()
        header.setObjectName("headerBar")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 20, 30, 18)
        header_layout.setSpacing(20)

        title_col = QVBoxLayout()
        title_col.setSpacing(3)
        self.eyebrow = QLabel(tr("@app.eyebrow"))
        self.eyebrow.setObjectName("eyebrow")
        self.page_title = QLabel()
        self.page_title.setObjectName("pageTitle")
        self.page_description = QLabel()
        self.page_description.setObjectName("pageDescription")
        self.page_description.setWordWrap(True)
        title_col.addWidget(self.eyebrow)
        title_col.addWidget(self.page_title)
        title_col.addWidget(self.page_description)
        header_layout.addLayout(title_col, 1)

        segmented = QFrame()
        segmented.setObjectName("segmentedNav")
        segmented_layout = QHBoxLayout(segmented)
        segmented_layout.setContentsMargins(4, 4, 4, 4)
        segmented_layout.setSpacing(3)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self.nav_buttons: list[QPushButton] = []
        for index, key in enumerate(("@tab.separate", "@tab.merge", "@tab.convert")):
            button = QPushButton(tr(key))
            button.setObjectName("navButton")
            button.setCheckable(True)
            self.nav_group.addButton(button, index)
            self.nav_buttons.append(button)
            segmented_layout.addWidget(button)
        self.nav_buttons[0].setChecked(True)
        self.nav_group.idClicked.connect(self._on_nav_clicked)
        header_layout.addWidget(segmented, 0, Qt.AlignBottom)
        central_layout.addWidget(header)

        # Functional pages
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 0, 30, 24)
        content_layout.setSpacing(0)

        self.stack = QStackedWidget()
        self.separate_panel = SeparatePanel()
        self.merge_panel = MergePanel()
        self.convert_panel = FormatConvertPanel()
        self.stack.addWidget(self.separate_panel)
        self.stack.addWidget(self.merge_panel)
        self.stack.addWidget(self.convert_panel)
        content_layout.addWidget(self.stack)
        central_layout.addWidget(content, 1)
        self.setCentralWidget(central)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(tr("@status.ready"))

        self.separate_panel.status_message.connect(self.status_bar.showMessage)
        self.merge_panel.status_message.connect(self.status_bar.showMessage)
        self.convert_panel.status_message.connect(self.status_bar.showMessage)
        i18n.language_changed.connect(self._on_language_changed)

        self._refresh_page_copy()

    def _on_nav_clicked(self, index: int):
        self.stack.setCurrentIndex(index)
        self._refresh_page_copy()
        self.status_bar.showMessage(tr("@status.ready"))

    def _refresh_page_copy(self):
        index = self.stack.currentIndex()
        title_key, desc_key = self.PAGE_KEYS[index]
        self.page_title.setText(tr(title_key))
        self.page_description.setText(tr(desc_key))

    def _on_lang_changed(self, index: int):
        language = self.lang_combo.itemData(index)
        if language and language != i18n.current_lang:
            i18n.set_language(language)

    def _on_language_changed(self, language: str):
        self.setWindowTitle(tr("@window.title"))
        self.top_title.setText(tr("@app.name"))
        self.eyebrow.setText(tr("@app.eyebrow"))
        self.help_btn.setToolTip(tr("@app.help"))
        self.nav_buttons[0].setText(tr("@tab.separate"))
        self.nav_buttons[1].setText(tr("@tab.merge"))
        self.nav_buttons[2].setText(tr("@tab.convert"))
        self._refresh_page_copy()
        self.status_bar.showMessage(tr("@status.ready"))

        expected = 1 if language == "zh" else 0
        if self.lang_combo.currentIndex() != expected:
            self.lang_combo.blockSignals(True)
            self.lang_combo.setCurrentIndex(expected)
            self.lang_combo.blockSignals(False)

    def _show_help(self):
        QMessageBox.information(
            self,
            tr("@app.help_title"),
            tr("@app.help_body"),
        )

    def closeEvent(self, event):
        event.accept()
