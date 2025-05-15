# tests/backend/test_classifier.py

import pytest
from backend.classifier import classify_word

def test_classify_single_candidate():
    res = classify_word("test", ["test"], alpha=0.5)
    # similarity("test","test") == 1.0 → score = 0.5
    assert res["scores"] == {"test": pytest.approx(0.5)}
    assert res["best"] == "test"

def test_classify_multiple_candidates():
    # "a"→"a": sim=1.0, score=0.8; "a"→"b": sim=0.0, score=0.0
    res = classify_word("a", ["a", "b"], alpha=0.8)
    assert res["scores"]["a"] == pytest.approx(0.8)
    assert res["scores"]["b"] == pytest.approx(0.0)
    assert res["best"] == "a"

def test_alpha_bounds():
    with pytest.raises(ValueError):
        classify_word("x", ["y"], alpha=-0.1)
    with pytest.raises(ValueError):
        classify_word("x", ["y"], alpha=1.1)

def test_empty_candidates():
    with pytest.raises(ValueError):
        classify_word("word", [], alpha=0.5)

def test_method_parameter():
    # Using phonetic: two different spellings with same sound
    res = classify_word("Robert", ["Rupert", "Smith"], alpha=1.0, method="phonetic")
    # only Rupert matches phonetically
    assert res["scores"]["Rupert"] == pytest.approx(1.0)
    assert res["scores"]["Smith"] == pytest.approx(0.0)
    assert res["best"] == "Rupert"
