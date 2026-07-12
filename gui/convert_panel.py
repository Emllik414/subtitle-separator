"""Format Convert Panel ? third tab of the main window.

Allows the user to convert subtitle files between SRT, ASS, SSA, and VTT
formats. Reuses existing parser infrastructure and DropZone widget.
"""

import os
import subprocess
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QFileDialog, QFrame,
)
from PySide6.QtCore import Qt, Signal

from gui.drop_zone import DropZone
from gui.i18n import i18n, tr
from models.enums import SubtitleFormat
from parsers.base import detect_format, get_parser
from logic.converter import convert_subtitle
from utils.text import read_subtitle_file


class FormatConvertPanel(QWidget):
    status_message = Signal(str)

    def __init__(self):
        super().__init__()
        self._source_format = None
        self._source_path = ""
        self._entry_count = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Description card
        desc_card = QFrame()
        desc_card.setObjectName("desc_card")
        desc_card.setStyleSheet(
            "QFrame#desc_card {"
            "  background-color: #252836;"
            "  border: 1px solid #363a4f;"
            "  border-radius: 10px;"
            "  padding: 14px 18px;"
            "}"
        )
        desc_layout = QVBoxLayout(desc_card)
        desc_layout.setContentsMargins(18, 14, 18, 14)
        desc_layout.setSpacing(4)

        self.title_label = QLabel(tr("@convert.title"))
        self.title_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #cdd6f4;"
            "background: transparent; border: none;"
        )
        desc_layout.addWidget(self.title_label)

        self.desc_label = QLabel(tr("@convert.description"))
        self.desc_label.setStyleSheet(
            "font-size: 13px; color: #6c7086;"
            "background: transparent; border: none;"
        )
        desc_layout.addWidget(self.desc_label)

        layout.addWidget(desc_card)

        # Drop zone
        self.drop_zone = DropZone("@convert.drop_label")
        self.drop_zone.file_changed.connect(self._on_file_loaded)
        layout.addWidget(self.drop_zone)

        # Source format info
        info_row = QHBoxLayout()
        info_row.setSpacing(8)

        self.source_format_label = QLabel(tr("@convert.source_format"))
        self.source_format_label.setStyleSheet("color: #a6adc8; font-size: 13px;")
        info_row.addWidget(self.source_format_label)

        self.format_value_label = QLabel("--")
        self.format_value_label.setStyleSheet(
            "color: #585b70; font-size: 13px; font-weight: bold;"
        )
        info_row.addWidget(self.format_value_label)

        info_row.addStretch()
        layout.addLayout(info_row)

        # Settings card
        settings_card = QFrame()
        settings_card.setObjectName("settings_card")
        settings_card.setStyleSheet(
            "QFrame#settings_card {"
            "  background-color: #252836;"
            "  border: 1px solid #363a4f;"
            "  border-radius: 10px;"
            "  padding: 14px 18px;"
            "}"
        )
        settings_layout = QVBoxLayout(settings_card)
        settings_layout.setSpacing(10)

        # Target format
        target_row = QHBoxLayout()
        target_row.setSpacing(8)

        self.target_label = QLabel(tr("@convert.target_format"))
        self.target_label.setStyleSheet("color: #a6adc8; font-size: 13px;")
        target_row.addWidget(self.target_label)

        self.format_combo = QComboBox()
        self.format_combo.addItems(["SRT", "ASS", "SSA", "VTT"])
        self.format_combo.setMinimumWidth(160)
        self.format_combo.currentIndexChanged.connect(self._on_target_format_changed)
        target_row.addWidget(self.format_combo)

        target_row.addStretch()
        settings_layout.addLayout(target_row)

        # Output path
        output_row = QHBoxLayout()
        output_row.setSpacing(8)

        self.output_label = QLabel(tr("@convert.output_path"))
        self.output_label.setStyleSheet("color: #a6adc8; font-size: 13px;")
        output_row.addWidget(self.output_label)

        self.output_path_label = QLabel(tr("@convert.auto_output"))
        self.output_path_label.setStyleSheet(
            "color: #a6adc8; font-size: 12px; padding: 4px 0;"
        )
        output_row.addWidget(self.output_path_label, 1)

        self.output_browse_btn = QPushButton(tr("@convert.choose_output"))
        self.output_browse_btn.setStyleSheet(
            "QPushButton { background-color: transparent; color: #89b4fa;"
            "  border: 1px solid #89b4fa; padding: 6px 16px;"
            "  border-radius: 6px; font-size: 13px; }"
            "QPushButton:hover { background-color: #313244; }"
        )
        self.output_browse_btn.clicked.connect(self._browse_output)
        output_row.addWidget(self.output_browse_btn)

        settings_layout.addLayout(output_row)
        layout.addWidget(settings_card)

        # Status
        self.status_label = QLabel(tr("@convert.status.idle"))
        self.status_label.setObjectName("convert_status")
        self.status_label.setWordWrap(True)
        self._set_status_style("idle")
        layout.addWidget(self.status_label)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.convert_btn = QPushButton(tr("@convert.start"))
        self.convert_btn.setFixedWidth(150)
        self.convert_btn.setEnabled(False)
        self.convert_btn.clicked.connect(self._on_convert)
        btn_row.addWidget(self.convert_btn)

        self.open_folder_btn = QPushButton(tr("@convert.open_output_folder"))
        self.open_folder_btn.setStyleSheet(
            "QPushButton { background-color: transparent; color: #89b4fa;"
            "  border: 1px solid #89b4fa; padding: 6px 16px;"
            "  border-radius: 6px; font-size: 13px; }"
            "QPushButton:hover { background-color: #313244; }"
        )
        self.open_folder_btn.setEnabled(False)
        self.open_folder_btn.clicked.connect(self._open_output_folder)
        btn_row.addWidget(self.open_folder_btn)

        btn_row.addStretch()

        self.clear_btn = QPushButton(tr("@convert.clear"))
        self.clear_btn.setStyleSheet(
            "QPushButton { background-color: transparent; color: #f38ba8;"
            "  border: 1px solid #585b70; padding: 6px 16px;"
            "  border-radius: 6px; font-size: 13px; }"
            "QPushButton:hover { background-color: #313244; border-color: #f38ba8; }"
        )
        self.clear_btn.clicked.connect(self._on_clear)
        btn_row.addWidget(self.clear_btn)

        layout.addLayout(btn_row)
        layout.addStretch()

        self._custom_output_path = ""
        self._last_output_path = ""

        i18n.language_changed.connect(self._on_language_changed)

    def _on_language_changed(self, lang):
        self.title_label.setText(tr("@convert.title"))
        self.desc_label.setText(tr("@convert.description"))
        self.target_label.setText(tr("@convert.target_format"))
        self.output_label.setText(tr("@convert.output_path"))
        self.convert_btn.setText(tr("@convert.start"))
        self.clear_btn.setText(tr("@convert.clear"))
        self.open_folder_btn.setText(tr("@convert.open_output_folder"))
        self.output_browse_btn.setText(tr("@convert.choose_output"))
        self.source_format_label.setText(tr("@convert.source_format"))
        if not self._source_path:
            self._set_status_text("idle")
        else:
            self._set_status_text("detected")

    def _on_file_loaded(self, path):
        self._source_path = path
        self._custom_output_path = ""
        self._last_output_path = ""
        self.open_folder_btn.setEnabled(False)
        try:
            raw_text, _enc, _nl = read_subtitle_file(path)
            self._source_format = detect_format(raw_text)
            parser_cls = get_parser(self._source_format)
            sub_file = parser_cls.parse(raw_text)
            self._entry_count = len(sub_file.entries)

            self.format_value_label.setText(self._source_format.name)
            self.format_value_label.setStyleSheet(
                "color: #a6e3a1; font-size: 13px; font-weight: bold;"
            )
            self.convert_btn.setEnabled(True)
            self._set_status_text("detected")
            self._update_output_path()
        except Exception as e:
            self._source_format = None
            self._entry_count = 0
            self.format_value_label.setText("?")
            self.format_value_label.setStyleSheet(
                "color: #f38ba8; font-size: 13px; font-weight: bold;"
            )
            self.convert_btn.setEnabled(False)
            self._set_status_text("failed", msg=str(e))

    def _update_output_path(self):
        if not self._source_path:
            self.output_path_label.setText(tr("@convert.auto_output"))
            return
        if self._custom_output_path:
            self.output_path_label.setText(self._custom_output_path)
            return
        src = Path(self._source_path)
        ext_map = {"SRT": ".srt", "ASS": ".ass", "SSA": ".ssa", "VTT": ".vtt"}
        target_ext = ext_map.get(self.format_combo.currentText(), ".srt")
        name = f"{src.stem}_converted{target_ext}"
        self.output_path_label.setText(str(src.parent / name))

    def _on_target_format_changed(self, idx):
        self._update_output_path()
        if self._source_path and self._source_format:
            self._set_status_text("detected")

    def _browse_output(self):
        target_text = self.format_combo.currentText()
        ext_map = {"SRT": ".srt", "ASS": ".ass", "SSA": ".ssa", "VTT": ".vtt"}
        ext = ext_map.get(target_text, ".srt")
        path, _ = QFileDialog.getSaveFileName(
            self, tr("@convert.choose_output"),
            self.output_path_label.text(),
            f"{target_text} Files (*{ext});;All Files (*.*)",
        )
        if path:
            self._custom_output_path = path
            self.output_path_label.setText(path)

    def _on_convert(self):
        if not self._source_path or not self._source_format:
            return
        target_text = self.format_combo.currentText()
        target_fmt = SubtitleFormat[target_text]
        output_path = self.output_path_label.text()
        if not output_path or output_path == tr("@convert.auto_output"):
            self._update_output_path()
            output_path = self.output_path_label.text()
        self.convert_btn.setEnabled(False)
        self._set_status_style("converting")
        self.status_label.setText(tr("@convert.status.converting"))
        try:
            result = convert_subtitle(self._source_path, output_path, target_fmt)
            self._last_output_path = output_path
            self.open_folder_btn.setEnabled(True)
            self._set_status_text("success", msg=result)
            self.status_message.emit(result)
        except Exception as e:
            self._set_status_text("failed", msg=str(e))
            self.convert_btn.setEnabled(True)

    def _on_clear(self):
        self._source_path = ""
        self._source_format = None
        self._entry_count = 0
        self._custom_output_path = ""
        self._last_output_path = ""
        self.open_folder_btn.setEnabled(False)
        self.convert_btn.setEnabled(False)
        self.drop_zone.clear()
        self.format_value_label.setText("--")
        self.format_value_label.setStyleSheet(
            "color: #585b70; font-size: 13px; font-weight: bold;"
        )
        self._set_status_text("idle")
        self._update_output_path()

    def _open_output_folder(self):
        if self._last_output_path:
            folder = os.path.dirname(os.path.abspath(self._last_output_path))
            try:
                subprocess.Popen(["explorer", folder])
            except Exception:
                pass

    def _set_status_style(self, state):
        colors = {
            "idle": "#6c7086",
            "detected": "#a6e3a1",
            "converting": "#f9e2af",
            "success": "#a6e3a1",
            "failed": "#f38ba8",
        }
        c = colors.get(state, "#6c7086")
        self.status_label.setStyleSheet(
            f"QLabel#convert_status {{ color: {c}; font-size: 13px; padding: 8px 0; }}"
        )

    def _set_status_text(self, state, msg=""):
        self._set_status_style(state)
        if state == "idle":
            self.status_label.setText(tr("@convert.status.idle"))
        elif state == "detected":
            fmt = self._source_format.name if self._source_format else "?"
            self.status_label.setText(
                tr("@convert.status.detected", fmt=fmt, count=str(self._entry_count))
            )
        elif state == "success":
            self.status_label.setText(tr("@convert.status.success", msg=msg))
        elif state == "failed":
            self.status_label.setText(tr("@convert.status.failed", msg=msg))
