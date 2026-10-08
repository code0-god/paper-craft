from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / '.agents/skills/paper-craft/scripts/editing_guard.py'


class SemanticEditingTests(unittest.TestCase):
    def run_guard(self, original: str, revised: str) -> dict:
        with tempfile.TemporaryDirectory() as directory:
            before, after = Path(directory) / 'original.txt', Path(directory) / 'revised.txt'
            before.write_text(original, encoding='utf-8')
            after.write_text(revised, encoding='utf-8')
            original_bytes, revised_bytes = before.read_bytes(), after.read_bytes()
            result = subprocess.run([sys.executable, str(SCRIPT), str(before), str(after), '--json'],
                                    capture_output=True, text=True, check=False)
            self.assertEqual(before.read_bytes(), original_bytes)
            self.assertEqual(after.read_bytes(), revised_bytes)
            return json.loads(result.stdout)

    def test_swapped_associations_require_review_when_numeric_bag_is_equal(self) -> None:
        report = self.run_guard('A takes 10 ns; B takes 20 ns.', 'A takes 20 ns; B takes 10 ns.')
        self.assertEqual(report['status'], 'UNKNOWN')
        self.assertEqual(report['semantic_review'], 'MANUAL_REQUIRED')
        self.assertIn('number_association', [item['check'] for item in report['semantic_signals']])
        self.assertTrue(all(item['status'] == 'UNKNOWN' for item in report['semantic_signals']))
        self.assertTrue(report['touched_contexts'])

    def test_risky_changes_are_signals_when_english_or_korean_claims_change(self) -> None:
        cases = [('A does not reduce latency.', 'A does reduce latency.', 'negation'),
                 ('A is faster than B.', 'A is slower than B.', 'comparison'),
                 ('A correlates with B.', 'A causes B.', 'causality'),
                 ('A may help.', 'A always helps.', 'confidence'),
                 ('A may help; B always helps.', 'A always helps; B may help.', 'confidence'),
                 ('A는 성능을 개선하지 않는다.', 'A는 성능을 개선한다.', 'negation'),
                 ('A는 B보다 높다.', 'A는 B보다 낮다.', 'comparison'),
                 ('The model predicts 10 ns.', 'Hardware measurement gives 10 ns.', 'evidence_context')]
        for before, after, signal in cases:
            with self.subTest(signal=signal, before=before):
                report = self.run_guard(before, after)
                self.assertIn(signal, [item['check'] for item in report['semantic_signals']])
                self.assertEqual(report['semantic_review'], 'MANUAL_REQUIRED')

    def test_protected_changes_still_fail(self) -> None:
        report = self.run_guard('A takes 10 ns.', 'A takes 20 ns.')
        self.assertEqual(report['status'], 'FAIL')

    def test_unchanged_text_does_not_become_semantically_verified(self) -> None:
        report = self.run_guard('A may help.', 'A may help.')
        self.assertEqual(report['status'], 'UNKNOWN')
        self.assertEqual(report['semantic_signals'], [])
        self.assertEqual(report['touched_contexts'], [])


if __name__ == '__main__':
    unittest.main()
