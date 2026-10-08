"""Field checks for the two review-report contracts; not a JSON Schema engine."""
from __future__ import annotations

import re
from typing import Final

from argument_graph_model import (
    PROVENANCE_KINDS,
    SUPPORT_STATES,
    GraphError,
    JSONValue,
    choice,
    identifier,
    items,
    locators,
    text,
)

STATUSES: Final = ('PASS', 'FAIL', 'SKIPPED', 'UNKNOWN')
EDIT_CATEGORIES: Final = ('language_only', 'structural', 'claim_qualification',
                          'technical_correction', 'evidence_alignment')


def fields(value: JSONValue, required: str, optional: str = '', at: str = 'report') -> dict[str, JSONValue]:
    """Check required/unknown fields before their concrete values are parsed."""
    if not isinstance(value, dict):
        raise GraphError(f'{at}: expected object')
    missing = set(required.split()) - set(value)
    extra = set(value) - set((required + ' ' + optional).split())
    if missing or extra:
        raise GraphError(f'{at}: missing fields {sorted(missing)}; unknown fields {sorted(extra)}')
    return value


def strings(value: JSONValue, at: str) -> list[str]:
    return [text(item, at, empty=True) for item in items(value, at)]


def digest(value: JSONValue, at: str) -> str:
    result = text(value, at)
    if re.fullmatch(r'[a-f0-9]{64}', result) is None:
        raise GraphError(f'{at}: expected 64 lowercase hexadecimal characters')
    return result


def verification(value: JSONValue) -> None:
    data = fields(value, 'performed unperformed', at='verification_scope')
    performed = strings(data['performed'], 'performed')
    unperformed = strings(data['unperformed'], 'unperformed')
    if set(performed) & set(unperformed):
        raise GraphError('verification_scope: performed and unperformed must be disjoint')


def locator_references(value: JSONValue, input_ids: set[str]) -> None:
    for locator in locators(value):
        if locator.input_id not in input_ids:
            raise GraphError('locator: dangling input_id')


def scientific_fields(data: dict[str, JSONValue], input_ids: set[str]) -> None:
    """Check metadata structure independently of scientific validity."""
    verification(data['verification_scope'])
    provenance = fields(data['provenance'], 'kind artifacts run_locator', at='provenance')
    kind = choice(provenance['kind'], PROVENANCE_KINDS, 'provenance.kind')
    locator_references(provenance['artifacts'], input_ids)
    run = text(provenance['run_locator'], 'run_locator', empty=True)
    scope = fields(data['verification_scope'], 'performed unperformed', at='verification_scope')
    if kind == 'independently_reproduced' and (
            not provenance['artifacts'] or not run.strip() or not scope['performed']):
        raise GraphError('independent reproduction requires artifacts, run_locator and performed scope')
    axes = fields(data['evidence_axes'], 'existence validity inference', at='evidence_axes')
    for name, raw in axes.items():
        axis = fields(raw, 'status rationale locators', at=name)
        choice(axis['status'], STATUSES, name + '.status')
        text(axis['rationale'], name + '.rationale')
        locator_references(axis['locators'], input_ids)


def finding(raw: JSONValue, version: int, input_ids: set[str]) -> dict[str, JSONValue]:
    required = 'id location category severity evidence explanation recommendation evidence_state'
    optional = 'additional_material proposed_revision technical_meaning_risk'
    if version == 2:
        required += ' claim_ids provenance verification_scope evidence_axes'
        optional += ' current_state'
    data = fields(raw, required, optional, 'finding')
    for name in ('id', 'location', 'category', 'explanation', 'recommendation'):
        text(data[name], 'finding.' + name)
    choice(data['severity'], ('Critical', 'Major', 'Minor', 'Suggestion'), 'severity')
    choice(data['evidence_state'], SUPPORT_STATES, 'evidence_state')
    strings(data['evidence'], 'evidence')
    if 'additional_material' in data:
        strings(data['additional_material'], 'additional_material')
    for name in ('proposed_revision', 'technical_meaning_risk'):
        if name in data and data[name] is not None:
            text(data[name], name, empty=True)
    if version == 2:
        scientific_fields(data, input_ids)
        strings(data['claim_ids'], 'claim_ids')
        if 'current_state' in data:
            choice(data['current_state'], ('open', 'resolved', 'disputed', 'deferred'), 'current_state')
    return data


def claim(raw: JSONValue, version: int, input_ids: set[str]) -> dict[str, JSONValue]:
    required = 'id text location evidence_locations evidence_state notes'
    if version == 2:
        required += ' provenance verification_scope evidence_axes'
    data = fields(raw, required, at='claim')
    for name in ('id', 'text', 'location', 'notes'):
        text(data[name], 'claim.' + name, empty=True)
    strings(data['evidence_locations'], 'evidence_locations')
    choice(data['evidence_state'], SUPPORT_STATES, 'evidence_state')
    if version == 2:
        scientific_fields(data, input_ids)
    return data


def target(raw: JSONValue) -> None:
    if raw is None:
        return
    data = fields(raw, 'venue_id year track stage verification_status', 'profile_path', 'target')
    for name in ('venue_id', 'track', 'stage'):
        text(data[name], name, empty=True)
    if data['year'] is not None and type(data['year']) is not int:
        raise GraphError('target.year: expected integer or null')
    if 'profile_path' in data and data['profile_path'] is not None:
        text(data['profile_path'], 'profile_path', empty=True)
    choice(data['verification_status'], ('verified', 'unverified', 'outdated', 'conflicting'),
           'verification_status')


def edits(raw: JSONValue, claim_ids: set[str]) -> list[str]:
    ids: list[str] = []
    for value in items(raw, 'edits'):
        data = fields(value, 'id categories claim_ids evidence assumptions scope_impact', at='edit')
        ids.append(identifier(data['id']))
        categories = [choice(item, EDIT_CATEGORIES, 'categories') for item in items(data['categories'], 'categories')]
        if not categories or len(categories) != len(set(categories)):
            raise GraphError('categories: expected one or more unique edit categories')
        if not set(strings(data['claim_ids'], 'claim_ids')) <= claim_ids:
            raise GraphError('edit.claim_ids: dangling claim reference')
        strings(data['evidence'], 'evidence')
        strings(data['assumptions'], 'assumptions')
        text(data['scope_impact'], 'scope_impact')
    return ids
