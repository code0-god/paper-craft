#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
# How to run: python3 validate_writing_patterns.py [atlas.json] --json
"""Check writing-atlas provenance structure offline, never scientific or venue truth."""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Final, TypedDict
from urllib.parse import urlsplit

from argument_graph_model import GraphError, JSONValue, choice, identifier, items, record, text, texts
from venue_common import ProfileError, read_json

DEFAULT: Final = Path(__file__).resolve().parents[1] / 'venues/writing-patterns.json'
CATEGORIES: Final = ('official_requirement', 'official_recommendation', 'observed_pattern',
                     'independent_guidance')


class Finding(TypedDict):
    check: str
    status: str
    severity: str
    file: str
    line: None
    message: str


class Report(TypedDict):
    tool: str
    status: str
    scientific_validity: str
    current_rule_applicability: str
    findings: list[Finding]


@dataclass(frozen=True, slots=True)
class Paper:
    venue: str
    read_status: str
    locators: tuple[tuple[int, str, str], ...]
    page_count: int


def integer(value: JSONValue, at: str, minimum: int = 1) -> int:
    if type(value) is not int or value < minimum:
        raise GraphError(f'{at}: expected integer >= {minimum}')
    return value


def https_url(value: JSONValue) -> str:
    result = text(value, 'url')
    try:
        url = urlsplit(result)
        valid = (url.scheme == 'https' and bool(url.hostname) and bool(url.path)
                 and not url.username and not url.password and url.port in (None, 443)
                 and not any(character.isspace() for character in result))
    except ValueError as error:
        raise GraphError(f'url: {error}') from error
    if not valid:
        raise GraphError('url: expected public HTTPS URL without credentials')
    return result


def checked_date(value: JSONValue) -> str:
    result = text(value, 'date')
    try:
        parsed = date.fromisoformat(result)
    except ValueError as error:
        raise GraphError(f'date: {error}') from error
    if parsed.isoformat() != result or parsed > date.today():
        raise GraphError('date: expected ISO date no later than today')
    return result


def locators(value: JSONValue, page_count: int) -> tuple[tuple[int, str, str], ...]:
    result: list[tuple[int, str, str]] = []
    for raw in items(value, 'locators'):
        data = record(raw, 'pdf_page section detail', 'locator')
        page = integer(data['pdf_page'], 'pdf_page')
        if page > page_count:
            raise GraphError('locator: pdf_page exceeds page_count')
        result.append((page, text(data['section'], 'section'), text(data['detail'], 'detail')))
    if len(set(result)) != len(result):
        raise GraphError('locators: duplicate entry')
    return tuple(result)


def paper(raw: JSONValue) -> tuple[str, Paper]:
    data = record(raw, 'id title venue_id year publication_url paper_url doi exact_revision '
                  'pdf_sha256 page_count read_coverage notes', 'paper')
    key = identifier(data['id'])
    for name in ('title', 'venue_id', 'doi', 'exact_revision', 'notes'):
        text(data[name], name)
    year = integer(data['year'], 'year', 1900)
    if year > date.today().year:
        raise GraphError('paper.year: future publication year')
    for name in ('publication_url', 'paper_url'):
        https_url(data[name])
    if not re.fullmatch(r'10\.\d{4,9}/\S+', text(data['doi'], 'doi')):
        raise GraphError('doi: expected DOI identifier')
    if not re.fullmatch(r'[a-f0-9]{64}', text(data['pdf_sha256'], 'pdf_sha256')):
        raise GraphError('pdf_sha256: expected 64 lowercase hex characters')
    pages = integer(data['page_count'], 'page_count')
    coverage = record(data['read_coverage'], 'status read_at method locators unread_scope limitations',
                      'read_coverage')
    status = choice(coverage['status'], ('read', 'partial', 'unread'), 'read_coverage.status')
    for name in ('method', 'unread_scope', 'limitations'):
        text(coverage[name], name)
    locations = locators(coverage['locators'], pages)
    if status == 'unread':
        if locations or coverage['read_at'] is not None:
            raise GraphError('unread paper cannot have read locators/date')
    else:
        checked_date(coverage['read_at'])
        if not locations:
            raise GraphError('read/partial paper requires read locators')
    return key, Paper(text(data['venue_id'], 'venue_id'), status, locations, pages)


