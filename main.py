from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure local modules are importable.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

import gui.i18n_extra  # Register additional validation copy.
from gui.main_window import MainWindow


def resource_path(relative_path: str) -> Path:
    """Return a resource path that works in source and PyInstaller builds."""
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_path / relative_path


def application_icon() -> QIcon:
    """Load the packaged PNG icon, falling back to the source SVG artwork."""
    for relative_path in ("assets/app_icon.png", "assets/app_icon.svg"):
        candidate = resource_path(relative_path)
        if candidate.exists():
            icon = QIcon(str(candidate))
            if not icon.isNull():
                return icon
    return QIcon()


def main():
    # Qt 6 enables high-DPI scaling automatically. Legacy AA_* attributes do
    # not need to be changed after QApplication has already been created.
    app = QApplication(sys.argv)
    app.setApplicationName("Bilingual Subtitle Tool")
    app.setApplicationDisplayName("双语字幕工具")

    icon = application_icon()
    if not icon.isNull():
        app.setWindowIcon(icon)

    window = MainWindow()
    if not icon.isNull():
        window.setWindowIcon(icon)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
