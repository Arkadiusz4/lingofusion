import re
from difflib import SequenceMatcher
from typing import List, Dict


def simple_highlight(src: str, out: str) -> List[Dict]:
    """
    Porównuje src i out na poziomie tokenów (słowa + interpunkcja),
    i zwraca listę słowników:
      [{"start": int, "end": int, "suggestion": str}, …]

    Podejście:
    1. Podziel oba teksty na listy tokenów (używamy regex, żeby wyróżnić słowa i wszystko inne).
    2. Użyj SequenceMatcher na listach tokenów, aby znaleźć operacje 'replace', 'insert' i 'delete'.
    3. Dla każdego 'replace' lub 'insert' przelicz token-indeksy z 'out' na pozycje znakowe
       i zanotuj [start, end) oraz sam tekst fragmentu z `out`.
    4. Zwróć te fragmenty jako highlights, gotowe do podświetlenia w frontendzie.
    """

    def tokenize(text: str) -> List[str]:
        return re.findall(r"\w+|\W+", text)

    tokens_src = tokenize(src)
    tokens_out = tokenize(out)

    matcher = SequenceMatcher(None, tokens_src, tokens_out)
    highlights = []

    out_positions = []
    pos = 0
    for tok in tokens_out:
        out_positions.append(pos)
        pos += len(tok)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue

        if tag == "delete":
            continue

        if tag in ("replace", "insert"):
            start_char = out_positions[j1]
            if j2 < len(out_positions):
                end_char = out_positions[j2]
            else:
                end_char = len(out)

            fragment = out[start_char:end_char]
            if fragment.strip():
                highlights.append({
                    "start": start_char,
                    "end": end_char,
                    "suggestion": fragment
                })

    return highlights
