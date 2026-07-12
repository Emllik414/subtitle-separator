STYLESHEET = r"""
/* ===== Application shell ===== */
QMainWindow, QWidget#app_root {
    background: #F5F5F7;
    color: #1D1D1F;
}
QWidget {
    color: #1D1D1F;
    font-family: "SF Pro Display", "Segoe UI", "Microsoft YaHei UI", sans-serif;
    font-size: 13px;
}
QWidget#top_bar {
    background: rgba(255, 255, 255, 0.96);
    border-bottom: 1px solid #E7E7EA;
}
QLabel#app_title {
    color: #1D1D1F;
    font-size: 17px;
    font-weight: 650;
}
QLabel#app_subtitle, QLabel#lang_label {
    color: #86868B;
    font-size: 12px;
}

/* ===== Segmented tabs ===== */
QTabWidget::pane {
    background: transparent;
    border: none;
    padding: 0;
}
QTabBar {
    background: transparent;
}
QTabBar::tab {
    min-width: 116px;
    min-height: 34px;
    padding: 2px 18px;
    margin: 0;
    color: #6E6E73;
    background: #ECECF0;
    border: none;
    border-right: 1px solid #D9D9DE;
    font-weight: 550;
}
QTabBar::tab:first {
    border-radius: 10px 0 0 10px;
}
QTabBar::tab:last {
    border-radius: 0 10px 10px 0;
    border-right: none;
}
QTabBar::tab:only-one {
    border-radius: 10px;
}
QTabBar::tab:selected {
    color: #1D1D1F;
    background: #FFFFFF;
    font-weight: 650;
}
QTabBar::tab:hover:!selected {
    background: #E4E4E9;
    color: #1D1D1F;
}

/* ===== Cards and groups ===== */
QGroupBox, QFrame#desc_card, QFrame#settings_card {
    background: #FFFFFF;
    border: 1px solid #E5E5EA;
    border-radius: 16px;
    margin-top: 14px;
    padding: 18px 16px 14px 16px;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 16px;
    padding: 0 8px;
    color: #1D1D1F;
    background: #F5F5F7;
    font-size: 13px;
    font-weight: 650;
}
QFrame#desc_card QLabel, QFrame#settings_card QLabel {
    background: transparent;
    border: none;
}

/* ===== Labels ===== */
QLabel {
    color: #3A3A3C;
    background: transparent;
}
QLabel[role="muted"] {
    color: #86868B;
}
QLabel[role="success"] {
    color: #248A3D;
}
QLabel[role="danger"] {
    color: #D70015;
}

/* ===== Buttons ===== */
QPushButton {
    min-height: 20px;
    padding: 9px 20px;
    color: #FFFFFF;
    background: #007AFF;
    border: 1px solid #007AFF;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 650;
}
QPushButton:hover {
    background: #1687FF;
    border-color: #1687FF;
}
QPushButton:pressed {
    background: #0068D9;
    border-color: #0068D9;
}
QPushButton:disabled {
    color: #A8A8AD;
    background: #E9E9ED;
    border-color: #E9E9ED;
}
QPushButton[objectName="secondary_btn"], QPushButton[flat="true"], QPushButton[role="secondary"] {
    color: #1D1D1F;
    background: #FFFFFF;
    border: 1px solid #D2D2D7;
}
QPushButton[objectName="secondary_btn"]:hover, QPushButton[flat="true"]:hover, QPushButton[role="secondary"]:hover {
    background: #F2F2F7;
    border-color: #C7C7CC;
}
QPushButton[role="danger"] {
    color: #D70015;
    background: #FFFFFF;
    border: 1px solid #E5E5EA;
}
QPushButton[role="danger"]:hover {
    background: #FFF1F2;
    border-color: #FFD0D5;
}

/* ===== Inputs ===== */
QLineEdit, QComboBox, QSpinBox {
    min-height: 20px;
    padding: 8px 12px;
    color: #1D1D1F;
    background: #FFFFFF;
    border: 1px solid #D2D2D7;
    border-radius: 9px;
    selection-background-color: #B7D8FF;
}
QLineEdit:hover, QComboBox:hover, QSpinBox:hover {
    border-color: #B7B7BC;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 2px solid #007AFF;
    padding: 7px 11px;
}
QLineEdit:read-only {
    color: #6E6E73;
    background: #F9F9FB;
}
QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled {
    color: #A1A1A6;
    background: #F2F2F7;
    border-color: #E5E5EA;
}
QComboBox::drop-down {
    width: 26px;
    border: none;
}
QComboBox QAbstractItemView {
    color: #1D1D1F;
    background: #FFFFFF;
    border: 1px solid #D2D2D7;
    border-radius: 10px;
    padding: 5px;
    outline: none;
    selection-color: #1D1D1F;
    selection-background-color: #EAF3FF;
}
QComboBox QAbstractItemView::item {
    min-height: 30px;
    padding: 4px 10px;
    border-radius: 7px;
}

/* ===== Drop zone ===== */
QFrame#drop_card {
    background: #FBFBFD;
    border: 1.5px dashed #C7C7CC;
    border-radius: 16px;
}
QFrame#drop_card[dropState="hover"] {
    background: #F2F8FF;
    border: 1.5px dashed #007AFF;
}
QFrame#drop_card[dropState="loaded"] {
    background: #F4FBF6;
    border: 1.5px solid #B7E5C2;
}
QLabel#drop_icon {
    color: #007AFF;
    font-size: 25px;
    font-weight: 400;
}
QLabel#drop_label {
    color: #1D1D1F;
    font-size: 14px;
    font-weight: 600;
}
QLabel#drop_hint {
    color: #86868B;
    font-size: 11px;
}

/* ===== Preview table ===== */
QTableWidget {
    color: #1D1D1F;
    background: #FFFFFF;
    alternate-background-color: #FAFAFC;
    border: 1px solid #E5E5EA;
    border-radius: 14px;
    gridline-color: #EFEFF2;
    outline: none;
}
QTableWidget::item {
    min-height: 34px;
    padding: 7px 10px;
    border: none;
}
QTableWidget::item:hover:!selected {
    background: #F2F7FF;
}
QTableWidget::item:selected {
    color: #1D1D1F;
    background: #DDEEFF;
}
QHeaderView::section {
    color: #6E6E73;
    background: #F7F7F9;
    padding: 10px;
    border: none;
    border-bottom: 1px solid #E5E5EA;
    font-size: 11px;
    font-weight: 650;
}

/* ===== Selection controls ===== */
QCheckBox, QRadioButton {
    spacing: 8px;
    color: #3A3A3C;
}
QCheckBox::indicator, QRadioButton::indicator {
    width: 17px;
    height: 17px;
    background: #FFFFFF;
    border: 1.5px solid #C7C7CC;
}
QCheckBox::indicator {
    border-radius: 5px;
}
QRadioButton::indicator {
    border-radius: 9px;
}
QCheckBox::indicator:hover, QRadioButton::indicator:hover {
    border-color: #007AFF;
}
QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    background: #007AFF;
    border-color: #007AFF;
}

/* ===== Status bar, menus, tooltips ===== */
QStatusBar {
    color: #86868B;
    background: #FFFFFF;
    border-top: 1px solid #E5E5EA;
    padding: 4px 14px;
    font-size: 12px;
}
QMenu, QToolTip {
    color: #1D1D1F;
    background: #FFFFFF;
    border: 1px solid #D2D2D7;
    border-radius: 10px;
    padding: 6px;
}
QMenu::item {
    padding: 7px 24px 7px 10px;
    border-radius: 7px;
}
QMenu::item:selected {
    background: #EAF3FF;
}

/* ===== Scroll bars ===== */
QScrollBar:vertical {
    width: 10px;
    margin: 2px;
    background: transparent;
}
QScrollBar:horizontal {
    height: 10px;
    margin: 2px;
    background: transparent;
}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    min-height: 34px;
    min-width: 34px;
    background: #C7C7CC;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
    background: #AEAEB2;
}
QScrollBar::add-line, QScrollBar::sub-line,
QScrollBar::add-page, QScrollBar::sub-page {
    width: 0;
    height: 0;
    background: transparent;
    border: none;
}
QAbstractScrollArea::corner {
    background: transparent;
}
"""
