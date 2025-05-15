# tests/backend/test_similarity.py

import pytest
from backend.similarity import calculate_similarity, _soundex

def test_levenshtein_identical():
    assert calculate_similarity("test", "test") == 1.0

def test_levenshtein_empty():
    assert calculate_similarity("", "") == 1.0
    assert calculate_similarity("a", "") == 0.0

def test_levenshtein_basic():
    # 'kitten' → 'sitting' has distance 3 over max_len=7
    assert calculate_similarity("kitten", "sitting") == pytest.approx(1 - 3/7)

def test_unknown_method():
    with pytest.raises(ValueError):
        calculate_similarity("a", "b", method="foobar")

def test_soundex_known():
    # classic Soundex example: Robert/Rupert → R163
    assert _soundex("Robert") == "R163"
    assert _soundex("Rupert") == "R163"
    assert calculate_similarity("Robert", "Rupert", method="phonetic") == 1.0

def test_soundex_mismatch():
    assert calculate_similarity("Smith", "Johnson", method="phonetic") == 0.0

def test_soundex_empty():
    assert _soundex("") == "0000"
