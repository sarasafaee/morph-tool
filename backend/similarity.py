# backend/similarity.py

"""
Module: similarity
Provides functions to compute string (Levenshtein) and simple phonetic (Soundex) similarity.
"""

def calculate_similarity(a: str, b: str, method: str = 'levenshtein') -> float:
    """
    Compute a similarity score between strings a and b.
    - method='levenshtein': normalized [0.0–1.0], where 1.0 means identical.
    - method='phonetic': returns 1.0 if Soundex codes match, else 0.0.
    """
    a, b = a.lower(), b.lower()
    if method == 'levenshtein':
        return _levenshtein_similarity(a, b)
    elif method == 'phonetic':
        return _phonetic_similarity(a, b)
    else:
        raise ValueError(f"Unknown method '{method}'")

def _levenshtein_similarity(a: str, b: str) -> float:
    # classic DP
    m, n = len(a), len(b)
    if m == 0 and n == 0:
        return 1.0
    # build distance matrix
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(m+1):
        dp[i][0] = i
    for j in range(n+1):
        dp[0][j] = j
    for i in range(1, m+1):
        for j in range(1, n+1):
            cost = 0 if a[i-1] == b[j-1] else 1
            dp[i][j] = min(
                dp[i-1][j] + 1,    # deletion
                dp[i][j-1] + 1,    # insertion
                dp[i-1][j-1] + cost  # substitution
            )
    dist = dp[m][n]
    # normalize by max length
    max_len = max(m, n)
    return 1.0 - dist/max_len

def _phonetic_similarity(a: str, b: str) -> float:
    return 1.0 if _soundex(a) == _soundex(b) else 0.0

def _soundex(word: str) -> str:
    """
    Basic Soundex implementation:
    - Keep first letter.
    - Map letters → digits (per American Soundex).
    - Drop repeats and zeros, pad/truncate to 4 chars.
    """
    codes = {
        'a': '0','e': '0','i': '0','o': '0','u': '0','y': '0','h': '0','w': '0',
        'b': '1','f': '1','p': '1','v': '1',
        'c': '2','g': '2','j': '2','k': '2','q': '2','s': '2','x': '2','z': '2',
        'd': '3','t': '3',
        'l': '4',
        'm': '5','n': '5',
        'r': '6'
    }
    if not word:
        return "0000"
    first, tail = word[0], word[1:]
    # encode tail
    encoded = [codes.get(ch, '') for ch in tail]
    # drop zeros and duplicates
    filtered = []
    prev = codes.get(first, '')
    for code in encoded:
        if code != prev and code != '0':
            filtered.append(code)
        prev = code
    # build result
    sound = first.upper() + ''.join(filtered)
    sound = (sound + '000')[:4]
    return sound
