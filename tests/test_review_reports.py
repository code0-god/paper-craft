from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / '.agents/skills/paper-craft/scripts/validate_review_report.py'
FIXTURES = ROOT / 'tests/scenarios/reports'


class ReviewReportTests(unittest.TestCase):
    def run_report(self, report: dict) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'report.json'
            path.write_text(json.dumps(report), encoding='utf-8')
            before = path.read_bytes()
            result = subprocess.run([sys.executable, str(SCRIPT), str(path), '--json'],
                                    capture_output=True, text=True, check=False)
            self.assertEqual(path.read_bytes(), before)
            return result

    def test_legacy_and_v2_remain_readable_without_scientific_pass(self) -> None:
        for fixture, version in [('legacy.json', None), ('legacy.json', 1), ('v2.json', 2)]:
            with self.subTest(fixture=fixture, version=version):
                report = json.loads((FIXTURES / fixture).read_text())
                if version is not None:
                    report['schema_version'] = version
                result = self.run_report(report)
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                output = json.loads(result.stdout)
                self.assertEqual(output['structure_status'], 'PASS')
                self.assertEqual(output['scientific_status'], 'UNKNOWN')
                self.assertEqual(output['semantic_review'], 'MANUAL_REQUIRED')

    def test_invalid_types_enums_references_and_versions_are_rejected(self) -> None:
        mutations = [
            lambda r: r.update(schema_version=True),
            lambda r: r.update(schema_version=3),
            lambda r: r.update(mode='automatic_rewrite'),
            lambda r: r['verification_scope'].update(performed=True),
            lambda r: r['findings'][0].update(evidence_state='verified'),
            lambda r: r['findings'][0].update(claim_ids=['C404']),
            lambda r: r['findings'][0]['provenance'].update(kind='measured'),
            lambda r: r['findings'][0]['provenance']['artifacts'][0].update(input_id='I404'),
            lambda r: r['findings'][0]['evidence_axes']['validity'].update(status='VALID'),
            lambda r: r['findings'][0]['evidence_axes'].pop('inference'),
            lambda r: r['edits'][0].update(categories=['silent_weakening']),
            lambda r: r['edits'][0].update(categories=[]),
            lambda r: r['inputs'][0].update(sha256='bad'),
            lambda r: r['findings'][0].update(support_state='needs_validation'),
            lambda r: r['findings'][0].update(id='C1'),
            lambda r: r['findings'][0]['provenance'].update(kind='independently_reproduced'),
            lambda r: r['verification_scope'].update(unperformed=['source reading']),
            lambda r: r['findings'][0].update(current_state='verified'),
            lambda r: r['edits'][0].update(categories=['language_only', 'language_only']),
            lambda r: r['edits'][0].update(claim_ids=['C404']),
            lambda r: r['claims'][0].update(evidence_locations=42),
            lambda r: r['findings'][0]['evidence_axes']['existence'].update(rationale=''),
        ]
        for index, mutate in enumerate(mutations):
            with self.subTest(index=index):
                report = json.loads((FIXTURES / 'v2.json').read_text())
                mutate(report)
                result = self.run_report(report)
                self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
                self.assertEqual(json.loads(result.stdout)['structure_status'], 'FAIL')

    def test_included_graph_is_validated_at_its_shared_boundary(self) -> None:
        report = json.loads((FIXTURES / 'v2.json').read_text())
        report['argument_graph'] = {'schema_version': 1, 'nodes': []}
        result = self.run_report(report)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['structure_status'], 'FAIL')

    def test_shared_graph_claims_require_consistent_state_and_input_metadata(self) -> None:
        report = json.loads((FIXTURES / 'v2.json').read_text())
        graph = json.loads((ROOT / 'tests/scenarios/graphs/mixed.json').read_text())
        report['argument_graph'] = graph
        report['inputs'].extend(dict(source, read_status='read') for source in graph['inputs'])
        report['findings'][0]['claim_ids'].append('n0')
        result = self.run_report(report)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['graph_reuse_status'], 'UNKNOWN')
        report['claims'][0]['id'] = 'n0'
        report['findings'][0]['claim_ids'] = ['n0']
        report['edits'][0]['claim_ids'] = ['n0']
        result = self.run_report(report)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_inline_graph_metadata_must_match_report_inputs(self) -> None:
        report = json.loads((FIXTURES / 'v2.json').read_text())
        graph = json.loads((ROOT / 'tests/scenarios/graphs/mixed.json').read_text())
        report['argument_graph'] = graph
        report['inputs'].extend(dict(source, read_status='read') for source in graph['inputs'])
        report['inputs'][-1]['sha256'] = 'f' * 64
        result = self.run_report(report)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['error_field'], 'argument_graph')

    def test_graph_reference_is_metadata_only_without_a_freshness_claim(self) -> None:
        report = json.loads((FIXTURES / 'v2.json').read_text())
        report['argument_graph_reference'] = {'path': 'graph.json', 'sha256': '0' * 64,
                                              'claim_ids': ['C2']}
        report['findings'][0]['claim_ids'].append('C2')
        result = self.run_report(report)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['graph_reuse_status'], 'UNKNOWN')

    def test_diagnostics_do_not_echo_raw_private_values(self) -> None:
        report = json.loads((FIXTURES / 'v2.json').read_text())
        secret = '/private/user/path'
        report['findings'][0]['provenance']['kind'] = secret
        result = self.run_report(report)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(secret, result.stdout + result.stderr)

    def test_legacy_wrong_field_types_are_rejected(self) -> None:
        report = json.loads((FIXTURES / 'legacy.json').read_text())
        report['findings'] = 'not-an-array'
        result = self.run_report(report)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
