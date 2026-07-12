"""Apple-inspired light QSS for the subtitle tool."""

STYLESHEET = r"""
QMainWindow,
QWidget#appRoot {
    background: #f5f5f7;
    color: #1d1d1f;
}

QWidget {
    color: #1d1d1f;
    font-size: 13px;
}

QFrame#topBar {
    background: #ffffff;
    border: none;
    border-bottom: 1px solid #e5e5e8;
}

QFrame#headerBar {
    background: #f5f5f7;
    border: none;
}

QFrame#appMark {
    background: #007aff;
    border-radius: 8px;
}

QLabel#topTitle {
    color: #3a3a3c;
    font-size: 13px;
    font-weight: 700;
}

QLabel#eyebrow {
    color: #007aff;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1px;
}

QLabel#pageTitle {
    color: #1d1d1f;
    font-size: 27px;
    font-weight: 800;
}

QLabel#pageDescription,
QLabel#mutedText,
QLabel#metaText {
    color: #6e6e73;
}

QLabel#pageDescription {
    font-size: 13px;
}

QLabel#sectionTitle {
    color: #1d1d1f;
    font-size: 14px;
    font-weight: 750;
}

QLabel#sectionSubtitle {
    color: #6e6e73;
    font-size: 11px;
}

QLabel#fieldLabel {
    color: #6e6e73;
    font-size: 10px;
    font-weight: 700;
}

QLabel#chip {
    background: #eaf3ff;
    color: #007aff;
    border: 1px solid #cfe4ff;
    border-radius: 9px;
    padding: 6px 9px;
    font-size: 11px;
    font-weight: 700;
}

QLabel#pill {
    background: #eaf8ee;
    color: #187b35;
    border: none;
    border-radius: 10px;
    padding: 5px 9px;
    font-size: 10px;
    font-weight: 750;
}

QLabel#pill[tone="warning"] {
    background: #fff7e8;
    color: #a86100;
}

QLabel#pill[tone="error"] {
    background: #fff0f1;
    color: #c33f48;
}

QLabel[tone="success"] { color: #21843f; }
QLabel[tone="warning"] { color: #b56b00; }
QLabel[tone="error"] { color: #c33f48; }
QLabel[tone="muted"] { color: #8e8e93; }

QFrame#card {
    background: #ffffff;
    border: 1px solid #e5e5e9;
    border-radius: 18px;
}

QFrame#settingBox {
    background: #f8f8fa;
    border: 1px solid #ececf0;
    border-radius: 13px;
}

QFrame#segmentedNav {
    background: #e9e9ed;
    border: 1px solid #e1e1e5;
    border-radius: 13px;
}

QPushButton#navButton {
    min-width: 96px;
    min-height: 32px;
    padding: 0 15px;
    color: #66666c;
    background: transparent;
    border: none;
    border-radius: 10px;
    font-size: 12px;
    font-weight: 700;
}

QPushButton#navButton:hover:!checked {
    background: rgba(255, 255, 255, 0.45);
    color: #333338;
}

QPushButton#navButton:checked {
    background: #ffffff;
    color: #1d1d1f;
    border: 1px solid #dddddf;
}

QPushButton {
    min-height: 38px;
    padding: 0 18px;
    color: #ffffff;
    background: #007aff;
    border: none;
    border-radius: 11px;
    font-size: 12px;
    font-weight: 750;
}

QPushButton:hover { background: #006edc; }
QPushButton:pressed { background: #005fc1; }
QPushButton:disabled {
    background: #d7d7dc;
    color: #9a9aa1;
}

QPushButton#primaryButton {
    min-height: 42px;
    padding: 0 20px;
    border-radius: 12px;
    font-size: 13px;
}

QPushButton#secondaryButton,
QPushButton#iconButton,
QPushButton#topButton {
    color: #44444a;
    background: #ffffff;
    border: 1px solid #dedee3;
}

QPushButton#secondaryButton:hover,
QPushButton#iconButton:hover,
QPushButton#topButton:hover {
    color: #1d1d1f;
    background: #f7f7f9;
    border-color: #cfcfd5;
}

QPushButton#dangerButton {
    color: #c54249;
    background: #fff7f7;
    border: 1px solid #f0d6d8;
}

QPushButton#dangerButton:hover {
    background: #ffeded;
    border-color: #e8bfc2;
}

QPushButton#miniButton {
    min-height: 30px;
    padding: 0 12px;
    color: #007aff;
    background: #eaf3ff;
    border: none;
    border-radius: 9px;
    font-size: 11px;
    font-weight: 750;
}

QPushButton#miniButton:hover { background: #dcecff; }

QPushButton#iconButton,
QPushButton#topButton {
    min-width: 34px;
    max-width: 34px;
    padding: 0;
}

QFrame#dropCard {
    background: #fafafd;
    border: 2px dashed #cfd0d5;
    border-radius: 16px;
}

QFrame#dropCard[state="hover"] {
    background: #f5f9ff;
    border-color: #007aff;
}

QFrame#dropCard[state="loaded"] {
    background: #fbfdff;
    border: 1px solid #cfe4ff;
}

QLabel#fileIcon {
    min-width: 48px;
    max-width: 48px;
    min-height: 52px;
    max-height: 52px;
    color: #007aff;
    background: #ffffff;
    border: 1px solid #dedee3;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 800;
}

QLabel#dropMain {
    color: #252529;
    font-size: 13px;
    font-weight: 750;
}

QLabel#dropHint {
    color: #9a9aa1;
    font-size: 10px;
}

QFrame#fileSummary {
    background: #f8f8fa;
    border: 1px solid #ededf0;
    border-radius: 12px;
}

QLabel#fileCheck {
    min-width: 26px;
    max-width: 26px;
    min-height: 26px;
    max-height: 26px;
    color: #21843f;
    background: #eaf8ee;
    border-radius: 8px;
    font-weight: 800;
}

QLineEdit,
QComboBox,
QSpinBox {
    min-height: 36px;
    color: #333338;
    background: #ffffff;
    border: 1px solid #dedee3;
    border-radius: 10px;
    padding: 0 11px;
    selection-background-color: #cfe4ff;
}

QLineEdit:hover,
QComboBox:hover,
QSpinBox:hover { border-color: #c1c1c7; }

QLineEdit:focus,
QComboBox:focus,
QSpinBox:focus { border-color: #007aff; }

QLineEdit:read-only {
    color: #65656b;
    background: #f7f7f9;
    border-color: #e3e3e7;
}

QLineEdit:disabled,
QComboBox:disabled,
QSpinBox:disabled {
    color: #9a9aa1;
    background: #f1f1f3;
}

QComboBox::drop-down {
    width: 28px;
    border: none;
}

QComboBox QAbstractItemView {
    color: #1d1d1f;
    background: #ffffff;
    border: 1px solid #dedee3;
    border-radius: 9px;
    selection-color: #1d1d1f;
    selection-background-color: #eaf3ff;
    outline: 0;
    padding: 4px;
}

QRadioButton {
    color: #55555b;
    background: #ffffff;
    border: 1px solid #e3e3e7;
    border-radius: 8px;
    padding: 6px 8px;
    spacing: 0;
    font-size: 10px;
}

QRadioButton:hover {
    border-color: #b7d8ff;
    background: #f7fbff;
}

QRadioButton:checked {
    color: #0671e8;
    background: #edf5ff;
    border-color: #a9d0ff;
    font-weight: 750;
}

QRadioButton::indicator {
    width: 0;
    height: 0;
}

QTableWidget {
    color: #3a3a3f;
    background: #ffffff;
    alternate-background-color: #fcfcfd;
    border: none;
    gridline-color: transparent;
    outline: 0;
    font-size: 11px;
}

QTableWidget::item {
    padding: 9px 11px;
    border-bottom: 1px solid #eeeef1;
}

QTableWidget::item:hover { background: #fbfdff; }
QTableWidget::item:selected {
    color: #1d1d1f;
    background: #eaf3ff;
}

QHeaderView::section {
    color: #74747b;
    background: #f8f8fa;
    border: none;
    border-bottom: 1px solid #e7e7eb;
    padding: 9px 11px;
    font-size: 10px;
    font-weight: 750;
}

QScrollBar:vertical {
    width: 9px;
    margin: 3px;
    background: transparent;
}

QScrollBar::handle:vertical {
    min-height: 34px;
    background: #c8c8ce;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover { background: #aaaab1; }
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical { height: 0; background: transparent; }

QScrollBar:horizontal {
    height: 9px;
    margin: 3px;
    background: transparent;
}

QScrollBar::handle:horizontal {
    min-width: 34px;
    background: #c8c8ce;
    border-radius: 4px;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal { width: 0; background: transparent; }

QStatusBar {
    min-height: 28px;
    color: #818188;
    background: rgba(255, 255, 255, 0.92);
    border-top: 1px solid #e5e5e8;
    font-size: 10px;
    padding: 0 14px;
}

QToolTip {
    color: #ffffff;
    background: #2c2c2e;
    border: none;
    border-radius: 7px;
    padding: 6px 9px;
    font-size: 11px;
}

QMessageBox {
    background: #f5f5f7;
}
"""
