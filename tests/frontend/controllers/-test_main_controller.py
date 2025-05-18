import os
import tempfile
import pytest

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from PyQt5.QtGui import QStandardItemModel

import frontend.controllers.main_controller as mc
from frontend.controllers.main_controller import MainController

@pytest.fixture
def controller(qtbot, tmp_path, monkeypatch):
    w = MainController()
    qtbot.addWidget(w)
    w.show()

    # Patch QFileDialog to return predictable paths
    fake_html = str(tmp_path / "out.html")
    fake_pdf  = str(tmp_path / "out.pdf")
    monkeypatch.setattr(
        QFileDialog, 'getSaveFileName',
        lambda *args, **kwargs: (fake_html, None) if "HTML" in args[1] else (fake_pdf, None)
    )

    return w

def test_add_and_remove_candidate(controller):
    # Initially empty
    assert controller.listWidgetCandidates.count() == 0

    # Add candidate
    controller.lineEditWord.setText("demo")
    controller.add_candidate()
    assert controller.listWidgetCandidates.count() == 1
    assert controller.listWidgetCandidates.item(0).text() == "demo"

    # Remove candidate
    controller.listWidgetCandidates.setCurrentRow(0)
    controller.remove_candidate()
    assert controller.listWidgetCandidates.count() == 0

def test_run_classification_and_table_chart(controller, monkeypatch):
    # Stub the classify_word function _in_ main_controller
    fake_result = {"scores": {"x": 0.2, "y": 0.8}, "best": "y"}
    monkeypatch.setattr(mc, 'classify_word',
                        lambda word, cands, alpha, method: fake_result)

    # Set inputs
    controller.lineEditWord.setText("word")
    controller.listWidgetCandidates.addItem("x")
    controller.listWidgetCandidates.addItem("y")
    controller.sliderAlpha.setValue(50)  # alpha=0.5
    controller.comboBoxMethod.setCurrentText("levenshtein")

    # Run classification
    controller.run_classification()

    # Check last_data
    ld = controller.last_data
    assert ld['word']       == "word"
    assert ld['candidates'] == ["x", "y"]
    assert pytest.approx(ld['alpha']) == 0.5
    assert ld['method']     == "levenshtein"
    assert ld['scores']     == fake_result['scores']
    assert ld['best']       == fake_result['best']

    # Table: two rows, correct items
    model: QStandardItemModel = controller.tableViewResults.model()
    assert model.rowCount() == 2
    # find the row for 'y'
    texts = [model.item(r,0).text() for r in range(2)]
    assert 'y' in texts
    # Chart: widgetChart should now have at least one FigureCanvas child
    # (we ignore model children)
    drawn = any(not isinstance(c, QStandardItemModel) for c in controller.widgetChart.children())
    assert drawn

def test_export_html_and_pdf(controller, monkeypatch, tmp_path):
    # Stub the generate_html & generate_pdf in main_controller
    called = {}
    monkeypatch.setattr(mc, 'generate_html',
                        lambda data, path: called.setdefault('html', path))
    monkeypatch.setattr(mc, 'generate_pdf',
                        lambda html, pdf: called.setdefault('pdf', pdf))

    # Without classification: export_html -> warning, no 'html' key
    controller.last_data = None
    called.clear()
    controller.export_html()
    assert 'html' not in called

    # Now simulate a classification
    controller.last_data = {
        'word': 'w',
        'candidates': ['c'],
        'alpha': 1.0,
        'method': 'levenshtein',
        'scores': {'c': 1.0},
        'best': 'c'
    }

    # Export HTML
    controller.export_html()
    assert 'html' in called and called['html'].endswith('.html')

    # Export PDF
    called.clear()
    controller.export_pdf()
    assert 'pdf' in called and called['pdf'].endswith('.pdf')
