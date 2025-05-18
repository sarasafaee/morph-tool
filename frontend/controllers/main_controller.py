import os
import sys
import tempfile

from PyQt5 import uic
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QStandardItemModel, QStandardItem

from backend.classifier import classify_word
from reports.generate_report import generate_html, generate_pdf


class MainController(QMainWindow):
    def __init__(self):
        super().__init__()

        app = QApplication.instance() or QApplication(sys.argv)
        app.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#fafafa"))
        palette.setColor(QPalette.Base, QColor("#ffffff"))
        palette.setColor(QPalette.AlternateBase, QColor("#f5f5f5"))
        palette.setColor(QPalette.Button, QColor("#fff1f0"))
        palette.setColor(QPalette.Highlight, QColor("#1890ff"))
        palette.setColor(QPalette.ButtonText, Qt.black)
        palette.setColor(QPalette.Text, Qt.black)
        app.setPalette(palette)

        qss_path = os.path.join(os.path.dirname(__file__), '..', 'style.qss')
        try:
            with open(qss_path, 'r') as f:
                app.setStyleSheet(f.read())
        except FileNotFoundError:
            pass

        ui_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'main_window.ui')
        uic.loadUi(ui_path, self)

        central_layout = self.centralwidget.layout()
        central_layout.setContentsMargins(20, 20, 20, 20)
        central_layout.setSpacing(15)

        self.buttonAddCandidate.clicked.connect(self.add_candidate)
        self.buttonRemoveCandidate.clicked.connect(self.remove_candidate)
        self.buttonClassify.clicked.connect(self.run_classification)
        self.buttonExportHTML.clicked.connect(self.export_html)
        self.buttonExportPDF.clicked.connect(self.export_pdf)
        self.update_alpha_label(self.sliderAlpha.value())
        self.sliderAlpha.valueChanged.connect(self.update_alpha_label)

        self.last_data = None

    def add_candidate(self):
        text = self.lineEditWord.text().strip()
        if text:
            self.listWidgetCandidates.addItem(text)

    def remove_candidate(self):
        for item in self.listWidgetCandidates.selectedItems():
            self.listWidgetCandidates.takeItem(
                self.listWidgetCandidates.row(item)
            )

    def run_classification(self):
        word = self.lineEditWord.text().strip()
        candidates = [
            self.listWidgetCandidates.item(i).text()
            for i in range(self.listWidgetCandidates.count())
        ]
        alpha = self.sliderAlpha.value() / 100.0
        method = self.comboBoxMethod.currentText()

        if not word or not candidates:
            QMessageBox.warning(
                self,
                "Input Error",
                "Please enter a word and at least one candidate."
            )
            return

        result = classify_word(word, candidates, alpha, method)
        # Store for exports
        self.last_data = {
            'word': word,
            'candidates': candidates,
            'alpha': alpha,
            'method': method,
            **result
        }
        self._populate_results(result)

    def _populate_results(self, result):
        scores = result['scores']
        model = QStandardItemModel(len(scores), 2, self)
        model.setHorizontalHeaderLabels(['Candidate', 'Score'])
        for row, (cand, score) in enumerate(scores.items()):
            model.setItem(row, 0, QStandardItem(cand))
            model.setItem(row, 1, QStandardItem(f"{score:.4f}"))
        self.tableViewResults.setModel(model)
        self.tableViewResults.resizeColumnsToContents()

    def export_html(self):
        if not self.last_data:
            QMessageBox.warning(
                self,
                "No Data",
                "Please classify a word before exporting."
            )
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save HTML Report",
            filter="HTML Files (*.html)"
        )
        if path:
            try:
                generate_html(self.last_data, path)
                QMessageBox.information(
                    self,
                    "Success",
                    f"HTML report saved to:\n{path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to generate HTML report:\n{e}"
                )

    def export_pdf(self):
        if not self.last_data:
            QMessageBox.warning(
                self,
                "No Data",
                "Please classify a word before exporting."
            )
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF Report",
            filter="PDF Files (*.pdf)"
        )
        if path:
            try:
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
                tmp.close()
                generate_html(self.last_data, tmp.name)
                generate_pdf(tmp.name, path)
                QMessageBox.information(
                    self,
                    "Success",
                    f"PDF report saved to:\n{path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to generate PDF report:\n{e}"
                )
            finally:
                try:
                    os.unlink(tmp.name)
                except OSError:
                    pass

    def update_alpha_label(self, slider_val: int):
        """Slot to show the slider’s value as a 0.00–1.00 float."""
        alpha = slider_val / 100.0
        self.labelAlphaValue.setText(f"{alpha:.2f}")
