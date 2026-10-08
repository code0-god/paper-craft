#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
# Run: python3 argument_graph.py validate GRAPH --project-root ROOT --check-inputs --json
"""Validate argument graph structure and current local hashes; never grade scientific truth."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import TypedDict

from argument_graph_model import Graph, GraphError, JSONValue, parse_graph


class InputCheck(TypedDict):
    input_id: str
    status: str
    expected_sha256: str
    actual_sha256: str | None


class ValidationReport(TypedDict):
    tool: str
    status: str
    structure_status: str
    input_status: str
    reuse_status: str
    scientific_status: str
    manual_review: str
    diagnostics: list[str]
    input_checks: list[InputCheck]
    limits: list[str]


def dependency_cycles(graph: Graph) -> bool:
    """Detect cycles iteratively; dependency cycles need interpretation, not rejection."""
    adjacency: dict[str, list[str]] = {node.id: [] for node in graph.nodes}
    indegrees = dict.fromkeys(adjacency, 0)
    for edge in graph.edges:
        if edge.kind in {'requires', 'derived_from'}:
            adjacency[edge.source].append(edge.target)
            indegrees[edge.target] += 1
    ready = [node for node, count in indegrees.items() if count == 0]
    visited = 0
    while ready:
        current = ready.pop()
        visited += 1
        for target in adjacency[current]:
            indegrees[target] -= 1
            if indegrees[target] == 0:
                ready.append(target)
    return visited != len(adjacency)


def unique_fields(pairs: list[tuple[str, JSONValue]]) -> dict[str, JSONValue]:
    """Reject duplicate JSON keys instead of silently keeping a later assertion."""
    result: dict[str, JSONValue] = {}
    for key, value in pairs:
        if key in result:
            raise GraphError(f'duplicate JSON key: {key}')
        result[key] = value
    return result


def validate(graph_path: Path, project_root: Path, check_inputs: bool = False) -> ValidationReport:
    report: ValidationReport = {
        'tool': 'argument_graph', 'status': 'PASS', 'structure_status': 'PASS',
        'input_status': 'UNKNOWN', 'reuse_status': 'UNKNOWN', 'scientific_status': 'UNKNOWN',
        'manual_review': 'MANUAL_REQUIRED', 'diagnostics': [], 'input_checks': [],
        'limits': ['PASS concerns structure and declared provenance only, never scientific truth.',
                   'Hashes show byte identity at this invocation, not authenticity or independence.',
                   'Locators, run descriptions, scientific support, and scope coverage require manual review.',
                   'No commands, simulations, experiments, or network requests are executed.']}
    try:
        raw: JSONValue = json.loads(graph_path.read_text(encoding='utf-8'), object_pairs_hook=unique_fields)
        graph = parse_graph(raw)
    except (OSError, UnicodeError, ValueError, RecursionError) as error:
        report.update(status='FAIL', structure_status='FAIL')
        report['diagnostics'].append(str(error))
        return report
    if dependency_cycles(graph):
        report['diagnostics'].append('DEPENDENCY_CYCLE: requires/derived_from cycle needs manual interpretation')
    if not graph.nodes:
        report['diagnostics'].append('EMPTY_GRAPH: template contains no scientific assertions')
    if not check_inputs:
        report['diagnostics'].append('INPUTS_UNCHECKED: run --check-inputs before reusing this graph')
        return report
    if not project_root.is_dir():
        report.update(status='FAIL', input_status='FAIL', reuse_status='FAIL')
        report['diagnostics'].append('PROJECT_ROOT_MISSING: project root must be an existing directory')
        return report
    for source in graph.inputs:
        digest = None
        try:
            path = Path(source.path).expanduser()
            if not path.is_absolute():
                path = project_root / path
            with path.open('rb') as stream:
                hasher = hashlib.sha256()
                for block in iter(lambda: stream.read(1024 * 1024), b''):
                    hasher.update(block)
                digest = hasher.hexdigest()
            status = 'PASS' if digest == source.sha256 else 'STALE'
        except (OSError, ValueError, RuntimeError):
            status = 'UNREADABLE'
        report['input_checks'].append({'input_id': source.id, 'status': status,
                                       'expected_sha256': source.sha256, 'actual_sha256': digest})
        if status != 'PASS':
            report['diagnostics'].append(f'{source.id}: {status}; cached analysis must not be reused')
    if any(check['status'] != 'PASS' for check in report['input_checks']):
        report.update(status='FAIL', input_status='FAIL', reuse_status='FAIL')
    elif graph.inputs:
        report['input_status'] = 'PASS'
        if graph.nodes:
            report['reuse_status'] = 'PASS'
    else:
        report['diagnostics'].append('NO_INPUTS: nothing was read or hash-verified')
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    command = commands.add_parser('validate', help='Read-only structural and optional input-hash validation')
    command.add_argument('graph', type=Path)
    command.add_argument('--project-root', type=Path, required=True,
                         help='Resolve relative input paths here, never against the Skill installation')
    command.add_argument('--check-inputs', action='store_true')
    command.add_argument('--json', action='store_true', help='Emit machine-readable validation result')
    args = parser.parse_args()
    report = validate(args.graph, args.project_root, args.check_inputs)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"argument_graph: {report['status']} (structure={report['structure_status']}, "
              f"inputs={report['input_status']}, scientific=UNKNOWN, MANUAL_REQUIRED)")
        for diagnostic in report['diagnostics']:
            print(diagnostic)
    return int(report['status'] == 'FAIL')


if __name__ == '__main__':
    raise SystemExit(main())
