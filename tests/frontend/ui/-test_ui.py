# tests/frontend/test_ui.py

import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox
from frontend.controllers.main_controller import MainController

def test_ui_smoke(qtbot):
    """Smoke‐test that the main window and its key widgets load."""
    window = MainController()
    qtbot.addWidget(window)
    window.show()

    assert window.lineEditWord is not None
    assert window.listWidgetCandidates is not None
    assert window.buttonClassify.text() == "Classify"
    assert window.tableViewResults is not None
    assert window.widgetChart is not None
    assert window.buttonExportHTML is not None

def test_classify_without_input_shows_warning(qtbot, monkeypatch):
    """Clicking Classify with no inputs should pop a warning dialog."""
    window = MainController()
    qtbot.addWidget(window)
    window.show()

    # Capture QMessageBox.warning calls
    called = {}
    def fake_warning(self, title, text):
        called['title'] = title
        called['text'] = text

    monkeypatch.setattr(QMessageBox, 'warning', fake_warning)

    # Simulate click on Classify
    qtbot.mouseClick(window.buttonClassify, Qt.LeftButton)

    # Verify warning invoked
    assert called['title'] == "Input Error"
    assert "Please enter a word and at least one candidate" in called['text']
