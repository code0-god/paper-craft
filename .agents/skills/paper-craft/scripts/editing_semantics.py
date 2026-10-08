"""Conservative lexical review hints; no static semantic-equivalence verdict."""
from __future__ import annotations

import difflib
import re
from collections import Counter
from typing import Final, TypedDict

from manuscript_common import Finding, notice

RISK_TERMS: Final = {
    'negation': r"\b(?:no|not|never|without|neither|cannot)\b|n't\b|않|없|아니|못|불가능",
    'comparison': r'\b(?:more|less|faster|slower|higher|lower|better|worse|than|outperform\w*)\b|보다|높|낮|빠르|느리|우수|열등',
    'causality': r'\b(?:caus\w*|because|therefore|hence|correlat\w*|lead\w*|result\w*)\b|때문|인해|유발|원인|상관|따라서',
    'confidence': r'\b(?:may|might|could|can|must|always|all|never|suggest\w*|prove\w*|likely|possibly|guarantee\w*)\b|가능|추정|확실|항상|모든|입증|보장',
    'evidence_context': r'\b(?:model\w*|predict\w*|simulat\w*|measur\w*|hardware|theoretic\w*|empiric\w*)\b|모델|예측|시뮬레이션|측정|실측|이론|하드웨어',
}


class TouchedContext(TypedDict):
    original_sentence_start: int
    revised_sentence_start: int
    original: list[str]
    revised: list[str]


def sentences(text: str) -> list[str]:
    # ponytail: lexical sentence boundaries miss abbreviations; inspect whole affected paragraphs manually.
    return [part.strip() for part in re.split(r'(?<=[.!?])\s+|\n+', text) if part.strip()]


def token_contexts(text: str, pattern: re.Pattern[str]) -> Counter[tuple[str, str, str]]:
    """Associate each lexical occurrence with nearby words inside its sentence."""
    return Counter((match.group(), ' '.join(sentence[:match.start()].split()[-4:]),
                    ' '.join(sentence[match.end():].split()[:4]))
                   for sentence in sentences(text) for match in pattern.finditer(sentence))


def semantic_hints(before: str, after: str, number: re.Pattern[str]) -> tuple[list[Finding], list[TouchedContext]]:
    """Return UNKNOWN hints for changed contexts, including equal-bag numeric swaps."""
    old, new = sentences(before), sentences(after)
    contexts: list[TouchedContext] = [
        {'original_sentence_start': i + 1, 'revised_sentence_start': j + 1,
         'original': old[i:end_i], 'revised': new[j:end_j]}
        for tag, i, end_i, j, end_j in difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes()
        if tag != 'equal'
    ]
    signals: list[Finding] = []
    if contexts:
        signals.append(notice('changed_context', 'Sentence/context changed; inspect associated claims, conditions and paragraph scope', 'UNKNOWN'))
    if token_contexts(before, number) != token_contexts(after, number):
        signals.append(notice('number_association', 'Number-to-context association changed; equal numeric multisets do not establish equivalence', 'UNKNOWN'))
    for check, pattern in RISK_TERMS.items():
        matcher = re.compile(pattern, re.IGNORECASE)
        if token_contexts(before, matcher) != token_contexts(after, matcher):
            signals.append(notice(check, 'Risk-term context changed; inspect meaning manually (lexical hint, not a scientific error)', 'UNKNOWN'))
    return signals, contexts
