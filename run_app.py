import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor

from frontend.controllers.main_controller import MainController

def main():
    app = QApplication(sys.argv)
    with open("frontend/style.qss", "r") as f:
        app.setStyleSheet(f.read())

    window = MainController()
    window.verticalLayout.setContentsMargins(20,20,20,20)
    window.verticalLayout.setSpacing(15)

    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
