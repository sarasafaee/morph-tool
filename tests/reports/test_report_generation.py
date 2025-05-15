import os
import tempfile
import pytest
from reports.generate_report import generate_html, generate_pdf

@pytest.fixture
def sample_data(tmp_path):
    # Create a minimal data dict
    return {
        'word': 'analysis',
        'candidates': ['-able', '-ible'],
        'alpha': 0.75,
        'method': 'levenshtein',
        'scores': {'-able': 0.83, '-ible': 0.77},
        'best': '-able'
    }

def test_generate_html_creates_file(sample_data, tmp_path):
    html_path = tmp_path / "report.html"
    # Call generate_html
    generate_html(sample_data, str(html_path))
    # Assert file exists and contains key pieces
    assert html_path.exists()
    content = html_path.read_text(encoding='utf-8')
    assert "<h1>Report: analysis</h1>" in content
    assert "<td>-able</td>" in content
    assert "0.8300" in content  # formatted score
    # Chart image reference
    assert "report_chart.png" in content or "_chart.png" in content

def test_generate_pdf_creates_file(sample_data, tmp_path):
    # First generate HTML
    html_path = tmp_path / "temp.html"
    pdf_path = tmp_path / "report.pdf"
    generate_html(sample_data, str(html_path))
    # Now PDF
    generate_pdf(str(html_path), str(pdf_path))
    # Assert PDF exists and is non-empty
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0

def test_chart_image_is_created(sample_data, tmp_path):
    html_path = tmp_path / "report.html"
    # After HTML generation, chart PNG should exist
    generate_html(sample_data, str(html_path))
    chart_path = tmp_path / (html_path.stem + "_chart.png")
    assert chart_path.exists()
    assert chart_path.stat().st_size > 0
