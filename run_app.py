#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication
from frontend.controllers.main_controller import MainController

def main():
    app = QApplication(sys.argv)
    window = MainController()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
