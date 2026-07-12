import os
import sys

# Ensure local modules are importable.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication

import gui.i18n_extra  # Register additional validation copy.
from gui.main_window import MainWindow


def main():
    # Qt 6 enables high-DPI scaling automatically. Legacy AA_* attributes do
    # not need to be changed after QApplication has already been created.
    app = QApplication(sys.argv)
    app.setApplicationName("Bilingual Subtitle Tool")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
