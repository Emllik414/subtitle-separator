from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from gui.drop_zone import DropZone
from gui.i18n import i18n, tr
from gui.ui_components import AppleCard, set_tone
from logic.converter import convert_subtitle
from models.enums import SubtitleFormat
from parsers.base import detect_format, get_parser
from utils.text import read_subtitle_file


class FormatConvertPanel(QWidget):
    status_message = Signal(str)

    def __init__(self):
        super().__init__()
        self._source_format = None
        self._source_path = ""
        self._entry_count = 0
        self._custom_output_path = ""
        self._last_output_path = ""

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(14)
        root.addWidget(left, 6)

        hero = AppleCard(spacing=10)
        self.hero_eyebrow = QLabel("FORMAT CONVERTER")
        self.hero_eyebrow.setObjectName("eyebrow")
        self.title_label = QLabel(tr("@convert.title"))
        self.title_label.setObjectName("pageTitle")
        self.title_label.setStyleSheet("font-size: 22px;")
        self.desc_label = QLabel(tr("@convert.description"))
        self.desc_label.setObjectName("pageDescription")
        self.desc_label.setWordWrap(True)
        hero.content_layout.addWidget(self.hero_eyebrow)
        hero.content_layout.addWidget(self.title_label)
        hero.content_layout.addWidget(self.desc_label)

        flow = QHBoxLayout()
        flow.setSpacing(9)
        self.source_badge = QLabel("SRT")
        self.source_badge.setObjectName("chip")
        arrow = QLabel("→")
        arrow.setObjectName("mutedText")
        self.target_badge = QLabel("ASS")
        self.target_badge.setObjectName("chip")
        flow.addWidget(self.source_badge)
        flow.addWidget(arrow)
        flow.addWidget(self.target_badge)
        flow.addStretch()
        hero.content_layout.addLayout(flow)
        left_layout.addWidget(hero)

        import_card = AppleCard(spacing=10)
        import_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.import_title = QLabel(tr("@convert.import_title"))
        self.import_title.setObjectName("sectionTitle")
        import_card.content_layout.addWidget(self.import_title)
        self.drop_zone = DropZone("@convert.drop_label")
        self.drop_zone.file_changed.connect(self._on_file_loaded)
        import_card.content_layout.addWidget(self.drop_zone, 1)
        left_layout.addWidget(import_card, 1)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(14)
        root.addWidget(right, 4)

        settings = AppleCard(spacing=0)
        self.settings_title = QLabel(tr("@convert.settings_title"))
        self.settings_title.setObjectName("sectionTitle")
        settings.content_layout.addWidget(self.settings_title)

        source_row = self._make_setting_row()
        source_text = QVBoxLayout()
        source_text.setSpacing(2)
        self.source_key = QLabel(tr("@convert.source_format"))
        self.source_key.setObjectName("sectionTitle")
        self.source_key.setStyleSheet("font-size: 12px;")
        self.source_hint = QLabel(tr("@convert.source_auto"))
        self.source_hint.setObjectName("sectionSubtitle")
        source_text.addWidget(self.source_key)
        source_text.addWidget(self.source_hint)
        source_row.addLayout(source_text, 1)
        self.format_value_label = QLabel("—")
        self.format_value_label.setObjectName("chip")
        source_row.addWidget(self.format_value_label)
        settings.content_layout.addLayout(source_row)
        settings.content_layout.addWidget(self._separator())

        target_row = self._make_setting_row()
        target_text = QVBoxLayout()
        target_text.setSpacing(2)
        self.target_label = QLabel(tr("@convert.target_format"))
        self.target_label.setObjectName("sectionTitle")
        self.target_label.setStyleSheet("font-size: 12px;")
        self.target_hint = QLabel(tr("@convert.target_hint"))
        self.target_hint.setObjectName("sectionSubtitle")
        target_text.addWidget(self.target_label)
        target_text.addWidget(self.target_hint)
        target_row.addLayout(target_text, 1)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["SRT", "ASS", "SSA", "VTT"])
        self.format_combo.setMinimumWidth(128)
        self.format_combo.setCurrentText("ASS")
        self.format_combo.currentIndexChanged.connect(self._on_target_format_changed)
        target_row.addWidget(self.format_combo)
        settings.content_layout.addLayout(target_row)
        settings.content_layout.addWidget(self._separator())

        output_row = self._make_setting_row()
        output_text = QVBoxLayout()
        output_text.setSpacing(2)
        self.output_label = QLabel(tr("@convert.output_path"))
        self.output_label.setObjectName("sectionTitle")
        self.output_label.setStyleSheet("font-size: 12px;")
        self.output_path_label = QLabel(tr("@convert.auto_output"))
        self.output_path_label.setObjectName("sectionSubtitle")
        self.output_path_label.setWordWrap(True)
        output_text.addWidget(self.output_label)
        output_text.addWidget(self.output_path_label)
        output_row.addLayout(output_text, 1)
        self.output_browse_btn = QPushButton(tr("@convert.choose_output"))
        self.output_browse_btn.setObjectName("secondaryButton")
        self.output_browse_btn.clicked.connect(self._browse_output)
        output_row.addWidget(self.output_browse_btn)
        settings.content_layout.addLayout(output_row)
        settings.content_layout.addWidget(self._separator())

        status_row = self._make_setting_row()
        status_text = QVBoxLayout()
        status_text.setSpacing(2)
        self.status_key = QLabel(tr("@convert.status_title"))
        self.status_key.setObjectName("sectionTitle")
        self.status_key.setStyleSheet("font-size: 12px;")
        self.status_label = QLabel(tr("@convert.status.idle"))
        self.status_label.setObjectName("sectionSubtitle")
        self.status_label.setWordWrap(True)
        status_text.addWidget(self.status_key)
        status_text.addWidget(self.status_label)
        status_row.addLayout(status_text, 1)
        self.status_pill = QLabel(tr("@convert.status_waiting"))
        self.status_pill.setObjectName("pill")
        set_tone(self.status_pill, "warning")
        status_row.addWidget(self.status_pill)
        settings.content_layout.addLayout(status_row)
        right_layout.addWidget(settings)

        action_card = AppleCard(horizontal=True, margins=(15, 14, 15, 14), spacing=9)
        self.clear_btn = QPushButton(tr("@convert.clear"))
        self.clear_btn.setObjectName("dangerButton")
        self.clear_btn.clicked.connect(self._on_clear)
        action_card.content_layout.addWidget(self.clear_btn)
        action_card.content_layout.addStretch()

        self.open_folder_btn = QPushButton(tr("@convert.open_output_folder"))
        self.open_folder_btn.setObjectName("secondaryButton")
        self.open_folder_btn.setEnabled(False)
        self.open_folder_btn.clicked.connect(self._open_output_folder)
        action_card.content_layout.addWidget(self.open_folder_btn)

        self.convert_btn = QPushButton(tr("@convert.start"))
        self.convert_btn.setObjectName("primaryButton")
        self.convert_btn.setEnabled(False)
        self.convert_btn.clicked.connect(self._on_convert)
        action_card.content_layout.addWidget(self.convert_btn)
        right_layout.addStretch()
        right_layout.addWidget(action_card)

        self._update_target_badge()
        i18n.language_changed.connect(self._on_language_changed)

    @staticmethod
    def _make_setting_row() -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 11, 0, 11)
        row.setSpacing(14)
        return row

    @staticmethod
    def _separator() -> QWidget:
        line = QWidget()
        line.setFixedHeight(1)
        line.setStyleSheet("background: #ededf0;")
        return line

    def _on_language_changed(self, _lang):
        self.title_label.setText(tr("@convert.title"))
        self.desc_label.setText(tr("@convert.description"))
        self.import_title.setText(tr("@convert.import_title"))
        self.settings_title.setText(tr("@convert.settings_title"))
        self.source_key.setText(tr("@convert.source_format"))
        self.source_hint.setText(tr("@convert.source_auto"))
        self.target_label.setText(tr("@convert.target_format"))
        self.target_hint.setText(tr("@convert.target_hint"))
        self.output_label.setText(tr("@convert.output_path"))
        self.output_browse_btn.setText(tr("@convert.choose_output"))
        self.status_key.setText(tr("@convert.status_title"))
        self.convert_btn.setText(tr("@convert.start"))
        self.clear_btn.setText(tr("@convert.clear"))
        self.open_folder_btn.setText(tr("@convert.open_output_folder"))
        if not self._source_path:
            self.output_path_label.setText(tr("@convert.auto_output"))
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
            self.source_badge.setText(self._source_format.name)
            self.convert_btn.setEnabled(True)
            self._set_status_text("detected")
            self._update_output_path()
        except Exception as exc:
            self._source_format = None
            self._entry_count = 0
            self.format_value_label.setText("?")
            self.source_badge.setText("?")
            self.convert_btn.setEnabled(False)
            self._set_status_text("failed", msg=str(exc))

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
        self.output_path_label.setText(str(src.parent / f"{src.stem}_converted{target_ext}"))

    def _update_target_badge(self):
        self.target_badge.setText(self.format_combo.currentText())

    def _on_target_format_changed(self, _idx):
        self._update_target_badge()
        self._update_output_path()
        if self._source_path and self._source_format:
            self._set_status_text("detected")

    def _browse_output(self):
        target_text = self.format_combo.currentText()
        ext_map = {"SRT": ".srt", "ASS": ".ass", "SSA": ".ssa", "VTT": ".vtt"}
        ext = ext_map.get(target_text, ".srt")
        path, _ = QFileDialog.getSaveFileName(
            self,
            tr("@convert.choose_output"),
            self.output_path_label.text(),
            f"{target_text} Files (*{ext});;All Files (*.*)",
        )
        if path:
            self._custom_output_path = path
            self.output_path_label.setText(path)

    def _on_convert(self):
        if not self._source_path or not self._source_format:
            return

        target_fmt = SubtitleFormat[self.format_combo.currentText()]
        output_path = self.output_path_label.text()
        if not output_path or output_path == tr("@convert.auto_output"):
            self._update_output_path()
            output_path = self.output_path_label.text()

        self.convert_btn.setEnabled(False)
        self._set_status_text("converting")
        try:
            result = convert_subtitle(self._source_path, output_path, target_fmt)
            self._last_output_path = output_path
            self.open_folder_btn.setEnabled(True)
            self._set_status_text("success", msg=result)
            self.status_message.emit(result)
            QMessageBox.information(
                self,
                tr("@convert.output_title"),
                tr("@convert.output_msg", path=output_path),
            )
        except Exception as exc:
            self._set_status_text("failed", msg=str(exc))
        finally:
            self.convert_btn.setEnabled(bool(self._source_path and self._source_format))

    def _on_clear(self):
        self._source_path = ""
        self._source_format = None
        self._entry_count = 0
        self._custom_output_path = ""
        self._last_output_path = ""
        self.open_folder_btn.setEnabled(False)
        self.convert_btn.setEnabled(False)
        self.drop_zone.clear()
        self.format_value_label.setText("—")
        self.source_badge.setText("SRT")
        self._set_status_text("idle")
        self._update_output_path()

    def _open_output_folder(self):
        if not self._last_output_path:
            return
        folder = os.path.dirname(os.path.abspath(self._last_output_path))
        try:
            if sys.platform.startswith("win"):
                os.startfile(folder)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["xdg-open", folder])
        except Exception:
            pass

    def _set_status_text(self, state, msg=""):
        if state == "idle":
            self.status_label.setText(tr("@convert.status.idle"))
            self.status_pill.setText(tr("@convert.status_waiting"))
            set_tone(self.status_pill, "warning")
        elif state == "detected":
            fmt = self._source_format.name if self._source_format else "?"
            self.status_label.setText(
                tr("@convert.status.detected", fmt=fmt, count=str(self._entry_count))
            )
            self.status_pill.setText(tr("@convert.status_ready"))
            set_tone(self.status_pill, "success")
        elif state == "converting":
            self.status_label.setText(tr("@convert.status.converting"))
            self.status_pill.setText(tr("@convert.status_working"))
            set_tone(self.status_pill, "warning")
        elif state == "success":
            self.status_label.setText(tr("@convert.status.success", msg=msg))
            self.status_pill.setText(tr("@convert.status_done"))
            set_tone(self.status_pill, "success")
        elif state == "failed":
            self.status_label.setText(tr("@convert.status.failed", msg=msg))
            self.status_pill.setText(tr("@convert.status_error"))
            set_tone(self.status_pill, "error")
