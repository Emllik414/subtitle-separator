STYLESHEET = """
/* ===== Main Window ===== */
/* ===== Tab Widget ===== */
QTabWidget::pane {
    border: 1px solid #45475a;
    border-top: none;
    background-color: #1e1e2e;
    border-radius: 0 0 10px 10px;
    padding: 4px;
}
QTabBar::tab {
    background-color: #252836;
    color: #a6adc8;
    padding: 12px 32px;
    border: 1px solid #45475a;
    border-bottom: none;
    margin-right: 2px;
    border-radius: 10px 10px 0 0;
    font-size: 14px;
}
QTabBar::tab:selected {
    background-color: #1e1e2e;
    color: #cdd6f4;
    border-bottom: 2px solid #89b4fa;
    font-weight: bold;
}
QTabBar::tab:hover:!selected {
    background-color: #363a4f;
    color: #cdd6f4;
}

/* ===== Labels ===== */
QLabel {
    color: #cdd6f4;
}

/* ===== Buttons ===== */
QPushButton {
    background-color: #89b4fa;
    color: #11111b;
    border: none;
    padding: 10px 26px;
    border-radius: 10px;
    font-weight: bold;
    font-size: 14px;
    min-height: 18px;
}
QPushButton:hover {
    background-color: #b4befe;
}
QPushButton:pressed {
    background-color: #74c7ec;
}
QPushButton:disabled {
    background-color: #45475a;
    color: #6c7086;
}
QPushButton[objectName="secondary_btn"], QPushButton[flat="true"] {
    background-color: transparent;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 10px;
    padding: 9px 22px;
}
QPushButton[objectName="secondary_btn"]:hover, QPushButton[flat="true"]:hover {
    background-color: #363a4f;
    border-color: #585b70;
}

/* ===== Line Edit ===== */
QLineEdit {
    background-color: #252836;
    color: #cdd6f4;
    border: 1px solid #45475a;
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 14px;
}
QLineEdit:focus {
    border: 1px solid #89b4fa;
    background-color: #2a2e3e;
}
QLineEdit:disabled {
    background-color: #1e1e2e;
    color: #6c7086;
}
QLineEdit[readOnly="true"] {
    background-color: #1e2030;
    color: #a6adc8;
    border-style: solid;
}

/* ===== Combo Box ===== */
QComboBox {
    background-color: #252836;
    color: #cdd6f4;
    border: 1px solid #45475a;
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 14px;
    min-width: 80px;
}
QComboBox:hover {
    border: 1px solid #89b4fa;
}
QComboBox:focus {
    border: 1px solid #89b4fa;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #45475a;
    border-radius: 0 6px 6px 0;
}
QComboBox::down-arrow {
    width: 10px;
    height: 10px;
}
QComboBox[enabled="false"] {
    background-color: #1e1e2e;
    color: #6c7086;
}
QComboBox QAbstractItemView {
    background-color: #252836;
    color: #cdd6f4;
    selection-background-color: #45475a;
    selection-color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 4px;
    outline: none;
}
QComboBox QAbstractItemView::item {
    padding: 6px 10px;
    border-radius: 3px;
}
QComboBox QAbstractItemView::item:hover {
    background-color: #363a4f;
}

/* ===== Table Widget ===== */
QTableWidget {
    background-color: #252836;
    color: #cdd6f4;
    border: 1px solid #45475a;
    gridline-color: #363a4f;
    border-radius: 8px;
    font-size: 14px;
    alternate-background-color: #2a2e3e;
}
QTableWidget::item {
    padding: 8px 12px;
    border: none;
}
QTableWidget::item:selected {
    background-color: #45475a;
    color: #cdd6f4;
}
QTableWidget::item:hover:!selected {
    background-color: #313244;
}
QHeaderView::section {
    background-color: #181825;
    color: #89b4fa;
    padding: 10px;
    border: none;
    border-bottom: 2px solid #45475a;
    font-weight: bold;
    font-size: 12px;
    text-transform: uppercase;
}

/* ===== Check Box ===== */
QCheckBox {
    color: #cdd6f4;
    spacing: 8px;
    font-size: 13px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #585b70;
    border-radius: 4px;
    background-color: #252836;
}
QCheckBox::indicator:hover {
    border-color: #89b4fa;
}
QCheckBox::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}
QCheckBox::indicator:checked:hover {
    background-color: #b4befe;
    border-color: #b4befe;
}
QCheckBox::indicator:disabled {
    border-color: #45475a;
    background-color: #313244;
}

/* ===== Radio Button ===== */
QRadioButton {
    color: #cdd6f4;
    spacing: 8px;
    font-size: 13px;
}
QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #585b70;
    border-radius: 10px;
    background-color: #252836;
}
QRadioButton::indicator:hover {
    border-color: #89b4fa;
}
QRadioButton::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}
QRadioButton::indicator:checked:hover {
    background-color: #b4befe;
    border-color: #b4befe;
}

/* ===== Spin Box ===== */
QSpinBox {
    background-color: #252836;
    color: #cdd6f4;
    border: 1px solid #45475a;
    padding: 6px 8px;
    border-radius: 6px;
    font-size: 13px;
}
QSpinBox:focus {
    border: 1px solid #89b4fa;
}
QSpinBox::up-button, QSpinBox::down-button {
    width: 20px;
    border: none;
    background-color: #45475a;
}
QSpinBox::up-button {
    border-radius: 0 6px 0 0;
    margin-left: 1px;
}
QSpinBox::down-button {
    border-radius: 0 0 6px 0;
    margin-left: 1px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #585b70;
}
QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {
    background-color: #6c7086;
}
QSpinBox::up-arrow {
    image: none;
    width: 8px;
    height: 8px;
}
QSpinBox::down-arrow {
    image: none;
    width: 8px;
    height: 8px;
}

/* ===== Group Box ===== */
QGroupBox {
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 10px;
    margin-top: 20px;
    padding: 16px 12px 10px 12px;
    font-weight: bold;
    font-size: 14px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 10px;
    color: #89b4fa;
}

/* ===== Status Bar ===== */
QStatusBar {
    background-color: #181825;
    color: #a6adc8;
    border-top: 1px solid #313244;
    font-size: 13px;
    padding: 4px 14px;
}

/* ===== Scroll Area ===== */
QScrollArea {
    border: none;
    background-color: transparent;
}

/* ===== Scroll Bar ===== */
QScrollBar {
    background-color: #1e1e2e;
}
QAbstractScrollArea::corner {
    background-color: #1e1e2e;
    border: none;
}

/* ===== Scroll Bar: Vertical ===== */
QScrollBar:vertical {
    background-color: #1e1e2e;
    width: 10px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background-color: #45475a;
    border-radius: 4px;
    min-height: 36px;
}
QScrollBar::handle:vertical:hover {
    background-color: #585b70;
}
QScrollBar::handle:vertical:pressed {
    background-color: #6c7086;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
    border: none;
    background: none;
}
QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
    border: none;
    background: none;
    width: 0;
    height: 0;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

/* ===== Scroll Bar: Horizontal ===== */
QScrollBar:horizontal {
    background-color: #1e1e2e;
    height: 10px;
    margin: 0;
}
QScrollBar::handle:horizontal {
    background-color: #45475a;
    border-radius: 4px;
    min-width: 36px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #585b70;
}
QScrollBar::handle:horizontal:pressed {
    background-color: #6c7086;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
    border: none;
    background: none;
}
QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal {
    border: none;
    background: none;
    width: 0;
    height: 0;
}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}

/* ===== Tool Tip ===== */
QToolTip {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    padding: 6px 10px;
    border-radius: 6px;
    font-size: 12px;
}

/* ===== Menu ===== */
QMenu {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px;
}
QMenu::item {
    padding: 6px 28px 6px 12px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #45475a;
}
QMenu::item:disabled {
    color: #6c7086;
}
QMenu::separator {
    height: 1px;
    background-color: #45475a;
    margin: 4px 8px;
}

/* ===== Progress Bar ===== */
QProgressBar {
    background-color: #252836;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 8px;
    text-align: center;
    font-size: 12px;
    height: 20px;
}
QProgressBar::chunk {
    background-color: #89b4fa;
    border-radius: 7px;
}

/* ===== QFrame Cards (used in convert panel) ===== */
QFrame#desc_card, QFrame#settings_card {
    background-color: #252836;
    border: 1px solid #363a4f;
    border-radius: 10px;
}

/* ===== Splitter ===== */
QSplitter::handle {
    background-color: #45475a;
}
QSplitter::handle:horizontal {
    width: 1px;
}
QSplitter::handle:vertical {
    height: 1px;
}

/* ===== Dialog / Message Box ===== */
QMessageBox {
    background-color: #1e1e2e;
    color: #cdd6f4;
}
QMessageBox QLabel {
    color: #cdd6f4;
    font-size: 14px;
}

/* ===== File Dialog ===== */
QFileDialog {
    background-color: #1e1e2e;
    color: #cdd6f4;
}

/* ===== SpinBox ===== */
QSpinBox {
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
}

/* ===== Tool Tip ===== */
QToolTip {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 12px;
}
"""
