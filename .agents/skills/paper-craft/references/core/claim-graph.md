# Claim and argument graph

Use a graph to preserve the reasoning of a review across sessions. Begin with the
[empty template](../../assets/argument-graph.json); its empty arrays deliberately
assert nothing about a paper. Store the populated graph in the user's selected
private review directory using the [output policy](../workflows/output-policy.md).
Do not add manuscript-derived graphs or absolute private paths to public examples.
The [schema](../../schemas/argument-graph.schema.json) defines version 1.

## Capture the argument

Set `schema_version` to `1`, record the `research_question`, and state the
`analysis_scope.included` and `.excluded` boundaries. Register every manuscript,
code file, result, and reproduction artifact actually consulted in `inputs` with
an immutable `id`, explicit local `path`, and current lowercase SHA-256 digest.
List all consulted files, including included manuscript sections; a graph cannot
notice changes to files omitted from its input inventory. Relative paths resolve
from the explicitly supplied project root, not from the graph or installed Skill.
Absolute paths are accepted for private external artifacts and are read-only.

Give every input, node, and edge a globally unique stable ID; retain IDs when
revising the same assertion rather than deriving them from mutable prose or line
numbers. Node `kind` is `claim`, `assumption`, `evidence`, `alternative`, or
`qualification`. Every node has:

- `text`, `origins` (one or more `{input_id, locator}` references to the original
  passage, equation, figure, table, or result), and its applicable `scope`.
- `support_state`: `directly_verified`, `partially_verified`,
  `indirectly_supported`, `needs_validation`, `unsupported`, or `cannot_determine`.
- `provenance`: `kind`, `artifacts` (input/locator references), and `run_locator`.
- `verification_scope`: separate arrays of `performed` and `unperformed` checks;
  the same check identifier cannot occur in both arrays (enforced by the CLI).
- `unresolved_questions` and `next_action`; an empty action means none recorded,
  not that no action is needed.

The graph's research question applies to its nodes. State subquestions in node
text or unresolved questions. Do not silently expand a claim's scope or erase an
assumption when an edit makes the prose more concise.

Edges have `id`, `kind`, `source`, and `target`. Directions are explicit:

| Kind | Read the edge as |
| --- | --- |
| `requires` | Source depends on target assumption, claim, or prerequisite. |
| `supports` | Source supplies support for target. |
| `contradicts` | Source supplies counterevidence against target. |
| `alternative_to` | Source is an alternative explanation or design for target. |
| `qualifies` | Source limits or conditions target. |
| `derived_from` | Source is derived from target. |

These relations expose assumptions, dependencies, supportive and contradictory
evidence, alternatives, and qualifications without redundant node ID lists.
A `requires`/`derived_from` cycle triggers manual inspection; it can reflect a
reasoning problem or an intentional mutual dependency and is not by itself a
scientific error. Whether node types and edge directions make scientific sense
requires human review; the validator checks references and recognized types.

## Separate provenance from support

Provenance kinds are `manuscript_reported`, `mathematical_check`, `source_code`,
`numerical_reproduction`, `simulation`, `hardware_measurement`,
`independently_reproduced`, `hypothesis`, `inference`, and `unknown`.
A manuscript reporting measurements is still `manuscript_reported` when only its
prose was inspected. Use separate evidence nodes for mixed provenance. Reading a
source file does not execute it; checking a formula does not reproduce a hardware
experiment. Keep what was checked and what remains unchecked explicit.

`independently_reproduced` structurally requires at least one artifact reference,
a nonblank run locator, and performed verification scope. Those fields are
self-reported metadata, not proof of independent execution. Even matching file
hashes do not authenticate an artifact or establish independence. Inspect the
actual run, environment, artifact, and scope before making that judgment.

## Validate before reuse

```sh
python3 "$SKILL_DIR/scripts/argument_graph.py" validate "$REVIEW_DIR/argument-graph.json" \
  --project-root "$PROJECT_ROOT" --check-inputs --json
```

The CLI only reads local files and prints a report. It never writes manuscripts,
executes artifact commands, uploads files, or fetches URLs. `--help` describes the
CLI. Exit `0` means requested mechanical checks passed; exit `1` means invalid
structure or failed input checks; argument usage errors exit `2`.

`structure_status: PASS` means recognized fields, types, IDs, references, and
provenance requirements. `scientific_status` always remains `UNKNOWN`, with
`manual_review: MANUAL_REQUIRED`. There are no truth, novelty, or acceptance scores.

Without `--check-inputs`, `input_status` and `reuse_status` remain `UNKNOWN`.
With it, each registered file is freshly hashed. Missing/unreadable files or
mismatched hashes produce `FAIL` and block reuse. A populated graph with all
matching inputs has `reuse_status: PASS` for the captured input bytes only;
review scope changes and scientific validity manually. An empty template never
qualifies as reusable analysis. Recheck immediately before reuse: matching bytes
at one invocation are not a guarantee about later edits. When files change,
revisit affected claims, evidence, and dependents before updating their hashes.
Never merely replace old hashes to disguise stale analysis.
