from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / '.agents/skills/paper-craft'
FIXTURES = ROOT / 'tests/scenarios/graphs'


class ArgumentGraphTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.graph = json.loads((FIXTURES / 'mixed.json').read_text())
        self.source = self.root / 'source.txt'
        self.source.write_bytes((FIXTURES / 'source.txt').read_bytes())
        self.graph_path = self.root / 'external-review' / 'graph.json'
        self.graph_path.parent.mkdir()

    def run_graph(self, *, check_inputs: bool = True) -> subprocess.CompletedProcess[str]:
        self.graph_path.write_text(json.dumps(self.graph), encoding='utf-8')
        return subprocess.run([sys.executable, str(SKILL / 'scripts/argument_graph.py'), 'validate',
                               str(self.graph_path), '--project-root', str(self.root), '--json',
                               *(['--check-inputs'] if check_inputs else [])], cwd=SKILL,
                              capture_output=True, text=True, check=False)

    def test_current_inputs_enable_reuse_without_scientific_pass(self) -> None:
        before = self.source.read_bytes()
        result = self.run_graph()
        report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report['structure_status'], 'PASS')
        self.assertEqual(report['reuse_status'], 'PASS')
        self.assertEqual(report['scientific_status'], 'UNKNOWN')
        self.assertEqual(report['manual_review'], 'MANUAL_REQUIRED')
        self.assertEqual(self.source.read_bytes(), before)

    def test_hash_metadata_without_file_read_cannot_enable_reuse(self) -> None:
        result = self.run_graph(check_inputs=False)
        self.assertEqual(json.loads(result.stdout)['reuse_status'], 'UNKNOWN')

    def test_changed_manuscript_prevents_reusing_previously_valid_graph(self) -> None:
        self.assertEqual(self.run_graph().returncode, 0)
        self.source.write_text('changed input', encoding='utf-8')
        result = self.run_graph()
        report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report['structure_status'], 'PASS')
        self.assertEqual(report['reuse_status'], 'FAIL')
        self.assertEqual(report['input_checks'][0]['status'], 'STALE')
        self.assertEqual(self.source.read_text(), 'changed input')

    def test_missing_source_blocks_reuse(self) -> None:
        self.source.unlink()
        result = self.run_graph()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)['input_checks'][0]['status'], 'UNREADABLE')
        self.assertFalse(self.source.exists())

    def test_absolute_input_path_is_supported_read_only(self) -> None:
        self.graph['inputs'][0]['path'] = str(self.source)
        result = self.run_graph()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_invalid_fields_fail_structure(self) -> None:
        cases = [
            ('duplicate id', lambda g: g['nodes'][1].update(id='n0')),
            ('invalid id', lambda g: g['nodes'][0].update(id='not an ID')),
            ('dangling node', lambda g: g['edges'][0].update(target='absent')),
            ('dangling input', lambda g: g['nodes'][0]['origins'][0].update(input_id='absent')),
            ('edge kind', lambda g: g['edges'][0].update(kind='proves')),
            ('node kind', lambda g: g['nodes'][0].update(kind='invalid')),
            ('hash', lambda g: g['inputs'][0].update(sha256='fake')),
            ('support', lambda g: g['nodes'][0].update(support_state='proven')),
            ('provenance', lambda g: g['nodes'][0]['provenance'].update(kind='verified')),
            ('required', lambda g: g['nodes'][0].pop('scope')),
            ('type', lambda g: g['nodes'][0]['verification_scope'].update(performed='yes')),
            ('extra field', lambda g: g.update(score=100)),
            ('empty scope', lambda g: g['analysis_scope'].update(included=[])),
            ('boolean version', lambda g: g.update(schema_version=True)),
            ('independent artifact', lambda g: g['nodes'][6]['provenance'].update(artifacts=[])),
            ('independent run', lambda g: g['nodes'][6]['provenance'].update(run_locator='')),
            ('independent scope', lambda g: g['nodes'][6]['verification_scope'].update(performed=[])),
        ]
        for name, mutate in cases:
            with self.subTest(name=name):
                self.graph = json.loads((FIXTURES / 'mixed.json').read_text())
                mutate(self.graph)
                result = self.run_graph()
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertEqual(json.loads(result.stdout)['structure_status'], 'FAIL')

    def test_dependency_cycle_requires_manual_review_without_structural_failure(self) -> None:
        self.graph['edges'].append({'id': 'cycle', 'kind': 'derived_from', 'source': 'n0', 'target': 'n1'})
        result = self.run_graph()
        report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertTrue(any(item.startswith('DEPENDENCY_CYCLE:') for item in report['diagnostics']))
        self.assertEqual(report['scientific_status'], 'UNKNOWN')

    def test_empty_template_is_valid_but_not_reusable_analysis(self) -> None:
        self.graph = json.loads((SKILL / 'assets/argument-graph.json').read_text())
        result = self.run_graph()
        report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(report['structure_status'], 'PASS')
        self.assertEqual(report['reuse_status'], 'UNKNOWN')
        self.assertEqual(report['input_status'], 'UNKNOWN')
        self.assertEqual(self.graph['nodes'], [])

    def test_missing_project_root_blocks_hash_validation(self) -> None:
        self.run_graph()
        result = subprocess.run([sys.executable, str(SKILL / 'scripts/argument_graph.py'), 'validate',
                                 str(self.graph_path), '--project-root', str(self.root / 'absent'),
                                 '--check-inputs', '--json'], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)['reuse_status'], 'FAIL')

    def test_malformed_json_has_machine_readable_failure(self) -> None:
        self.graph_path.write_text('{"schema_version":1,"schema_version":1}', encoding='utf-8')
        result = subprocess.run([sys.executable, str(SKILL / 'scripts/argument_graph.py'), 'validate',
                                 str(self.graph_path), '--project-root', str(self.root), '--json'],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)['structure_status'], 'FAIL')

    def test_unknown_home_user_is_unreadable_without_traceback(self) -> None:
        self.graph['inputs'][0]['path'] = '~paper_craft_nonexistent_21e95a/source.txt'
        result = self.run_graph()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, '')
        report = json.loads(result.stdout)
        self.assertEqual(report['input_status'], 'FAIL')
        self.assertEqual(report['reuse_status'], 'FAIL')
        self.assertEqual(report['input_checks'][0]['status'], 'UNREADABLE')
        self.assertEqual(report['scientific_status'], 'UNKNOWN')

    def test_overlapping_verification_scopes_fail_structure(self) -> None:
        self.graph['nodes'][0]['verification_scope'] = {
            'performed': ['simulation'], 'unperformed': ['simulation']}
        result = self.run_graph()
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertEqual(report['structure_status'], 'FAIL')
        self.assertEqual(report['scientific_status'], 'UNKNOWN')

    def test_cli_help(self) -> None:
        result = subprocess.run([sys.executable, str(SKILL / 'scripts/argument_graph.py'), '--help'],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()
