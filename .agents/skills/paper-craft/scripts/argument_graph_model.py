"""Parse argument graph version 1 into immutable, validated records (stdlib only)."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final, TypeAlias

JSONValue: TypeAlias = str | int | float | bool | None | list['JSONValue'] | dict[str, 'JSONValue']
NODE_KINDS: Final = ('claim', 'assumption', 'evidence', 'alternative', 'qualification')
EDGE_KINDS: Final = ('requires', 'supports', 'contradicts', 'alternative_to', 'qualifies', 'derived_from')
SUPPORT_STATES: Final = ('directly_verified', 'partially_verified', 'indirectly_supported',
                         'needs_validation', 'unsupported', 'cannot_determine')
PROVENANCE_KINDS: Final = ('manuscript_reported', 'mathematical_check', 'source_code',
                           'numerical_reproduction', 'simulation', 'hardware_measurement',
                           'independently_reproduced', 'hypothesis', 'inference', 'unknown')


class GraphError(ValueError):
    """Invalid graph input; its message locates the rejected field."""


def record(value: JSONValue, keys: str, location: str) -> dict[str, JSONValue]:
    if not isinstance(value, dict) or set(value) != set(keys.split()):
        raise GraphError(f'{location}: expected exactly fields {keys}')
    return value


def text(value: JSONValue, location: str, *, empty: bool = False) -> str:
    if not isinstance(value, str) or (not empty and not value.strip()):
        raise GraphError(f'{location}: expected {"possibly empty " if empty else "nonblank "}string')
    return value


def items(value: JSONValue, location: str) -> list[JSONValue]:
    if not isinstance(value, list):
        raise GraphError(f'{location}: expected array')
    return value


def texts(value: JSONValue, location: str) -> tuple[str, ...]:
    return tuple(text(item, location) for item in items(value, location))


def choice(value: JSONValue, allowed: tuple[str, ...], location: str) -> str:
    result = text(value, location)
    if result not in allowed:
        raise GraphError(f'{location}: unknown value {result!r}')
    return result


def identifier(value: JSONValue) -> str:
    result = text(value, 'id')
    if re.fullmatch(r'[A-Za-z][A-Za-z0-9_.:-]*', result) is None:
        raise GraphError(f'id: invalid identifier {result!r}')
    return result


@dataclass(frozen=True, slots=True)
class Input:
    id: str
    path: str
    sha256: str


@dataclass(frozen=True, slots=True)
class Locator:
    input_id: str
    locator: str


@dataclass(frozen=True, slots=True)
class Node:
    id: str
    kind: str
    text: str
    origins: tuple[Locator, ...]
    scope: tuple[str, ...]
    support_state: str
    provenance_kind: str
    artifacts: tuple[Locator, ...]
    run_locator: str
    performed: tuple[str, ...]
    unperformed: tuple[str, ...]
    unresolved_questions: tuple[str, ...]
    next_action: str


@dataclass(frozen=True, slots=True)
class Edge:
    id: str
    kind: str
    source: str
    target: str


@dataclass(frozen=True, slots=True)
class Graph:
    research_question: str
    included: tuple[str, ...]
    excluded: tuple[str, ...]
    inputs: tuple[Input, ...]
    nodes: tuple[Node, ...]
    edges: tuple[Edge, ...]


def locators(value: JSONValue) -> tuple[Locator, ...]:
    result: list[Locator] = []
    for raw in items(value, 'locators'):
        data = record(raw, 'input_id locator', 'locator')
        result.append(Locator(identifier(data['input_id']), text(data['locator'], 'locator')))
    return tuple(result)


def parse_node(raw: JSONValue) -> Node:
    data = record(raw, 'id kind text origins scope support_state provenance verification_scope '
                  'unresolved_questions next_action', 'node')
    provenance = record(data['provenance'], 'kind artifacts run_locator', 'provenance')
    verification = record(data['verification_scope'], 'performed unperformed', 'verification_scope')
    node = Node(identifier(data['id']), choice(data['kind'], NODE_KINDS, 'node.kind'),
                text(data['text'], 'node.text'), locators(data['origins']), texts(data['scope'], 'scope'),
                choice(data['support_state'], SUPPORT_STATES, 'support_state'),
                choice(provenance['kind'], PROVENANCE_KINDS, 'provenance.kind'),
                locators(provenance['artifacts']), text(provenance['run_locator'], 'run_locator', empty=True),
                texts(verification['performed'], 'performed'), texts(verification['unperformed'], 'unperformed'),
                texts(data['unresolved_questions'], 'unresolved_questions'),
                text(data['next_action'], 'next_action', empty=True))
    if set(node.performed) & set(node.unperformed):
        raise GraphError(f'{node.id}: performed and unperformed verification scopes must be disjoint')
    if not node.origins:
        raise GraphError(f'{node.id}: at least one original source locator required')
    if node.provenance_kind == 'independently_reproduced' and (
            not node.artifacts or not node.run_locator.strip() or not node.performed):
        raise GraphError(f'{node.id}: independent reproduction requires artifact, run locator, performed scope')
    return node


def parse_graph(raw: JSONValue) -> Graph:
    data = record(raw, 'schema_version research_question analysis_scope inputs nodes edges', 'graph')
    if type(data['schema_version']) is not int or data['schema_version'] != 1:
        raise GraphError('schema_version: expected integer 1')
    scope = record(data['analysis_scope'], 'included excluded', 'analysis_scope')
    inputs: list[Input] = []
    for raw_input in items(data['inputs'], 'inputs'):
        source = record(raw_input, 'id path sha256', 'input')
        digest = text(source['sha256'], 'sha256')
        if re.fullmatch(r'[0-9a-f]{64}', digest) is None:
            raise GraphError('sha256: expected 64 lowercase hexadecimal characters')
        inputs.append(Input(identifier(source['id']), text(source['path'], 'path'), digest))
    edges: list[Edge] = []
    for raw_edge in items(data['edges'], 'edges'):
        edge = record(raw_edge, 'id kind source target', 'edge')
        edges.append(Edge(identifier(edge['id']), choice(edge['kind'], EDGE_KINDS, 'edge.kind'),
                          identifier(edge['source']), identifier(edge['target'])))
    graph = Graph(text(data['research_question'], 'research_question', empty=True),
                  texts(scope['included'], 'included'), texts(scope['excluded'], 'excluded'), tuple(inputs),
                  tuple(parse_node(node) for node in items(data['nodes'], 'nodes')), tuple(edges))
    ids = [entry.id for entry in (*graph.inputs, *graph.nodes, *graph.edges)]
    if len(ids) != len(set(ids)):
        raise GraphError('id: identifiers must be globally unique')
    input_ids = {source.id for source in graph.inputs}
    node_ids = {node.id for node in graph.nodes}
    if graph.nodes and (not graph.research_question.strip() or not graph.included):
        raise GraphError('populated graph requires research_question and included analysis scope')
    for node in graph.nodes:
        if any(locator.input_id not in input_ids for locator in (*node.origins, *node.artifacts)):
            raise GraphError(f'{node.id}: dangling input locator')
    for edge in graph.edges:
        if edge.source not in node_ids or edge.target not in node_ids:
            raise GraphError(f'{edge.id}: dangling node reference')
    return graph
