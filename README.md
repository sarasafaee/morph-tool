## Getting Started

### Prerequisites

- Python 3.8+  
- Virtualenv (recommended)

### Install

```bash
git clone https://github.com/your-org/morph-tool.git
cd morph-tool
python3 -m venv venv
source venv/bin/activate      # or `venv\Scripts\activate` on Windows
pip install -r requirements-dev.txt

## Similarity Module (`backend/similarity.py`)

The **Similarity** component provides a simple, yet flexible way to quantify “closeness” between any two strings. Currently it supports:

### 1. Levenshtein Similarity
- Computes the classic edit distance (insertions + deletions + substitutions) via dynamic programming.
- Normalizes by the maximum string length to yield a score in `[0.0 … 1.0]`, where `1.0` means the strings are identical, and `0.0` means they share no characters in common.

### 2. Phonetic Similarity (Soundex)
- Encodes each word with the American Soundex algorithm (first letter + three digits).
- Returns `1.0` if the two Soundex codes match exactly (i.e. they “sound” the same), otherwise `0.0`.
- Useful for catching orthographic variants that share pronunciation (e.g. `color` → `colour`).

#### How to extend
- **Additional string metrics**: add Jaro–Winkler, n-gram cosine, Damerau-Levenshtein, etc., by plugging in new `_your_method(a, b)` functions and wiring them through `calculate_similarity`.
- **Embedding-based similarity**: integrate a pretrained word-embedding model (Word2Vec / FastText / BERT) and compute cosine similarity of vector representations.

---

## Classifier Module (`backend/classifier.py`)

The **Classifier** ranks a set of candidate affixes or word forms by applying a simple, configurable scoring function:

```python
score(c) = α × similarity(base, c)



