import re
from difflib import SequenceMatcher
from typing import List, Dict


def simple_highlight(src: str, out: str) -> List[Dict]:
    """
    Porównuje src i out na poziomie tokenów (słowa + interpunkcja),
    i zwraca listę słowników:
      [{"start": int, "end": int, "suggestion": str}, …]
    """

    def tokenize(text: str) -> List[str]:
        return re.findall(r"\w+|\W+", text)

    tokens_src = tokenize(src)
    tokens_out = tokenize(out)

    matcher = SequenceMatcher(None, tokens_src, tokens_out)
    highlights: List[Dict] = []

    out_positions: List[int] = []
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
            end_char = out_positions[j2] if j2 < len(out_positions) else len(out)
            fragment = out[start_char:end_char]
            if fragment.strip():
                highlights.append({
                    "start": start_char,
                    "end": end_char,
                    "suggestion": fragment
                })

    return highlights
