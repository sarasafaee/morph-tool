# frontend/controllers/main_controller.py

import os
import tempfile

from PyQt5 import uic
from PyQt5.QtWidgets import (
    QMainWindow,
    QFileDialog,
    QMessageBox,
    QVBoxLayout
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from backend.classifier import classify_word
from reports.generate_report import generate_html, generate_pdf

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt


class MainController(QMainWindow):
    def __init__(self):
        super().__init__()
        # Load UI
        uic.loadUi('frontend/ui/main_window.ui', self)

        # Prepare a layout on the chart widget
        self._chart_layout = QVBoxLayout(self.widgetChart)
        self.widgetChart.setLayout(self._chart_layout)

        # Connect signals
        self.buttonAddCandidate.clicked.connect(self.add_candidate)
        self.buttonRemoveCandidate.clicked.connect(self.remove_candidate)
        self.buttonClassify.clicked.connect(self.run_classification)
        self.buttonExportHTML.clicked.connect(self.export_html)
        self.buttonExportPDF.clicked.connect(self.export_pdf)

        # Placeholder for last classification data
        self.last_data = None

    def add_candidate(self):
        text = self.lineEditWord.text().strip()
        if text:
            self.listWidgetCandidates.addItem(text)

    def remove_candidate(self):
        for item in self.listWidgetCandidates.selectedItems():
            self.listWidgetCandidates.takeItem(self.listWidgetCandidates.row(item))

    def run_classification(self):
        word = self.lineEditWord.text().strip()
        candidates = [
            self.listWidgetCandidates.item(i).text()
            for i in range(self.listWidgetCandidates.count())
        ]
        alpha = self.sliderAlpha.value() / 100.0
        method = self.comboBoxMethod.currentText()

        if not word or not candidates:
            QMessageBox.warning(self, "Input Error",
                                "Please enter a word and at least one candidate.")
            return

        # Perform classification
        result = classify_word(word, candidates, alpha, method)
        # Combine with input parameters for reporting
        self.last_data = {
            'word': word,
            'candidates': candidates,
            'alpha': alpha,
            'method': method,
            **result
        }

        # Update UI
        self._populate_results(result)
        self._draw_chart(result)

    def _populate_results(self, result):
        """
        Populate the QTableView with candidate scores.
        """
        scores = result['scores']
        model = QStandardItemModel(len(scores), 2, self)
        model.setHorizontalHeaderLabels(['Candidate', 'Score'])
        for row, (cand, score) in enumerate(scores.items()):
            item_cand = QStandardItem(cand)
            item_score = QStandardItem(f"{score:.4f}")
            model.setItem(row, 0, item_cand)
            model.setItem(row, 1, item_score)
        self.tableViewResults.setModel(model)
        self.tableViewResults.resizeColumnsToContents()

    def _draw_chart(self, result):
        """
        Render a bar chart of scores into widgetChart.
        """
        # Clear previous chart
        while self._chart_layout.count():
            child = self._chart_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Prepare data
        candidates = list(result['scores'].keys())
        scores = list(result['scores'].values())

        # Draw matplotlib figure
        fig = plt.Figure()
        ax = fig.add_subplot(111)
        ax.bar(candidates, scores)
        ax.set_xlabel('Candidate')
        ax.set_ylabel('Score')
        ax.set_title('Activation Scores')
        fig.tight_layout()

        # Embed in Qt
        canvas = FigureCanvas(fig)
        self._chart_layout.addWidget(canvas)
        canvas.draw()

    def export_html(self):
        """
        Export the last result to an HTML report.
        """
        if not self.last_data:
            QMessageBox.warning(self, "No Data",
                                "Please classify a word before exporting.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save HTML Report", filter="HTML Files (*.html)"
        )
        if path:
            try:
                generate_html(self.last_data, path)
                QMessageBox.information(self, "Success",
                                        f"HTML report saved to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Error",
                                     f"Failed to generate HTML report:\n{e}")

    def export_pdf(self):
        """
        Export the last result to a PDF report (via a temporary HTML).
        """
        if not self.last_data:
            QMessageBox.warning(self, "No Data",
                                "Please classify a word before exporting.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF Report", filter="PDF Files (*.pdf)"
        )
        if path:
            try:
                # Generate temporary HTML
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
                tmp.close()
                generate_html(self.last_data, tmp.name)
                # Convert to PDF
                generate_pdf(tmp.name, path)
                QMessageBox.information(self, "Success",
                                        f"PDF report saved to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Error",
                                     f"Failed to generate PDF report:\n{e}")
            finally:
                try:
                    os.unlink(tmp.name)
                except OSError:
                    pass