def validate(raw: JSONValue) -> None:
    """Reject missing metadata and inconsistent source links; do not judge prose truth."""
    data = record(raw, 'atlas_version reviewed_at selection_scope venues papers observations', 'atlas')
    if type(data['atlas_version']) is not int or data['atlas_version'] != 1:
        raise GraphError('atlas_version: expected 1')
    checked_date(data['reviewed_at'])
    text(data['selection_scope'], 'selection_scope')
    papers: dict[str, Paper] = {}
    for raw_paper in items(data['papers'], 'papers'):
        key, entry = paper(raw_paper)
        if key in papers:
            raise GraphError('paper: duplicate id')
        papers[key] = entry
    venues: set[str] = set()
    for raw_venue in items(data['venues'], 'venues'):
        venue = record(raw_venue, 'venue_id sampling_status paper_ids sample_size scope_limit', 'venue')
        key = text(venue['venue_id'], 'venue_id')
        if key in venues:
            raise GraphError('venue: duplicate id')
        venues.add(key)
        status = choice(venue['sampling_status'], ('sampled', 'unsampled'), 'sampling_status')
        ids = texts(venue['paper_ids'], 'paper_ids')
        count = integer(venue['sample_size'], 'sample_size', 0)
        text(venue['scope_limit'], 'scope_limit')
        expected = {paper_id for paper_id, entry in papers.items() if entry.venue == key}
        if len(ids) != len(set(ids)) or set(ids) != expected or count != len(ids):
            raise GraphError('venue: paper_ids/sample_size must match its papers exactly')
        if (status == 'sampled') != bool(ids):
            raise GraphError('venue: sampling_status contradicts paper_ids')
    if any(entry.venue not in venues for entry in papers.values()):
        raise GraphError('paper: unknown venue_id')
    seen: set[str] = set()
    for raw_observation in items(data['observations'], 'observations'):
        observation = record(raw_observation, 'id venue_id paper_id category observation scope_limit '
                             'generalization verification_status locators', 'observation')
        key = identifier(observation['id'])
        if key in seen:
            raise GraphError('observation: duplicate id')
        seen.add(key)
        category = choice(observation['category'], CATEGORIES, 'category')
        if category in ('official_requirement', 'official_recommendation'):
            raise GraphError('official classification unsupported by paper evidence; use exact venue profiles')
        paper_id = text(observation['paper_id'], 'paper_id')
        source = papers.get(paper_id)
        if source is None:
            raise GraphError('observation: unknown paper_id')
        if observation['venue_id'] != source.venue:
            raise GraphError('observation: venue_id differs from paper')
        for name in ('observation', 'scope_limit'):
            text(observation[name], name)
        choice(observation['generalization'], ('sample_only',), 'generalization')
        status = choice(observation['verification_status'], ('verified', 'unverified'), 'verification_status')
        locations = locators(observation['locators'], source.page_count)
        if not locations:
            raise GraphError('observation: requires at least one locator')
        if status == 'verified' and (source.read_status == 'unread' or
                                     not set(locations).issubset(source.locators)):
            raise GraphError('verified observation requires paper read coverage for every locator')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', nargs='?', type=Path, default=DEFAULT)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    status, message = 'PASS', 'Atlas structure and recorded provenance consistent; sources not re-read by validator.'
    try:
        validate(read_json(args.path))
    except (GraphError, ProfileError) as error:
        status, message = 'FAIL', str(error)
    report: Report = {'tool': 'validate_writing_patterns', 'status': status,
                      'scientific_validity': 'UNKNOWN', 'current_rule_applicability': 'UNKNOWN',
                      'findings': [{'check': 'atlas_structure_and_provenance', 'status': status,
                                    'severity': 'Major' if status == 'FAIL' else 'Suggestion',
                                    'file': str(args.path), 'line': None, 'message': message}]}
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else f'{status}: {message}')
    return int(status == 'FAIL')


if __name__ == '__main__':
    raise SystemExit(main())
