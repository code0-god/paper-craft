#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
# How to run: python3 validate_review_report.py review.json --json
"""Read legacy/v1 and v2 reports; check structure and references, never scientific truth."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from argument_graph_model import GraphError, JSONValue, choice, identifier, items, parse_graph, text
from manuscript_common import InputError, read_text
from review_report_fields import (
    STATUSES,
    claim,
    digest,
    edits,
    fields,
    finding,
    strings,
    target,
    verification,
)


def validate_report(raw: JSONValue) -> int:
    """Reject malformed reports and dangling references without modifying artifacts."""
    required = 'task mode inputs findings checks limitations'
    optional = 'schema_version claims target'
    if not isinstance(raw, dict):
        raise GraphError('report: expected object')
    version = raw.get('schema_version', 1)
    if type(version) is not int or version not in (1, 2):
        raise GraphError('schema_version: expected integer 1 or 2')
    if version == 2:
        required += ' schema_version verification_scope'
        optional += ' argument_graph argument_graph_reference edits'
    data = fields(raw, required, optional)
    text(data['task'], 'task')
    choice(data['mode'], ('review_only', 'suggest_edits', 'apply_approved_edits'), 'mode')
    strings(data['limitations'], 'limitations')
    input_ids: set[str] = set()
    input_metadata: dict[str, tuple[str, JSONValue]] = {}
    inputs = items(data['inputs'], 'inputs')
    if not inputs:
        raise GraphError('inputs: expected at least one input')
    for raw_input in inputs:
        entry = fields(raw_input, 'path read_status' + (' id' if version == 2 else ''),
                       'sha256 notes', 'input')
        path = text(entry['path'], 'input.path')
        choice(entry['read_status'], ('read', 'partial', 'unreadable', 'missing'), 'read_status')
        if entry.get('sha256') is not None:
            digest(entry['sha256'], 'input.sha256')
        if 'notes' in entry:
            text(entry['notes'], 'input.notes', empty=True)
        if version == 2:
            key = identifier(entry['id'])
            if key in input_ids:
                raise GraphError('input.id: duplicate identifier')
            input_ids.add(key)
            input_metadata[key] = (path, entry.get('sha256'))
    findings = [finding(value, version, input_ids) for value in items(data['findings'], 'findings')]
    claims = [claim(value, version, input_ids) for value in items(data.get('claims', []), 'claims')]
    for raw_check in items(data['checks'], 'checks'):
        check = fields(raw_check, 'name status evidence limits', at='check')
        choice(check['status'], STATUSES, 'check.status')
        for name in ('name', 'evidence', 'limits'):
            text(check[name], 'check.' + name, empty=True)
    if 'target' in data:
        target(data['target'])
    if version == 2:
        verification(data['verification_scope'])
        references(data, claims, findings, input_ids, input_metadata)
    return version


def references(data: dict[str, JSONValue], claims: list[dict[str, JSONValue]],
               findings: list[dict[str, JSONValue]], input_ids: set[str],
               input_metadata: dict[str, tuple[str, JSONValue]]) -> None:
    """Bind stable claim IDs and metadata; actual source freshness is a separate check."""
    claim_states = {identifier(item['id']): item['evidence_state'] for item in claims}
    ids = [identifier(item['id']) for item in (*claims, *findings)] + list(input_ids)
    claim_ids = set(claim_states)
    if 'argument_graph' in data and 'argument_graph_reference' in data:
        raise GraphError('choose an inline argument_graph or an argument_graph_reference')
    if 'argument_graph' in data:
        graph = parse_graph(data['argument_graph'])
        for source in graph.inputs:
            if input_metadata.get(source.id) != (source.path, source.sha256):
                raise GraphError('argument_graph: input metadata differs from report inputs')
        for node in graph.nodes:
            if node.kind == 'claim':
                claim_ids.add(node.id)
                if node.id in claim_states and claim_states[node.id] != node.support_state:
                    raise GraphError('argument_graph: claim evidence state differs from report')
    if 'argument_graph_reference' in data:
        reference = fields(data['argument_graph_reference'], 'path sha256 claim_ids', at='argument_graph_reference')
        text(reference['path'], 'argument_graph_reference.path')
        digest(reference['sha256'], 'argument_graph_reference.sha256')
        external_ids = [identifier(item) for item in items(reference['claim_ids'], 'claim_ids')]
        if len(external_ids) != len(set(external_ids)):
            raise GraphError('argument_graph_reference: duplicate claim identifiers')
        claim_ids.update(external_ids)
    for item in findings:
        if not set(strings(item['claim_ids'], 'claim_ids')) <= claim_ids:
            raise GraphError('finding.claim_ids: dangling claim reference')
    ids += edits(data.get('edits', []), claim_ids)
    if len(ids) != len(set(ids)):
        raise GraphError('id: duplicate report identifier')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('--json', action='store_true', help='JSON output (also default)')
    args = parser.parse_args()
    try:
        raw: JSONValue = json.loads(read_text(args.report))
        version = validate_report(raw)
    except InputError:
        print('Cannot read report input', file=sys.stderr)
        return 2
    except (json.JSONDecodeError, GraphError) as exc:
        # Do not echo raw values, user paths or report content in public diagnostics.
        reason = 'Malformed JSON' if isinstance(exc, json.JSONDecodeError) else str(exc).split(':')[0]
        print(json.dumps({'tool': 'validate_review_report', 'structure_status': 'FAIL',
                          'scientific_status': 'UNKNOWN', 'semantic_review': 'MANUAL_REQUIRED',
                          'error_field': reason, 'limits': 'Structure and metadata checks only'}))
        return 1
    print(json.dumps({'tool': 'validate_review_report', 'schema_version': version,
                      'structure_status': 'PASS', 'scientific_status': 'UNKNOWN',
                      'semantic_review': 'MANUAL_REQUIRED', 'graph_reuse_status': 'UNKNOWN',
                      'limits': 'Metadata and references only; external graph contents and current input hashes '
                                'require argument_graph.py validate --check-inputs; evidence truth requires review'}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
