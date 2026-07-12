STYLESHEET = r"""
* {
    font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
    color: #1d1d1f;
}
QWidget { background: transparent; }
QToolTip {
    background: #2c2c2e;
    color: white;
    border: none;
    border-radius: 7px;
    padding: 6px 9px;
    font-size: 11px;
}
QFrame#app_shell {
    background: #f5f5f7;
    border: 1px solid rgba(0, 0, 0, 24);
    border-radius: 28px;
}
QFrame#app_shell[maximized="true"] { border-radius: 0; }
QFrame#title_bar {
    background: rgba(255, 255, 255, 235);
    border: none;
    border-bottom: 1px solid #e6e6e9;
    border-top-left-radius: 28px;
    border-top-right-radius: 28px;
}
QFrame#title_bar[maximized="true"] { border-top-left-radius: 0; border-top-right-radius: 0; }
QLabel#window_title {
    color: #3a3a3c;
    font-size: 13px;
    font-weight: 650;
}
QPushButton#traffic_red, QPushButton#traffic_yellow, QPushButton#traffic_green {
    border: none;
    border-radius: 6px;
    min-width: 12px;
    max-width: 12px;
    min-height: 12px;
    max-height: 12px;
    padding: 0;
}
QPushButton#traffic_red { background: #ff5f57; }
QPushButton#traffic_yellow { background: #febc2e; }
QPushButton#traffic_green { background: #28c840; }
QPushButton#traffic_red:hover { background: #ff453a; }
QPushButton#traffic_yellow:hover { background: #ffb000; }
QPushButton#traffic_green:hover { background: #20b83a; }
QPushButton#help_button {
    background: #ffffff;
    border: 1px solid #e1e1e5;
    border-radius: 10px;
    min-width: 32px;
    max-width: 32px;
    min-height: 32px;
    max-height: 32px;
    color: #55555b;
    font-size: 14px;
    padding: 0;
}
QPushButton#help_button:hover { background: #f6f6f8; border-color: #d2d2d7; }
QComboBox#language_combo {
    background: #ffffff;
    border: 1px solid #e1e1e5;
    border-radius: 10px;
    min-height: 30px;
    padding: 0 28px 0 10px;
    color: #55555b;
    font-size: 12px;
    font-weight: 650;
}
QComboBox#language_combo::drop-down { border: none; width: 22px; }
QComboBox#language_combo QAbstractItemView {
    background: #ffffff;
    border: 1px solid #dedee3;
    border-radius: 9px;
    padding: 4px;
    selection-background-color: #eaf3ff;
    selection-color: #007aff;
}
QFrame#header { background: transparent; border: none; }
QLabel#eyebrow {
    color: #007aff;
    font-size: 11px;
    font-weight: 750;
    letter-spacing: 1px;
}
QLabel#page_title {
    color: #1d1d1f;
    font-size: 28px;
    font-weight: 750;
}
QLabel#page_description { color: #6e6e73; font-size: 13px; }
QFrame#segmented_control {
    background: #e9e9ed;
    border: 1px solid #e1e1e5;
    border-radius: 13px;
}
QPushButton[segment="true"] {
    background: transparent;
    color: #66666c;
    border: none;
    border-radius: 10px;
    padding: 0 18px;
    font-size: 13px;
    font-weight: 650;
}
QPushButton[segment="true"]:checked {
    background: #ffffff;
    color: #1d1d1f;
    border: 1px solid #dddde2;
}
QPushButton[segment="true"]:hover:!checked { background: rgba(255,255,255,110); }
QFrame#card {
    background: #ffffff;
    border: 1px solid #e5e5e9;
    border-radius: 18px;
}
QLabel#card_title { color: #1d1d1f; font-size: 14px; font-weight: 720; }
QLabel#card_subtitle { color: #6e6e73; font-size: 12px; }
QLabel#format_hint { color: #99999f; font-size: 10px; font-weight: 650; }
QFrame#drop_zone {
    background: #fafafd;
    border: 2px dashed #cfd0d5;
    border-radius: 16px;
}
QFrame#drop_zone[state="hover"] {
    background: #f6faff;
    border-color: #007aff;
}
QFrame#drop_zone[state="loaded"] {
    background: #f8fbff;
    border-color: #bcdcff;
}
QLabel#file_icon {
    background: #ffffff;
    color: #007aff;
    border: 1px solid #dedee3;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 800;
}
QLabel#file_icon[compact="true"] { border-radius: 9px; font-size: 9px; }
QLabel#drop_main { color: #1d1d1f; font-size: 13px; font-weight: 700; }
QLabel#drop_hint { color: #9a9aa1; font-size: 10px; }
QPushButton#mini_button {
    background: #eaf3ff;
    color: #007aff;
    border: none;
    border-radius: 10px;
    padding: 7px 12px;
    font-size: 11px;
    font-weight: 700;
    margin-top: 5px;
}
QPushButton#mini_button:hover { background: #dcecff; }
QFrame#file_summary {
    background: #f8f8fa;
    border: 1px solid #ededf0;
    border-radius: 12px;
}
QLabel#file_check {
    background: #eaf8ee;
    color: #28a745;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 800;
}
QLabel#file_name { color: #303034; font-size: 11px; font-weight: 700; }
QLabel#file_meta { color: #77777d; font-size: 10px; }
QPushButton#more_button {
    border: none;
    background: transparent;
    color: #a0a0a5;
    font-size: 14px;
    padding: 0;
}
QPushButton#more_button:hover { color: #007aff; background: #edf5ff; border-radius: 8px; }
QFrame#divider { background: #eeeef1; border: none; min-height: 1px; max-height: 1px; }
QLabel#small_label { color: #6e6e73; font-size: 10px; font-weight: 650; }
QPushButton#language_chip {
    background: #eaf3ff;
    color: #007aff;
    border: 1px solid #cfe4ff;
    border-radius: 10px;
    padding: 7px 10px;
    font-size: 10px;
    font-weight: 700;
}
QPushButton#language_chip:disabled { color: #007aff; background: #eaf3ff; }
QPushButton#language_chip:hover:enabled { background: #dcecff; }
QComboBox#compact_combo, QComboBox#format_combo {
    background: #ffffff;
    color: #333337;
    border: 1px solid #dedee3;
    border-radius: 11px;
    min-height: 34px;
    padding: 0 30px 0 11px;
    font-size: 11px;
    font-weight: 650;
}
QComboBox#compact_combo:hover, QComboBox#format_combo:hover { border-color: #9cc8ff; }
QComboBox#compact_combo::drop-down, QComboBox#format_combo::drop-down { border: none; width: 24px; }
QComboBox#compact_combo QAbstractItemView, QComboBox#format_combo QAbstractItemView {
    background: #ffffff;
    color: #333337;
    border: 1px solid #dedee3;
    selection-background-color: #eaf3ff;
    selection-color: #007aff;
    outline: none;
}
QFrame#preview_header { background: #ffffff; border: none; border-bottom: 1px solid #ececf0; }
QLabel#preview_title { color: #1d1d1f; font-size: 14px; font-weight: 720; }
QLabel#preview_meta { color: #6e6e73; font-size: 10px; }
QLabel#status_pill {
    border: none;
    border-radius: 12px;
    padding: 6px 10px;
    font-size: 10px;
    font-weight: 750;
}
QLabel#status_pill[tone="success"] { background: #eaf8ee; color: #187b35; }
QLabel#status_pill[tone="warning"] { background: #fff7e8; color: #a86100; }
QLabel#status_pill[tone="neutral"] { background: #f1f2f4; color: #67676d; }
QLabel#status_pill[tone="danger"] { background: #fff0f0; color: #c54249; }
QTableWidget#preview_table {
    background: #ffffff;
    alternate-background-color: #ffffff;
    border: none;
    gridline-color: transparent;
    selection-background-color: #edf5ff;
    selection-color: #1d1d1f;
    font-size: 11px;
}
QTableWidget#preview_table::item {
    border: none;
    border-bottom: 1px solid #eeeef1;
    padding: 7px 11px;
}
QTableWidget#preview_table::item:hover { background: #fbfdff; }
QHeaderView::section {
    background: #f8f8fa;
    color: #74747b;
    border: none;
    border-bottom: 1px solid #e7e7eb;
    padding: 9px 11px;
    font-size: 9px;
    font-weight: 700;
}
QScrollBar:vertical { width: 10px; background: transparent; margin: 2px; }
QScrollBar::handle:vertical { background: #d2d2d7; border-radius: 4px; min-height: 35px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { height: 10px; background: transparent; margin: 2px; }
QScrollBar::handle:horizontal { background: #d2d2d7; border-radius: 4px; min-width: 35px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QLineEdit#path_field {
    background: #f7f7f9;
    color: #65656b;
    border: 1px solid #e3e3e7;
    border-radius: 10px;
    min-height: 32px;
    padding: 0 10px;
    font-size: 10px;
}
QLineEdit#path_field:focus { border-color: #9cc8ff; background: #ffffff; }
QPushButton#primary_button {
    background: #007aff;
    color: #ffffff;
    border: none;
    border-radius: 12px;
    min-height: 42px;
    padding: 0 19px;
    font-size: 12px;
    font-weight: 750;
}
QPushButton#primary_button:hover { background: #0066d6; }
QPushButton#primary_button:pressed { background: #005fc7; }
QPushButton#primary_button:disabled { background: #dfe0e5; color: #9b9ba1; }
QPushButton#secondary_button {
    background: #ffffff;
    color: #44444a;
    border: 1px solid #dedee3;
    border-radius: 11px;
    min-height: 38px;
    padding: 0 15px;
    font-size: 11px;
    font-weight: 700;
}
QPushButton#secondary_button:hover { background: #f7f7f9; border-color: #c8c8cd; }
QPushButton#secondary_button:disabled { color: #aaaab0; background: #f5f5f7; }
QPushButton#danger_button {
    background: #fff7f7;
    color: #c54249;
    border: 1px solid #f0d6d8;
    border-radius: 11px;
    min-height: 38px;
    padding: 0 15px;
    font-size: 11px;
    font-weight: 700;
}
QPushButton#danger_button:hover { background: #fff0f0; }
QFrame#setting_box {
    background: #f8f8fa;
    border: 1px solid #ececf0;
    border-radius: 13px;
}
QLabel#setting_label { color: #6e6e73; font-size: 10px; font-weight: 650; }
QPushButton[pill="true"] {
    background: #ffffff;
    color: #55555b;
    border: 1px solid #e3e3e7;
    border-radius: 8px;
    padding: 6px 8px;
    font-size: 9px;
}
QPushButton[pill="true"]:checked {
    border-color: #a9d0ff;
    background: #edf5ff;
    color: #0671e8;
    font-weight: 700;
}
QPushButton[pill="true"]:hover:!checked { background: #f2f2f5; }
QSpinBox#compact_spin {
    background: #ffffff;
    color: #333337;
    border: 1px solid #dedee3;
    border-radius: 8px;
    min-height: 27px;
    padding: 0 6px;
    font-size: 10px;
}
QFrame#hero_card { background: #f7fbff; border: 1px solid #dfeeff; border-radius: 18px; }
QLabel#hero_title { color: #1d1d1f; font-size: 22px; font-weight: 760; }
QLabel#hero_description { color: #6e6e73; font-size: 11px; }
QLabel#format_tag {
    background: #ffffff;
    color: #333337;
    border: 1px solid #dddde2;
    border-radius: 12px;
    min-width: 72px;
    min-height: 42px;
    font-size: 11px;
    font-weight: 800;
}
QLabel#format_tag[target="true"] { background: #f3f8ff; color: #007aff; border-color: #bcdcff; }
QLabel#format_arrow { color: #8e8e93; font-size: 18px; }
QFrame#settings_row { border: none; border-bottom: 1px solid #ededf0; }
QLabel#settings_key { color: #303034; font-size: 11px; font-weight: 650; }
QLabel#settings_value { color: #6e6e73; font-size: 10px; }
QFrame#footer {
    background: rgba(255, 255, 255, 180);
    border: none;
    border-top: 1px solid #e7e7ea;
    border-bottom-left-radius: 28px;
    border-bottom-right-radius: 28px;
}
QLabel#footer_dot { background: #35b653; border-radius: 3px; min-width: 6px; max-width: 6px; min-height: 6px; max-height: 6px; }
QLabel#footer_text, QLabel#footer_note { color: #818188; font-size: 9px; }
QMessageBox { background: #f5f5f7; }
QMessageBox QLabel { color: #1d1d1f; }
"""
