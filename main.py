import os
import sys

# Ensure local modules are importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtCore import QLocale, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from gui.i18n import i18n
from gui.main_window import MainWindow


def main():
    # These flags are ignored by newer Qt 6 builds but remain harmless for
    # compatible PySide6 versions. They must be configured before QApplication.
    if hasattr(Qt, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Subtitle Studio")
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))

    system_language = QLocale.system().language()
    chinese_language = getattr(QLocale.Language, "Chinese", None)
    i18n.set_language("zh" if system_language == chinese_language else "en")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
