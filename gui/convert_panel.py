from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gui.drop_zone import DropZone
from gui.i18n import i18n, tr
import gui.i18n_extra  # noqa: F401
from gui.ui_components import Card, StatusPill
from logic.converter import convert_subtitle, resolved_conversion_output_path
from models.enums import SubtitleFormat
from parsers.base import detect_format, get_parser
from utils.text import paths_equal, read_subtitle_file


class FormatConvertPanel(QWidget):
    status_message = Signal(str)

    def __init__(self):
        super().__init__()
        self._source_format: SubtitleFormat | None = None
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
        left_layout.addWidget(self._build_hero_card())
        left_layout.addWidget(self._build_import_card(), 1)
        root.addWidget(left, 11)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(14)
        right_layout.addWidget(self._build_settings_card())
        right_layout.addStretch()
        right_layout.addWidget(self._build_actions_card())
        root.addWidget(right, 9)

        i18n.language_changed.connect(self._on_language_changed)
        self._on_language_changed(i18n.current_lang)

    def _build_hero_card(self) -> Card:
        card = Card()
        card.setObjectName("hero_card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(26, 22, 26, 22)
        layout.setSpacing(5)

        self.eyebrow = QLabel("FORMAT CONVERTER")
        self.eyebrow.setObjectName("eyebrow")
        self.hero_title = QLabel()
        self.hero_title.setObjectName("hero_title")
        self.hero_desc = QLabel()
        self.hero_desc.setObjectName("hero_description")
        self.hero_desc.setWordWrap(True)
        layout.addWidget(self.eyebrow)
        layout.addWidget(self.hero_title)
        layout.addWidget(self.hero_desc)

        flow = QHBoxLayout()
        flow.setContentsMargins(0, 12, 0, 0)
        flow.setSpacing(9)
        self.source_tag = QLabel("SRT")
        self.source_tag.setObjectName("format_tag")
        self.source_tag.setAlignment(Qt.AlignCenter)
        arrow = QLabel("→")
        arrow.setObjectName("format_arrow")
        arrow.setAlignment(Qt.AlignCenter)
        self.target_tag = QLabel("ASS")
        self.target_tag.setObjectName("format_tag")
        self.target_tag.setProperty("target", True)
        self.target_tag.setAlignment(Qt.AlignCenter)
        flow.addWidget(self.source_tag)
        flow.addWidget(arrow)
        flow.addWidget(self.target_tag)
        flow.addStretch()
        layout.addLayout(flow)
        return card

    def _build_import_card(self) -> Card:
        card = Card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(17, 16, 17, 16)
        layout.setSpacing(12)
        self.import_title = QLabel()
        self.import_title.setObjectName("card_title")
        layout.addWidget(self.import_title)
        self.drop_zone = DropZone(
            "@convert.preview_drop_main",
            badge_text="SRT",
            replace_content_on_load=True,
        )
        self.drop_zone.setMinimumHeight(190)
        self.drop_zone.file_changed.connect(self._on_file_loaded)
        layout.addWidget(self.drop_zone, 1)
        return card

    def _build_settings_card(self) -> Card:
        card = Card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(17, 16, 17, 16)
        layout.setSpacing(0)
        self.settings_title = QLabel()
        self.settings_title.setObjectName("card_title")
        layout.addWidget(self.settings_title)
        layout.addSpacing(7)

        source_row, self.source_key, self.source_sub, source_right = self._make_settings_row()
        self.source_value = QLabel("--")
        self.source_value.setObjectName("settings_value")
        self.source_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        source_right.addWidget(self.source_value)
        layout.addWidget(source_row)

        target_row, self.target_key, self.target_sub, target_right = self._make_settings_row()
        self.format_combo = QComboBox()
        self.format_combo.setObjectName("format_combo")
        self.format_combo.addItems(["SRT", "ASS", "SSA", "VTT"])
        self.format_combo.setCurrentText("ASS")
        self.format_combo.currentIndexChanged.connect(self._on_target_format_changed)
        target_right.addWidget(self.format_combo)
        layout.addWidget(target_row)

        output_row, self.output_key, self.output_sub, output_right = self._make_settings_row()
        self.output_browse_btn = QPushButton()
        self.output_browse_btn.setObjectName("secondary_button")
        self.output_browse_btn.setCursor(Qt.PointingHandCursor)
        self.output_browse_btn.clicked.connect(self._browse_output)
        output_right.addWidget(self.output_browse_btn)
        layout.addWidget(output_row)

        name_row, self.name_key, self.output_name_label, name_right = self._make_settings_row()
        self.output_name_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.ready_pill = StatusPill(tone="neutral")
        name_right.addWidget(self.ready_pill)
        layout.addWidget(name_row)
        return card

    def _make_settings_row(self):
        row = QFrame()
        row.setObjectName("settings_row")
        row.setMinimumHeight(67)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(14)
        left = QVBoxLayout()
        left.setSpacing(3)
        key = QLabel()
        key.setObjectName("settings_key")
        sub = QLabel()
        sub.setObjectName("card_subtitle")
        sub.setWordWrap(True)
        left.addWidget(key)
        left.addWidget(sub)
        layout.addLayout(left, 1)
        right = QHBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(8)
        layout.addLayout(right)
        return row, key, sub, right

    def _build_actions_card(self) -> Card:
        card = Card()
        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 13, 16, 13)
        layout.setSpacing(9)
        self.clear_btn = QPushButton()
        self.clear_btn.setObjectName("danger_button")
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.clicked.connect(self._on_clear)
        layout.addWidget(self.clear_btn)
        layout.addStretch()
        self.open_folder_btn = QPushButton()
        self.open_folder_btn.setObjectName("secondary_button")
        self.open_folder_btn.setCursor(Qt.PointingHandCursor)
        self.open_folder_btn.setEnabled(False)
        self.open_folder_btn.clicked.connect(self._open_output_folder)
        layout.addWidget(self.open_folder_btn)
        self.convert_btn = QPushButton()
        self.convert_btn.setObjectName("primary_button")
        self.convert_btn.setCursor(Qt.PointingHandCursor)
        self.convert_btn.setEnabled(False)
        self.convert_btn.clicked.connect(self._on_convert)
        layout.addWidget(self.convert_btn)
        return card

    def _on_language_changed(self, _lang: str) -> None:
        self.hero_title.setText(tr("@convert.preview_hero_title"))
        self.hero_desc.setText(tr("@convert.preview_hero_desc"))
        self.import_title.setText(tr("@convert.preview_import_title"))
        self.settings_title.setText(tr("@convert.preview_settings_title"))
        self.source_key.setText(tr("@convert.preview_source_format"))
        self.source_sub.setText(tr("@convert.preview_auto_detect"))
        self.target_key.setText(tr("@convert.preview_target_format"))
        self.target_sub.setText(tr("@convert.preview_target_desc"))
        self.output_key.setText(tr("@convert.preview_output_location"))
        self.output_sub.setText(tr("@convert.preview_output_default"))
        self.name_key.setText(tr("@convert.preview_output_name"))
        self.output_browse_btn.setText(tr("@convert.preview_choose_location"))
        self.clear_btn.setText(tr("@convert.clear"))
        self.open_folder_btn.setText(tr("@convert.open_output_folder"))
        self.convert_btn.setText(tr("@convert.start"))
        self._refresh_state()

    def _on_file_loaded(self, path: str) -> None:
        try:
            raw_text, encoding, _newline = read_subtitle_file(path)
            source_format = detect_format(raw_text)
            parser = get_parser(source_format)
            subtitle = parser.parse(raw_text)
            if not subtitle.entries:
                raise ValueError(tr("@error.no_entries"))
        except Exception as exc:
            self.drop_zone.restore_state()
            QMessageBox.warning(self, tr("@convert.preview_load_failed"), tr("@error.load", msg=str(exc)))
            return

        self._source_path = path
        self._source_format = source_format
        self._entry_count = len(subtitle.entries)
        self._custom_output_path = ""
        self._last_output_path = ""
        self.open_folder_btn.setEnabled(False)
        self.drop_zone.set_loaded_metadata(
            path,
            source_format.name,
            tr(
                "@convert.preview_loaded_meta",
                fmt=source_format.name,
                count=self._entry_count,
                encoding=encoding.upper(),
            ),
        )
        self.convert_btn.setEnabled(True)
        self._update_output_path()
        self._refresh_state()
        self.status_message.emit(
            tr("@convert.status.detected", fmt=source_format.name, count=self._entry_count)
        )

    def _target_format(self) -> SubtitleFormat:
        return SubtitleFormat[self.format_combo.currentText()]

    def _on_target_format_changed(self, _index: int) -> None:
        self.target_tag.setText(self.format_combo.currentText())
        if self._custom_output_path:
            self._custom_output_path = resolved_conversion_output_path(
                self._custom_output_path,
                self._target_format(),
            )
        self._update_output_path()
        self._refresh_state()

    def _default_output_path(self) -> str:
        if not self._source_path:
            return ""
        source = Path(self._source_path)
        base = str(source.parent / f"{source.stem}_converted")
        return resolved_conversion_output_path(base, self._target_format())

    def _resolved_output_path(self) -> str:
        candidate = self._custom_output_path or self._default_output_path()
        if not candidate:
            return ""
        return resolved_conversion_output_path(candidate, self._target_format())

    def _update_output_path(self) -> None:
        output_path = self._resolved_output_path()
        if not output_path:
            self.output_name_label.setText(tr("@convert.preview_no_output"))
            self.output_name_label.setToolTip("")
            return
        self.output_name_label.setText(os.path.basename(output_path))
        self.output_name_label.setToolTip(output_path)

    def _browse_output(self) -> None:
        target = self.format_combo.currentText()
        extension = {"SRT": ".srt", "ASS": ".ass", "SSA": ".ssa", "VTT": ".vtt"}.get(target, ".srt")
        path, _ = QFileDialog.getSaveFileName(
            self,
            tr("@convert.choose_output"),
            self._resolved_output_path(),
            f"{target} Files (*{extension});;All Files (*.*)",
        )
        if path:
            self._custom_output_path = resolved_conversion_output_path(path, self._target_format())
            self._update_output_path()
            self._refresh_state()

    def _refresh_state(self) -> None:
        self.target_tag.setText(self.format_combo.currentText())
        if not self._source_format:
            self.source_tag.setText("SRT")
            self.source_value.setText("--")
            self.output_name_label.setText(tr("@convert.preview_no_output"))
            self.ready_pill.setText(tr("@convert.preview_waiting"))
            self.ready_pill.set_tone("neutral")
            return

        self.source_tag.setText(self._source_format.name)
        self.source_value.setText(
            tr("@convert.preview_source_value", fmt=self._source_format.name, count=self._entry_count)
        )
        self._update_output_path()
        if paths_equal(self._source_path, self._resolved_output_path()):
            self.ready_pill.setText(tr("@convert.preview_path_conflict"))
            self.ready_pill.set_tone("danger")
        else:
            self.ready_pill.setText(tr("@convert.preview_ready"))
            self.ready_pill.set_tone("success")

    def _on_convert(self) -> None:
        if not self._source_path or not self._source_format:
            return

        output_path = self._resolved_output_path()
        if paths_equal(self._source_path, output_path):
            QMessageBox.warning(self, tr("@error.output_path_title"), tr("@error.output_overwrites_source"))
            return

        self.convert_btn.setEnabled(False)
        self.ready_pill.setText(tr("@convert.status.converting"))
        self.ready_pill.set_tone("warning")
        try:
            result = convert_subtitle(self._source_path, output_path, self._target_format())
            self._last_output_path = output_path
            self.open_folder_btn.setEnabled(True)
            self.ready_pill.setText(tr("@convert.preview_complete"))
            self.ready_pill.set_tone("success")
            self.status_message.emit(result)
            QMessageBox.information(
                self,
                tr("@convert.output_title"),
                tr("@convert.output_msg", path=output_path),
            )
        except Exception as exc:
            self.ready_pill.setText(tr("@convert.preview_failed"))
            self.ready_pill.set_tone("danger")
            QMessageBox.warning(
                self,
                tr("@convert.preview_failed"),
                tr("@convert.status.failed", msg=str(exc)),
            )
            self.status_message.emit(tr("@convert.status.failed", msg=str(exc)))
        finally:
            self.convert_btn.setEnabled(True)

    def _on_clear(self) -> None:
        self._source_path = ""
        self._source_format = None
        self._entry_count = 0
        self._custom_output_path = ""
        self._last_output_path = ""
        self.drop_zone.clear()
        self.convert_btn.setEnabled(False)
        self.open_folder_btn.setEnabled(False)
        self._refresh_state()
        self.status_message.emit(tr("@status.ready"))

    def _open_output_folder(self) -> None:
        if not self._last_output_path:
            return
        folder = os.path.dirname(os.path.abspath(self._last_output_path))
        try:
            if os.name == "nt":
                os.startfile(folder)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["xdg-open", folder])
        except Exception as exc:
            QMessageBox.warning(
                self,
                tr("@convert.open_output_folder"),
                tr("@error.open_folder_failed", msg=str(exc)),
            )
